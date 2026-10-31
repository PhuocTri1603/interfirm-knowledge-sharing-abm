"""Game 1 sensitivity analysis: matched random and guided policies.

One-factor-at-a-time sweeps, including baseline 0.20/0.10.
All scenarios use the same seed-level common random schedules.
"""

import argparse
import json
from pathlib import Path

import pandas as pd

from interfirm_abm.simulation import Simulation

SCENARIOS = [
    ("baseline", 0.20, 0.10),
    ("explore_05", 0.05, 0.10),
    ("explore_10", 0.10, 0.10),
    ("explore_40", 0.40, 0.10),
    ("explore_60", 0.60, 0.10),
    ("radius_03", 0.20, 0.03),
    ("radius_05", 0.20, 0.05),
    ("radius_20", 0.20, 0.20),
    ("radius_30", 0.20, 0.30),
]
CHECKPOINTS = (5, 10, 20, 50, 100)


def run_experiment(n_seeds=100):
    rows = []
    for seed in range(2026, 2026 + n_seeds):
        for scenario, exploration, radius in SCENARIOS:
            for policy in ("random", "guided"):
                sim = Simulation(
                    n_firms=20,
                    n_rounds=100,
                    seed=seed,
                    learning_policy=policy,
                    matched_randomness=True,
                    exploration_probability=exploration,
                    search_radius=radius,
                )
                history = sim.run()
                snapshots = history[history["round"].isin(CHECKPOINTS)]
                for record in snapshots.itertuples(index=False):
                    rows.append({
                        "seed": seed,
                        "scenario": scenario,
                        "exploration_probability": exploration,
                        "search_radius": radius,
                        "policy": policy,
                        "round": record.round,
                        "firm_id": record.firm_id,
                        "technology": record.technology,
                        "output": record.current_output,
                    })
    return pd.DataFrame(rows)


def export_results(results, folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    paired = results.pivot(
        index=["seed", "scenario", "exploration_probability",
               "search_radius", "round", "firm_id", "technology"],
        columns="policy",
        values="output",
    ).reset_index()
    paired["advantage_pct"] = 100 * (
        paired["guided"] - paired["random"]
    ) / paired["random"]
    paired.to_csv(folder / "paired_sensitivity.csv", index=False)
    seed_means = paired.groupby(
        ["scenario", "exploration_probability", "search_radius",
         "seed", "round"], as_index=False
    ).agg(mean_advantage_pct=("advantage_pct", "mean"))
    seed_means.to_csv(folder / "seed_sensitivity.csv", index=False)
    summary = seed_means.groupby(
        ["scenario", "exploration_probability", "search_radius", "round"],
        as_index=False,
    ).agg(
        mean_advantage_pct=("mean_advantage_pct", "mean"),
        sd_seed_means=("mean_advantage_pct", "std"),
        positive_seed_fraction=("mean_advantage_pct", lambda x: (x > 0).mean()),
    )
    summary.to_csv(folder / "summary_sensitivity.csv", index=False)
    metadata = {
        "experiment": "game1_sensitivity",
        "seed_start": 2026,
        "seed_count": results["seed"].nunique(),
        "scenarios": SCENARIOS,
        "checkpoints": CHECKPOINTS,
        "n_firms": 20,
        "n_rounds": 100,
        "matched_randomness": True,
        "paired_rows": len(paired),
        "note": "Parameter sweeps are model robustness checks, not independent empirical evidence.",
    }
    (folder / "metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    return paired


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--export-dir", type=Path, required=True)
    parser.add_argument("--seeds", type=int, default=100)
    args = parser.parse_args()
    if args.seeds < 1:
        parser.error("--seeds must be positive")
    results = run_experiment(args.seeds)
    paired = export_results(results, args.export_dir)
    assert len(paired) == args.seeds * len(SCENARIOS) * 20 * len(CHECKPOINTS)
    assert paired["advantage_pct"].notna().all()
    print("Sensitivity matched pairs:", len(paired))

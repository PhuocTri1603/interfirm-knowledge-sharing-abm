"""
Validation 05: Matched Learning Policy Comparison.

Compare Random and Experience-Guided Exploration
using common random numbers across 100 seeds.
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from interfirm_abm.simulation import Simulation


N_REPLICATIONS = 100
CHECKPOINTS = [5, 10, 20, 50]
POLICIES = ["random", "guided"]


def run_experiment(n_firms=100, n_replications=N_REPLICATIONS, n_rounds=50):
    if n_rounds < max(CHECKPOINTS):
        raise ValueError('n_rounds must be at least 50 for the established checkpoints')
    records = []

    for seed in range(2026, 2026 + n_replications):
        for policy in POLICIES:
            sim = Simulation(
                n_firms=n_firms,
                n_rounds=n_rounds,
                seed=seed,
                learning_policy=policy,
                matched_randomness=True,
            )

            history = sim.run()

            snapshot = history[
                history["round"].isin(CHECKPOINTS)
            ]

            for row in snapshot.itertuples(index=False):
                records.append({
                    "seed": seed,
                    "policy": policy,
                    "round": row.round,
                    "firm_id": row.firm_id,
                    "technology": row.technology,
                    "output": row.current_output,
                })

    results = pd.DataFrame(records)

    paired = results.pivot(
        index=["seed", "round", "firm_id", "technology"],
        columns="policy",
        values="output",
    ).reset_index()

    paired["advantage_pct"] = (
        (paired["guided"] - paired["random"])
        / paired["random"] * 100
    )

    return paired


def export_results(paired, output_dir, n_firms=100, n_replications=N_REPLICATIONS, n_rounds=50):
    """Persist the exact matched observations and reproducibility metadata."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    paired.to_csv(output_dir / "paired_observations.csv", index=False)

    seed_round = (
        paired.groupby(["seed", "round"], as_index=False)
        .agg(mean_advantage_pct=("advantage_pct", "mean"))
    )
    seed_round.to_csv(output_dir / "seed_round_summary.csv", index=False)

    by_round = (
        seed_round.groupby("round", as_index=False)
        .agg(
            mean_advantage_pct=("mean_advantage_pct", "mean"),
            std_across_seeds=("mean_advantage_pct", "std"),
            guided_better_seed_pct=(
                "mean_advantage_pct",
                lambda x: 100 * (x > 0).mean(),
            ),
        )
    )
    by_round.to_json(
        output_dir / "summary_by_round.json",
        orient="records",
        indent=2,
    )

    metadata = {
        "experiment": "validation_05",
        "game": "Game 1",
        "n_replications": n_replications,
        "seed_start": 2026,
        "seed_end_inclusive": 2026 + n_replications - 1,
        "n_firms": n_firms,
        "n_rounds": n_rounds,
        "budget_per_firm": 100.0,
        "checkpoints": CHECKPOINTS,
        "policies": POLICIES,
        "matched_randomness": True,
        "expected_paired_rows": n_replications * n_firms * len(CHECKPOINTS),
        "observed_paired_rows": len(paired),
        "metric": "100 * (guided - random) / random",
        "numpy_version": np.__version__,
        "pandas_version": pd.__version__,
        "note": "Record the Git commit SHA separately with the run registry.",
    }
    (output_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Game 1 matched learning validation."
    )
    parser.add_argument(
        "--export-dir",
        type=Path,
        default=None,
        help="Write matched CSVs and JSON summaries to this directory.",
    )
    parser.add_argument("--firms", type=int, default=100)
    parser.add_argument("--seeds", type=int, default=N_REPLICATIONS)
    parser.add_argument("--rounds", type=int, choices=[50, 100, 200], default=50)
    args = parser.parse_args()
    if args.firms <= 0 or args.firms % 4:
        parser.error("--firms must be a positive multiple of four")
    if args.seeds <= 0:
        parser.error("--seeds must be positive")

    paired = run_experiment(n_firms=args.firms, n_replications=args.seeds, n_rounds=args.rounds)
    if args.export_dir is not None:
        export_results(paired, args.export_dir, n_firms=args.firms, n_replications=args.seeds, n_rounds=args.rounds)

    run_level = (
        paired.groupby(["seed", "round"])
        .agg(
            mean_advantage_pct=("advantage_pct", "mean")
        )
        .reset_index()
    )

    print("===== MATCHED COMPARISON BY ROUND =====")
    print(
        run_level.groupby("round")
        .agg(
            mean_advantage_pct=(
                "mean_advantage_pct", "mean"
            ),
            std_across_seeds=(
                "mean_advantage_pct", "std"
            ),
            guided_better_seed_pct=(
                "mean_advantage_pct",
                lambda x: 100 * (x > 0).mean()
            ),
        )
        .round(4)
        .to_string()
    )

    print("\n===== BY TECHNOLOGY AT ROUND 50 =====")
    print(
        paired[paired["round"] == 50]
        .groupby("technology")
        .agg(
            mean_advantage_pct=(
                "advantage_pct", "mean"
            ),
            guided_better_firm_pct=(
                "advantage_pct",
                lambda x: 100 * (x > 0).mean()
            ),
        )
        .round(4)
        .to_string()
    )

    print("\n===== EXPERIMENT SUMMARY =====")
    print("Seeds:", args.seeds)
    print("Paired observations:", len(paired))
    print("Matched randomness: True")

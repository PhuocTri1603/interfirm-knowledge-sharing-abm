"""Game 1 two-factor sensitivity: interaction between exploration and search radius.

A full 5x5 factorial design with matched policy random schedules.
The experiment exports seed-level means to support paired uncertainty estimates.
"""

import argparse
import json
from pathlib import Path

import pandas as pd

from interfirm_abm.simulation import Simulation

EXPLORATION_PROBABILITIES = (0.05, 0.10, 0.20, 0.40, 0.60)
SEARCH_RADII = (0.03, 0.05, 0.10, 0.20, 0.30)
CHECKPOINTS = (5, 10, 20, 50, 100)


def run_experiment(n_seeds=100):
    if not isinstance(n_seeds, int) or n_seeds < 1:
        raise ValueError("n_seeds must be a positive integer.")
    records = []
    for seed in range(2026, 2026 + n_seeds):
        # The random benchmark is identical for all configurations within a seed.
        random_history = Simulation(
            n_firms=20, n_rounds=100, seed=seed,
            learning_policy="random", matched_randomness=True,
        ).run()
        random_checkpoints = random_history[
            random_history["round"].isin(CHECKPOINTS)
        ].set_index(["round", "firm_id"])["current_output"]

        for probability in EXPLORATION_PROBABILITIES:
            for radius in SEARCH_RADII:
                guided_history = Simulation(
                    n_firms=20, n_rounds=100, seed=seed,
                    learning_policy="guided", matched_randomness=True,
                    exploration_probability=probability, search_radius=radius,
                ).run()
                for row in guided_history[
                    guided_history["round"].isin(CHECKPOINTS)
                ].itertuples(index=False):
                    random_output = float(random_checkpoints.loc[
                        (row.round, row.firm_id)
                    ])
                    records.append({
                        "seed": seed,
                        "exploration_probability": probability,
                        "search_radius": radius,
                        "round": row.round,
                        "firm_id": row.firm_id,
                        "technology": row.technology,
                        "guided_output": row.current_output,
                        "random_output": random_output,
                        "advantage_pct": 100 * (
                            row.current_output - random_output
                        ) / random_output,
                    })
    return pd.DataFrame.from_records(records)


def export_results(paired, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paired.to_csv(output_dir / "paired_factorial.csv", index=False)
    seed_means = paired.groupby(
        ["seed", "exploration_probability", "search_radius", "round"],
        as_index=False,
    ).agg(mean_advantage_pct=("advantage_pct", "mean"))
    seed_means.to_csv(output_dir / "seed_factorial.csv", index=False)
    summary = seed_means.groupby(
        ["exploration_probability", "search_radius", "round"],
        as_index=False,
    ).agg(
        mean_advantage_pct=("mean_advantage_pct", "mean"),
        sd_seed_means=("mean_advantage_pct", "std"),
        positive_seed_fraction=("mean_advantage_pct", lambda x: (x > 0).mean()),
    )
    summary.to_csv(output_dir / "summary_factorial.csv", index=False)

    # Interaction contrast at each checkpoint:
    # [Y(p_hi,r_hi)-Y(p_lo,r_hi)]-[Y(p_hi,r_lo)-Y(p_lo,r_lo)].
    # This measures nonadditivity of policy parameters within this model,
    # not a causal interaction identified from observational firm data.
    corners = seed_means[
        seed_means["exploration_probability"].isin((0.05, 0.60))
        & seed_means["search_radius"].isin((0.03, 0.30))
    ].pivot(
        index=["seed", "round"],
        columns=["exploration_probability", "search_radius"],
        values="mean_advantage_pct",
    )
    contrast = (
        corners[(0.60, 0.30)] - corners[(0.05, 0.30)]
        - corners[(0.60, 0.03)] + corners[(0.05, 0.03)]
    ).rename("interaction_contrast_pp").reset_index()
    contrast.to_csv(output_dir / "seed_interaction_contrast.csv", index=False)

    metadata = {
        "experiment": "game1_factorial_sensitivity",
        "seed_start": 2026,
        "seed_count": int(paired["seed"].nunique()),
        "n_firms": 20,
        "n_rounds": 100,
        "checkpoints": CHECKPOINTS,
        "exploration_probabilities": EXPLORATION_PROBABILITIES,
        "search_radii": SEARCH_RADII,
        "matched_randomness": True,
        "expected_paired_rows": int(paired["seed"].nunique()) * 25 * 20 * 5,
        "observed_paired_rows": len(paired),
    }
    (output_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    return seed_means


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--export-dir", type=Path, required=True)
    parser.add_argument("--seeds", type=int, default=100)
    args = parser.parse_args()
    paired = run_experiment(args.seeds)
    assert len(paired) == args.seeds * 25 * 20 * 5
    assert paired["advantage_pct"].notna().all()
    export_results(paired, args.export_dir)
    print("Matched factorial observations:", len(paired))

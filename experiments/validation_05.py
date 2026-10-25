"""
Validation 05: Matched Learning Policy Comparison.

Compare Random and Experience-Guided Exploration
using common random numbers across 100 seeds.
"""

import numpy as np
import pandas as pd

from interfirm_abm.simulation import Simulation


N_REPLICATIONS = 100
CHECKPOINTS = [5, 10, 20, 50]
POLICIES = ["random", "guided"]


def run_experiment():
    records = []

    for seed in range(2026, 2026 + N_REPLICATIONS):
        for policy in POLICIES:
            sim = Simulation(
                n_firms=20,
                n_rounds=50,
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


if __name__ == "__main__":
    paired = run_experiment()

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
    print("Seeds:", N_REPLICATIONS)
    print("Paired observations:", len(paired))
    print("Matched randomness: True")

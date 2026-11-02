"""Matched Game 2 comparison on the frozen heterogeneous Game 1 population.

The existing information_only and performance_triggered rules are compared
without adding market prices, profits, or new behavioral assumptions.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from interfirm_abm.competitive_simulation import CompetitiveSimulation
from interfirm_abm.production_optimum import optimal_output


POLICIES = ("information_only", "performance_triggered")


def run_experiment(rounds=100, seeds=100, population_seed=2026):
    if rounds < 3 or seeds < 1:
        raise ValueError("rounds >= 3 and seeds >= 1 required")
    rows, observation_rows = [], []
    for seed in range(2026, 2026 + seeds):
        for policy in POLICIES:
            sim = CompetitiveSimulation(
                n_firms=100, n_rounds=rounds, seed=seed,
                competitive_policy=policy, heterogeneous_population=True,
                population_seed=population_seed,
            )
            sim.run()
            for firm in sim.firms:
                optimum = optimal_output(
                    firm.technology, firm.budget, firm.alpha,
                    firm.rho, firm.productivity,
                )
                rows.append({
                    "population_seed": population_seed,
                    "learning_seed": seed,
                    "policy": policy,
                    "firm_id": firm.firm_id,
                    "technology": firm.technology,
                    "alpha": firm.alpha,
                    "stratum": str(sim.population.iloc[firm.firm_id - 1]["stratum"]),
                    "rounds": rounds,
                    "final_output": firm.current_output,
                    "efficiency_pct": 100 * firm.current_output / optimum,
                    "accepted": sum(x["accepted"] for x in firm.history),
                })
            for record in sim.observation_log:
                observation_rows.append({
                    "population_seed": population_seed,
                    "learning_seed": seed,
                    "policy": policy,
                    **record,
                })
    final = pd.DataFrame(rows)
    observations = pd.DataFrame(observation_rows)
    assert len(final) == seeds * 2 * 100
    assert len(observations) == seeds * 2 * 100 * rounds
    assert final.efficiency_pct.between(0, 100 + 1e-7).all()
    assert (observations.n_competitors == 99).all()
    assert (observations.observed_round == observations["round"] - 1).all()
    assert (observations.loc[observations.policy == "information_only",
                             "exploration_probability"] == 0.20).all()
    return final, observations


def summarize(final, observations):
    paired = final.pivot(
        index=["population_seed", "learning_seed", "firm_id", "technology",
               "stratum", "alpha"],
        columns="policy", values="efficiency_pct",
    ).reset_index()
    paired["triggered_minus_control_pp"] = (
        paired["performance_triggered"] - paired["information_only"]
    )
    by_seed_family = paired.groupby(
        ["population_seed", "learning_seed", "technology"], as_index=False
    )["triggered_minus_control_pp"].mean()
    by_family = by_seed_family.groupby("technology")[
        "triggered_minus_control_pp"
    ].agg(["mean", "std", "count"]).reset_index()
    by_family["seed_level_se_pp"] = by_family["std"] / np.sqrt(by_family["count"])
    treatment = observations.loc[
        observations.policy == "performance_triggered"
    ]
    activation = treatment.groupby("learning_seed").agg(
        triggered_share=("exploration_probability",
                         lambda x: float((x == 0.40).mean())),
        observed_growth_share=("own_growth_pct",
                               lambda x: float(x.notna().mean())),
    )
    result = {
        "population_seed": int(final.population_seed.iloc[0]),
        "learning_seeds": int(final.learning_seed.nunique()),
        "firms": 100,
        "rounds": int(final.rounds.iloc[0]),
        "comparison": "performance_triggered minus information_only",
        "overall_mean_efficiency_effect_pp": float(
            by_seed_family.groupby("learning_seed")[
                "triggered_minus_control_pp"
            ].mean().mean()
        ),
        "mean_trigger_activation_share": float(
            activation.triggered_share.mean()
        ),
        "mean_growth_signal_available_share": float(
            activation.observed_growth_share.mean()
        ),
        "by_technology": [
            {
                "technology": str(row.technology),
                "mean_efficiency_effect_pp": float(row["mean"]),
                "seed_level_se_pp": float(row.seed_level_se_pp),
            }
            for _, row in by_family.iterrows()
        ],
    }
    return paired, by_seed_family, result


def export(final, observations, destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    paired, by_seed_family, summary = summarize(final, observations)
    final.to_csv(destination / "final_firm_outcomes.csv", index=False)
    paired.to_csv(destination / "paired_firm_outcomes.csv", index=False)
    by_seed_family.to_csv(destination / "paired_seed_family_effects.csv", index=False)
    observations.groupby(
        ["population_seed", "learning_seed", "policy", "round"],
        as_index=False,
    ).agg(
        mean_exploration_probability=("exploration_probability", "mean"),
        mean_own_growth_pct=("own_growth_pct", "mean"),
        mean_peer_growth_pct=("peer_growth_pct", "mean"),
    ).to_csv(destination / "roundly_information_summary.csv", index=False)
    (destination / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    print("GAME 2 MATCHED EXPERIMENT PASSED")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--rounds", type=int, default=100)
    p.add_argument("--seeds", type=int, default=100)
    p.add_argument("--population-seed", type=int, default=2026)
    p.add_argument("--export-dir", type=Path, required=True)
    a = p.parse_args()
    export(*run_experiment(a.rounds, a.seeds, a.population_seed), a.export_dir)

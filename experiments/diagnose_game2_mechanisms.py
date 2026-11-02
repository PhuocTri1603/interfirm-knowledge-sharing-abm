"""Mechanism diagnostics for Game 2: choices, trigger timing, and efficiency paths.

No new decision rules. Each policy uses identical population and random schedule.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from interfirm_abm.competitive_simulation import CompetitiveSimulation
from interfirm_abm.production_optimum import optimal_output


def diagnose(rounds=100, seeds=20, population_seed=2026):
    if rounds < 3 or seeds < 1:
        raise ValueError("rounds >= 3 and seeds >= 1 required")
    rows = []
    for learning_seed in range(2026, 2026 + seeds):
        for policy in ("information_only", "performance_triggered"):
            sim = CompetitiveSimulation(
                n_firms=100, n_rounds=rounds, seed=learning_seed,
                competitive_policy=policy, heterogeneous_population=True,
                population_seed=population_seed,
            )
            history = sim.run()
            observations = pd.DataFrame(sim.observation_log)
            assert len(history) == len(observations) == 100 * rounds
            assert history[["round", "firm_id"]].equals(
                observations[["round", "firm_id"]]
            )
            history = history.copy()
            history["exploration_probability"] = observations["exploration_probability"]
            history["trigger_active"] = observations["exploration_probability"].eq(0.40)
            history["signal_available"] = observations["own_growth_pct"].notna()
            history["global_search"] = [
                (round_number == 1 or
                 sim.random_schedule.iloc[(round_number - 1) * 100 + firm_id - 1][
                     "exploration_draw"
                 ] < probability)
                for round_number, firm_id, probability in zip(
                    history["round"], history["firm_id"],
                    history["exploration_probability"]
                )
            ]
            optimum = {
                f.firm_id: optimal_output(
                    f.technology, f.budget, f.alpha, f.rho, f.productivity
                ) for f in sim.firms
            }
            history["efficiency_pct"] = [
                100 * output / optimum[firm_id]
                for firm_id, output in zip(history.firm_id, history.current_output)
            ]
            family = {f.firm_id: f.technology for f in sim.firms}
            history["technology"] = history.firm_id.map(family)
            grouped = history.groupby(["round", "technology"], as_index=False).agg(
                mean_efficiency_pct=("efficiency_pct", "mean"),
                acceptance_rate=("accepted", "mean"),
                global_search_rate=("global_search", "mean"),
                trigger_rate=("trigger_active", "mean"),
                signal_availability_rate=("signal_available", "mean"),
            )
            grouped["population_seed"] = population_seed
            grouped["learning_seed"] = learning_seed
            grouped["policy"] = policy
            rows.append(grouped)
    paths = pd.concat(rows, ignore_index=True)
    index = ["population_seed", "learning_seed", "round", "technology"]
    wide = paths.pivot(index=index, columns="policy",
                       values="mean_efficiency_pct").reset_index()
    wide["triggered_minus_control_pp"] = (
        wide["performance_triggered"] - wide["information_only"]
    )
    assert len(wide) == seeds * rounds * 4
    return paths, wide


def export(paths, paired, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    paths.to_csv(directory / "policy_round_family_paths.csv", index=False)
    paired.to_csv(directory / "paired_round_family_effects.csv", index=False)
    treatment = paths[paths.policy == "performance_triggered"]
    summary = {
        "population_seed": int(paths.population_seed.iloc[0]),
        "learning_seeds": int(paths.learning_seed.nunique()),
        "rounds": int(paths["round"].max()),
        "mean_trigger_rate_rounds_3_onward": float(
            treatment[treatment["round"] >= 3].trigger_rate.mean()
        ),
        "mean_global_search_rate_control": float(
            paths[paths.policy == "information_only"].global_search_rate.mean()
        ),
        "mean_global_search_rate_treatment": float(
            treatment.global_search_rate.mean()
        ),
        "mean_acceptance_rate_control": float(
            paths[paths.policy == "information_only"].acceptance_rate.mean()
        ),
        "mean_acceptance_rate_treatment": float(
            treatment.acceptance_rate.mean()
        ),
        "final_family_effect_pp": {
            name: float(g.triggered_minus_control_pp.mean())
            for name, g in paired[paired["round"] == paired["round"].max()]
                .groupby("technology")
        },
    }
    (directory / "mechanism_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--rounds", type=int, default=100)
    p.add_argument("--seeds", type=int, default=20)
    p.add_argument("--population-seed", type=int, default=2026)
    p.add_argument("--export-dir", type=Path, required=True)
    a = p.parse_args()
    export(*diagnose(a.rounds, a.seeds, a.population_seed), a.export_dir)

"""Paired heterogeneous Game 1 experiment; one population, independent learning seeds."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from interfirm_abm.simulation import Simulation
from interfirm_abm.production_optimum import optimal_output


def run_experiment(rounds, seeds=100, population_seed=2026):
    rows = []
    for seed in range(2026, 2026 + seeds):
        for policy in ("random", "guided"):
            sim = Simulation(n_firms=100, n_rounds=rounds, seed=seed,
                             learning_policy=policy, matched_randomness=True,
                             heterogeneous_population=True, population_seed=population_seed)
            sim.run()
            for firm in sim.firms:
                optimum = optimal_output(firm.technology, firm.budget, firm.alpha,
                                         firm.rho, firm.productivity)
                rows.append({"seed": seed, "policy": policy, "firm_id": firm.firm_id,
                             "technology": firm.technology, "alpha": firm.alpha,
                             "stratum": str(sim.population.iloc[firm.firm_id - 1]["stratum"]),
                             "rounds": rounds, "final_output": firm.current_output,
                             "efficiency_pct": 100 * firm.current_output / optimum,
                             "accepted": sum(x["accepted"] for x in firm.history)})
    result = pd.DataFrame(rows)
    assert len(result) == seeds * 100 * 2
    assert result.efficiency_pct.between(0, 100 + 1e-7).all()
    assert result.groupby(["seed", "policy"]).size().eq(100).all()
    assert result.groupby(["seed", "policy"]).apply(
        lambda g: (g.alpha < 0.5).sum(), include_groups=False
    ).eq(50).all()
    return result


def export(result, destination, population_seed):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    result.to_csv(destination / "final_firm_outcomes.csv", index=False)
    paired = result.pivot(index=["seed", "firm_id", "technology", "stratum", "alpha"],
                          columns="policy", values="efficiency_pct").reset_index()
    paired["guided_minus_random_efficiency_pp"] = paired["guided"] - paired["random"]
    paired.to_csv(destination / "paired_firm_outcomes.csv", index=False)
    seed_means = paired.groupby("seed", as_index=False)["guided_minus_random_efficiency_pp"].mean()
    seed_means.to_csv(destination / "paired_seed_effects.csv", index=False)
    effects = seed_means["guided_minus_random_efficiency_pp"].to_numpy()
    se = effects.std(ddof=1) / np.sqrt(len(effects)) if len(effects) > 1 else float("nan")
    summary = {"population_seed": population_seed, "learning_seeds": int(len(effects)),
               "firms": 100, "rounds": int(result.rounds.iloc[0]),
               "policies": ["random", "guided"], "mean_efficiency_effect_pp": float(effects.mean()),
               "seed_level_standard_error_pp": float(se),
               "normal_approx_95_ci_pp": [float(effects.mean() - 1.96 * se),
                                           float(effects.mean() + 1.96 * se)]}
    (destination / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--rounds", type=int, choices=(50, 100, 200), required=True)
    p.add_argument("--seeds", type=int, default=100)
    p.add_argument("--population-seed", type=int, default=2026)
    p.add_argument("--export-dir", type=Path, required=True)
    a = p.parse_args()
    if a.seeds < 2:
        p.error("--seeds must be at least 2 for confidence intervals")
    export(run_experiment(a.rounds, a.seeds, a.population_seed), a.export_dir, a.population_seed)

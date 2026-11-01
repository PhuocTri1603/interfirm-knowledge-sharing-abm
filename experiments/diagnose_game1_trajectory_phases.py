"""Phase-specific matched Guided vs Random efficiency, unchanged Game 1.

Exploratory 100-learning-seed robustness diagnostic. Population is the
independent unit for population-level generalization; seeds are paired draws.
"""
import argparse
import json
from pathlib import Path
import numpy as np
from interfirm_abm.simulation import Simulation
from interfirm_abm.production_optimum import optimal_output

PHASES = ((1, 25), (26, 50), (51, 75), (76, 100))
FAMILIES = ("CES", "Cobb-Douglas", "Leontief", "Linear")


def run(population_seed, learning_seeds=100):
    accum = {(t, p): [] for t in FAMILIES for p in range(4)}
    finals = {t: [] for t in FAMILIES}
    for seed in range(2026, 2026 + learning_seeds):
        policies = {}
        for policy in ("random", "guided"):
            sim = Simulation(n_firms=100, n_rounds=100, seed=seed,
                             learning_policy=policy, matched_randomness=True,
                             heterogeneous_population=True, population_seed=population_seed)
            history = sim.run()
            # Simulation records are round-major, firm-minor (1..100).
            assert len(history) == 10000
            assert np.array_equal(history.firm_id.to_numpy().reshape(100, 100)[0], np.arange(1, 101))
            outputs = history.current_output.to_numpy().reshape(100, 100)
            optima = np.array([optimal_output(f.technology, f.budget, f.alpha, f.rho, f.productivity)
                               for f in sim.firms])
            policies[policy] = 100 * outputs / optima[None, :]
            families = np.array([f.technology for f in sim.firms])
        delta = policies["guided"] - policies["random"]
        for family in FAMILIES:
            mask = families == family
            assert mask.sum() == 25
            finals[family].append(float(delta[-1, mask].mean()))
            for p, (start, end) in enumerate(PHASES):
                accum[(family, p)].append(float(delta[start-1:end, :][:, mask].mean()))
    summary = []
    for family in FAMILIES:
        phases = []
        for p, (start, end) in enumerate(PHASES):
            v = np.asarray(accum[(family, p)])
            phases.append({"rounds": f"{start}-{end}", "guided_minus_random_pp": float(v.mean()),
                           "learning_seed_sd_pp": float(v.std(ddof=1)),
                           "positive_seed_fraction": float(np.mean(v > 0))})
        final = np.asarray(finals[family])
        summary.append({"technology": family, "phases": phases,
                        "time_average_pp": float(np.mean([p["guided_minus_random_pp"] for p in phases])),
                        "final_advantage_pp": float(final.mean())})
    return {"population_seed": population_seed, "learning_seeds": learning_seeds,
            "horizon": 100, "summary": summary,
            "limitations": ["Exploratory descriptive analysis; not causal",
                            "Population-level inference requires treating five population draws as five draws",
                            "Repeated learning seeds are not independent populations",
                            "No multiple-comparison adjustment",
                            "Round-specific efficiency is post-acceptance"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--population-seed", type=int, required=True)
    parser.add_argument("--learning-seeds", type=int, default=100)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.population_seed, args.learning_seeds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print("PHASE ROBUSTNESS DIAGNOSTIC PASSED")
    for item in result["summary"]:
        print(json.dumps(item, sort_keys=True))

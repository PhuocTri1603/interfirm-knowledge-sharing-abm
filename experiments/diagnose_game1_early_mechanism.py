"""Diagnostic of early Guided underperformance; descriptive, unchanged model."""
import argparse
import json
from pathlib import Path
import numpy as np
from interfirm_abm.simulation import Simulation
from interfirm_abm.production_optimum import optimal_output

FAMILIES = ("CES", "Cobb-Douglas", "Leontief", "Linear")
PHASES = ((1, 25), (26, 50), (51, 75), (76, 100))

def run(population_seed, learning_seeds):
    data = {(family, i, policy): [] for family in FAMILIES for i in range(4)
            for policy in ("random", "guided")}
    for seed in range(2026, 2026 + learning_seeds):
        for policy in ("random", "guided"):
            sim = Simulation(n_firms=100, n_rounds=100, seed=seed,
                             learning_policy=policy, matched_randomness=True,
                             heterogeneous_population=True, population_seed=population_seed)
            h = sim.run()
            assert len(h) == 10000
            assert np.array_equal(h.firm_id.to_numpy().reshape(100, 100)[0], np.arange(1, 101))
            candidate = h.candidate_share.to_numpy().reshape(100, 100)
            candidate_output = h.candidate_output.to_numpy().reshape(100, 100)
            accepted = h.accepted.to_numpy().reshape(100, 100).astype(bool)
            output = h.current_output.to_numpy().reshape(100, 100)
            initial = np.array([f.produce(.5) for f in sim.firms])
            optimum = np.array([optimal_output(f.technology, f.budget, f.alpha, f.rho, f.productivity)
                                for f in sim.firms])
            families = np.array([f.technology for f in sim.firms])
            for family in FAMILIES:
                mask = families == family
                assert mask.sum() == 25
                for i, (start, end) in enumerate(PHASES):
                    sl = slice(start - 1, end)
                    a = accepted[sl, :][:, mask]
                    o = output[sl, :][:, mask]
                    prev = np.concatenate((initial[None, :], output[:-1, :]), axis=0)[sl, :][:, mask]
                    improvements = np.maximum(o - prev, 0)
                    cand = candidate[sl, :][:, mask]
                    # A guided local candidate is near the historically best candidate,
                    # not necessarily near the accepted incumbent; this is diagnostic only.
                    records = {
                        "efficiency_pct": float((100 * o / optimum[mask][None, :]).mean()),
                        "acceptance_rate": float(a.mean()),
                        "mean_improvement_pp_per_trial": float((100 * improvements / optimum[mask][None, :]).mean()),
                        "mean_candidate_distance_from_initial": float(np.abs(cand - .5).mean()),
                        "candidate_below_initial_rate": float((candidate_output[sl, :][:, mask] < initial[mask][None, :]).mean()),
                    }
                    data[(family, i, policy)].append(records)
    summary = []
    for family in FAMILIES:
        phases = []
        for i, (start, end) in enumerate(PHASES):
            policies = {}
            for policy in ("random", "guided"):
                policies[policy] = {key: float(np.mean([r[key] for r in data[(family, i, policy)]]))
                                    for key in data[(family, i, policy)][0]}
            phases.append({"rounds": f"{start}-{end}", "random": policies["random"],
                           "guided": policies["guided"],
                           "guided_minus_random": {key: policies["guided"][key] - policies["random"][key]
                                                   for key in policies["guided"]}})
        summary.append({"technology": family, "phases": phases})
    return {"population_seed": population_seed, "learning_seeds": learning_seeds,
            "horizon": 100, "summary": summary,
            "scope": "Descriptive accounting of observed trials; no causal identification",
            "limitations": ["5 population draws only across full study",
                            "Candidate below initial is not necessarily a rejected trial",
                            "Acceptance rate alone cannot identify search mechanism",
                            "Candidate distance from initial is not distance from optimum"]}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--population-seed", type=int, required=True)
    p.add_argument("--learning-seeds", type=int, default=100)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = run(args.population_seed, args.learning_seeds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print("EARLY MECHANISM ACCOUNTING PASSED")
    for row in result["summary"]:
        print(json.dumps(row, sort_keys=True))

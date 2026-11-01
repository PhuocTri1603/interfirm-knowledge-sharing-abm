"""Round-level paired Game 1 trajectories; unchanged economic/learning model."""
import argparse
import json
from pathlib import Path

import numpy as np

from interfirm_abm.production_optimum import optimal_output
from interfirm_abm.simulation import Simulation

FAMILIES = ("CES", "Cobb-Douglas", "Leontief", "Linear")


def run(population_seed, learning_seeds=100):
    deltas = {family: [] for family in FAMILIES}
    improvement_deltas = {family: [] for family in FAMILIES}
    acceptance_deltas = {family: [] for family in FAMILIES}
    for seed in range(2026, 2026 + learning_seeds):
        histories = {}
        for policy in ("random", "guided"):
            sim = Simulation(n_firms=100, n_rounds=100, seed=seed,
                             learning_policy=policy, matched_randomness=True,
                             heterogeneous_population=True,
                             population_seed=population_seed)
            h = sim.run()
            assert len(h) == 10000
            assert np.array_equal(h.firm_id.to_numpy().reshape(100, 100)[0],
                                  np.arange(1, 101))
            out = h.current_output.to_numpy().reshape(100, 100)
            opt = np.array([optimal_output(f.technology, f.budget, f.alpha,
                                           f.rho, f.productivity)
                            for f in sim.firms])
            initial = np.array([f.produce(0.5) for f in sim.firms])
            efficiency = 100 * out / opt[None, :]
            prior = np.vstack([initial[None, :], out[:-1]])
            improvement = 100 * np.maximum(out - prior, 0) / opt[None, :]
            histories[policy] = (efficiency, improvement,
                                 h.accepted.to_numpy().reshape(100, 100).astype(float))
            families = np.array([f.technology for f in sim.firms])
        for family in FAMILIES:
            mask = families == family
            assert mask.sum() == 25
            deltas[family].append((histories["guided"][0][:, mask]
                                   - histories["random"][0][:, mask]).mean(axis=1))
            improvement_deltas[family].append((histories["guided"][1][:, mask]
                                               - histories["random"][1][:, mask]).mean(axis=1))
            acceptance_deltas[family].append((histories["guided"][2][:, mask]
                                              - histories["random"][2][:, mask]).mean(axis=1))
    summary = []
    for family in FAMILIES:
        d = np.stack(deltas[family])
        flow = np.stack(improvement_deltas[family])
        acc = np.stack(acceptance_deltas[family])
        mean = d.mean(axis=0)
        # First positive *mean* is not a sustained crossing, nor an individual firm's crossing.
        first_positive = next((i + 1 for i, value in enumerate(mean) if value > 0), None)
        sustained_positive = next((i + 1 for i in range(100)
                                   if np.all(mean[i:] > 0)), None)
        rows = []
        for i in range(100):
            rows.append({
                "round": i + 1,
                "guided_minus_random_efficiency_pp": float(mean[i]),
                "learning_seed_sd_pp": float(d[:, i].std(ddof=1)) if learning_seeds > 1 else None,
                "positive_learning_seed_fraction": float((d[:, i] > 0).mean()),
                "guided_minus_random_improvement_pp": float(flow[:, i].mean()),
                "guided_minus_random_acceptance_rate": float(acc[:, i].mean()),
                "cumulative_guided_minus_random_improvement_pp": float(flow[:, :i + 1].sum(axis=1).mean()),
            })
        # Identity: paired level delta at round t equals cumulative paired
        # improvement from common initial conditions (up to floating error).
        assert np.allclose(mean, flow.cumsum(axis=1).mean(axis=0), atol=1e-9)
        summary.append({
            "technology": family,
            "first_positive_mean_round": first_positive,
            "first_sustained_positive_mean_round_through_100": sustained_positive,
            "mean_rounds_1_25_pp": float(mean[:25].mean()),
            "round_25_pp": float(mean[24]),
            "round_100_pp": float(mean[99]),
            "rounds": rows,
        })
    return {
        "population_seed": population_seed,
        "learning_seeds": learning_seeds,
        "horizon": 100,
        "summary": summary,
        "scope": "Round-specific descriptive paired trajectories; no causal identification",
        "limitations": [
            "First crossing is based on five-population-replicated mean within each population",
            "A sustained positive crossing through round 100 is horizon-specific",
            "Learning seeds are paired within a population, not independent populations",
            "No policy mechanism or economic assumptions changed",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--population-seed", type=int, required=True)
    parser.add_argument("--learning-seeds", type=int, default=100)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.population_seed, args.learning_seeds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print("ROUND TRAJECTORY DIAGNOSTIC PASSED")
    for row in result["summary"]:
        print(json.dumps({k: v for k, v in row.items() if k != "rounds"}, sort_keys=True))

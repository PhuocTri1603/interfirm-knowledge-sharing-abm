"""Exploratory paired search-trajectory diagnostic; original Game 1 rules unchanged.

Measures time to efficiency thresholds, acceptance rate and candidate proximity
to the firm-specific feasible optimum. Descriptive only; not causal.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from interfirm_abm.simulation import Simulation
from interfirm_abm.production_optimum import optimal_capital_share, optimal_output


def run(populations, seeds, rounds):
    rows = []
    for pop in populations:
        for seed in range(2026, 2026 + seeds):
            for policy in ("random", "guided"):
                sim = Simulation(n_firms=100, n_rounds=rounds, seed=seed,
                                 learning_policy=policy, matched_randomness=True,
                                 heterogeneous_population=True, population_seed=pop)
                history = sim.run()
                for firm in sim.firms:
                    h = history.loc[history.firm_id == firm.firm_id].sort_values("round")
                    assert len(h) == rounds
                    optimum = optimal_output(firm.technology, firm.budget, firm.alpha,
                                             firm.rho, firm.productivity)
                    optimal_share = optimal_capital_share(firm.technology, firm.alpha, firm.rho)
                    initial_eff = 100 * firm.produce(.5) / optimum
                    efficiencies = 100 * h.current_output.to_numpy() / optimum
                    def first_threshold(threshold):
                        hit = np.flatnonzero(efficiencies >= threshold)
                        return int(hit[0] + 1) if len(hit) else None
                    rows.append({
                        "population_seed": pop, "seed": seed, "policy": policy,
                        "firm_id": firm.firm_id, "technology": firm.technology,
                        "alpha": firm.alpha, "initial_gap_pp": 100 - initial_eff,
                        "optimal_share": optimal_share,
                        "initial_share_distance": abs(.5 - optimal_share),
                        "final_efficiency_pct": float(efficiencies[-1]),
                        "mean_efficiency_pct": float(efficiencies.mean()),
                        "accepted_fraction": float(h.accepted.mean()),
                        "mean_candidate_distance": float(np.mean(abs(h.candidate_share.to_numpy() - optimal_share))),
                        "mean_realized_share_distance": float(np.mean(abs(h.capital_share.to_numpy() - optimal_share))),
                        "round_to_95pct": first_threshold(95),
                        "round_to_99pct": first_threshold(99),
                    })
    df = pd.DataFrame(rows)
    assert len(df) == len(populations) * seeds * 2 * 100
    paired = df.pivot(index=["population_seed", "seed", "firm_id", "technology", "alpha", "initial_gap_pp"],
                      columns="policy", values=["final_efficiency_pct", "mean_efficiency_pct",
                                               "accepted_fraction", "mean_candidate_distance",
                                               "mean_realized_share_distance"])
    paired.columns = [f"{metric}_{policy}" for metric, policy in paired.columns]
    paired = paired.reset_index()
    paired["final_advantage_pp"] = paired.final_efficiency_pct_guided - paired.final_efficiency_pct_random
    paired["path_advantage_pp"] = paired.mean_efficiency_pct_guided - paired.mean_efficiency_pct_random
    paired["candidate_distance_delta"] = paired.mean_candidate_distance_guided - paired.mean_candidate_distance_random
    paired["realized_distance_delta"] = paired.mean_realized_share_distance_guided - paired.mean_realized_share_distance_random
    summary = []
    for technology, part in paired.groupby("technology"):
        pop_means = part.groupby("population_seed")[["final_advantage_pp", "path_advantage_pp",
                      "candidate_distance_delta", "realized_distance_delta"]].mean()
        summary.append({"technology": technology, "populations": len(pop_means),
                        "firms_per_population": 25, "learning_seeds": seeds,
                        **{k: float(pop_means[k].mean()) for k in pop_means.columns},
                        "population_range_final_advantage_pp": [
                            float(pop_means.final_advantage_pp.min()),
                            float(pop_means.final_advantage_pp.max())]})
    return {"design": {"populations": populations, "learning_seeds": seeds, "rounds": rounds,
                        "policies": ["random", "guided"], "matched_randomness": True},
            "cautions": ["New exploratory rerun, not original archived trajectory data",
                         "Same learning seeds across populations",
                         "Descriptive, no causal identification",
                         "Threshold hitting times right-censored; not interpreted as uncensored means",
                         "Candidate-distance and efficiency are not comparable across technologies",
                         "Five population draws only"],
            "summary": summary,
            "threshold_hit_rates": df.groupby(["technology", "policy"]).agg(
                hit95=("round_to_95pct", lambda s: float(s.notna().mean())),
                hit99=("round_to_99pct", lambda s: float(s.notna().mean()))).reset_index().to_dict(orient="records")}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--rounds", type=int, default=100)
    p.add_argument("--seeds", type=int, default=20)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    result = run(list(range(2026, 2031)), a.seeds, a.rounds)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2) + "\n")
    print("SEARCH TRAJECTORY DIAGNOSTIC PASSED")
    for item in result["summary"]:
        print(json.dumps(item, sort_keys=True))
    for item in result["threshold_hit_rates"]:
        print("THRESHOLD " + json.dumps(item, sort_keys=True))

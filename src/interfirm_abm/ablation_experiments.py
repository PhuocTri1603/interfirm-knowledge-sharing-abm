"""Matched-seed 2x2 ablation experiments for Game 3C."""

import pandas as pd

from interfirm_abm.disclosure_simulation import DisclosureSimulation


ABLATION_SCENARIOS = {
    "OpenSharing": (False, False),
    "DisclosureOnly": (True, False),
    "ReciprocityOnly": (False, True),
    "FullGame3C": (True, True),
}


def run_ablation(
    seeds,
    n_firms=20,
    n_rounds=50,
    disclosure_cost_rate=0.005,
    learning_rate=0.30,
    temperature=0.01,
):
    """Run all four scenarios using matched initial conditions."""
    rows = []

    for seed in seeds:
        for scenario, (disclosure, reciprocity) in ABLATION_SCENARIOS.items():
            simulation = DisclosureSimulation(
                n_firms=n_firms,
                n_rounds=n_rounds,
                seed=seed,
                transfer_policy="mixed",
                disclosure_cost_rate=disclosure_cost_rate,
                learning_rate=learning_rate,
                temperature=temperature,
                selective_disclosure=disclosure,
                conditional_reciprocity=reciprocity,
            )

            results = simulation.run()

            outputs = (
                results.groupby("round")["current_output"]
                .mean()
                .sort_index()
            )

            decisions = simulation.disclosure_log
            accepted = int(results["accepted"].sum())
            published = sum(x["shared"] for x in decisions)

            rows.append({
                "seed": seed,
                "scenario": scenario,
                "selective_disclosure": disclosure,
                "conditional_reciprocity": reciprocity,
                "mean_final_output": float(outputs.iloc[-1]),
                "learning_auc": float(outputs.mean()),
                "accepted": accepted,
                "published": published,
                "share_rate": (
                    published / len(decisions)
                    if decisions else float("nan")
                ),
                "shared_learning": sum(
                    x["learning_source"] == "shared"
                    for x in simulation.learning_log
                ),
                "access_rate": (
                    sum(x["access_granted"] for x in simulation.access_log)
                    / len(simulation.access_log)
                    if simulation.access_log else float("nan")
                ),
            })

    return pd.DataFrame(rows)

"""Monte Carlo comparison of Games 3A, 3B, and 3C."""

import pandas as pd

from interfirm_abm.cooperative_simulation import CooperativeSimulation
from interfirm_abm.cross_technology_simulation import CrossTechnologySimulation
from interfirm_abm.disclosure_simulation import DisclosureSimulation


def run_monte_carlo(
    seeds,
    n_firms=20,
    n_rounds=50,
    disclosure_cost_rate=0.005,
    learning_rate=0.30,
    temperature=0.01,
):
    """Run matched-seed simulations and return seed-level metrics."""

    rows = []

    for seed in seeds:
        models = {
            "Game3A": CooperativeSimulation(
                n_firms=n_firms,
                n_rounds=n_rounds,
                seed=seed,
            ),
            "Game3B": CrossTechnologySimulation(
                n_firms=n_firms,
                n_rounds=n_rounds,
                seed=seed,
                transfer_policy="mixed",
            ),
            "Game3C": DisclosureSimulation(
                n_firms=n_firms,
                n_rounds=n_rounds,
                seed=seed,
                transfer_policy="mixed",
                disclosure_cost_rate=disclosure_cost_rate,
                learning_rate=learning_rate,
                temperature=temperature,
            ),
        }

        for model_name, simulation in models.items():
            results = simulation.run()

            round_outputs = (
                results.groupby("round")["current_output"].mean()
                .sort_index()
            )

            learning_log = simulation.learning_log

            shared_learning = sum(
                entry["learning_source"] == "shared"
                for entry in learning_log
            )

            decisions = getattr(simulation, "disclosure_log", [])

            share_rate = (
                sum(entry["shared"] for entry in decisions)
                / len(decisions)
                if decisions
                else float("nan")
            )

            rows.append({
                "seed": seed,
                "model": model_name,
                "mean_final_output": float(round_outputs.iloc[-1]),
                "learning_auc": float(round_outputs.mean()),
                "accepted": int(results["accepted"].sum()),
                "shared_learning": shared_learning,
                "share_rate": share_rate,
            })

    return pd.DataFrame(rows)

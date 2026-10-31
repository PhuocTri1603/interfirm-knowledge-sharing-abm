"""
Minimal Agent-Based Simulation.

Game 1: Independent Learning.

Each firm experiments independently with capital-labor
allocation and retains improvements in production output.
"""

import numpy as np
import pandas as pd

from interfirm_abm.firm import Firm
from interfirm_abm.random_schedule import (
    generate_random_schedule,
)
from interfirm_abm.learning import (
    random_exploration,
    experience_guided_exploration,
)


TECHNOLOGIES = [
    "Cobb-Douglas",
    "Leontief",
    "Linear",
    "CES",
]


class Simulation:
    def __init__(
        self,
        n_firms=20,
        n_rounds=50,
        budget=100.0,
        seed=2026,
        learning_policy="random",
        matched_randomness=False,
        exploration_probability=0.20,
        search_radius=0.10,
    ):
        if not isinstance(n_firms, int) or n_firms <= 0:
            raise ValueError("n_firms must be a positive integer.")

        if not isinstance(n_rounds, int) or n_rounds <= 0:
            raise ValueError("n_rounds must be a positive integer.")

        if learning_policy not in ("random", "guided", "guided_initial"):
            raise ValueError("Unknown learning policy.")

        if not np.isfinite(exploration_probability) or not 0 <= exploration_probability <= 1:
            raise ValueError("exploration_probability must be finite and in [0, 1].")
        if not np.isfinite(search_radius) or search_radius <= 0:
            raise ValueError("search_radius must be positive and finite.")

        self.exploration_probability = float(exploration_probability)
        self.search_radius = float(search_radius)
        self.learning_policy = learning_policy
        self.matched_randomness = matched_randomness
        self.random_schedule = (
            generate_random_schedule(n_firms, n_rounds, seed)
            if matched_randomness else None
        )
        self.n_firms = n_firms
        self.n_rounds = n_rounds
        self.rng = np.random.default_rng(seed)

        self.firms = [
            Firm(
                firm_id=i + 1,
                technology=TECHNOLOGIES[i % 4],
                budget=budget,
            )
            for i in range(n_firms)
        ]

        self.records = []

    def run(self):
        if self.records:
            raise RuntimeError(
                "Simulation has already been run."
            )

        for round_number in range(1, self.n_rounds + 1):
            for firm in self.firms:
                if self.matched_randomness:
                    index = (
                        (round_number - 1) * self.n_firms
                        + (firm.firm_id - 1)
                    )
                    draw = self.random_schedule.iloc[index]

                    if self.learning_policy == "random":
                        candidate_share = (
                            0.05 + 0.90 * draw["uniform_draw"]
                        )
                    elif (
                        not firm.history
                        or draw["exploration_draw"] < self.exploration_probability
                    ):
                        candidate_share = (
                            0.05 + 0.90 * draw["uniform_draw"]
                        )
                    else:
                        best = max(
                            firm.history,
                            key=lambda r: r["candidate_output"],
                        )
                        center = best["candidate_share"]

                        if self.learning_policy == "guided_initial":
                            initial_output = firm.produce(0.50)

                            if initial_output >= best["candidate_output"]:
                                center = 0.50

                        candidate_share = float(np.clip(
                            center + self.search_radius * draw["normal_draw"],
                            0.05,
                            0.95,
                        ))
                elif self.learning_policy == "random":
                    candidate_share = random_exploration(
                        self.rng
                    )
                elif self.learning_policy == "guided":
                    candidate_share = experience_guided_exploration(
                        firm.history,
                        self.rng,
                        exploration_probability=self.exploration_probability,
                        search_radius=self.search_radius,
                    )
                else:
                    raise ValueError(
                        "guided_initial requires matched_randomness=True"
                    )

                record = firm.experiment(
                    candidate_share,
                    round_number,
                )

                self.records.append(record.copy())

        return pd.DataFrame(self.records)

    def summary(self):
        if not self.records:
            raise RuntimeError(
                "Run the simulation before requesting a summary."
            )

        rows = []

        for firm in self.firms:
            initial_output = firm.produce(0.50)

            rows.append({
                "firm_id": firm.firm_id,
                "technology": firm.technology,
                "initial_output": initial_output,
                "final_output": firm.current_output,
                "final_capital_share": firm.capital_share,
                "output_growth_pct": (
                    firm.current_output / initial_output - 1
                ) * 100,
                "accepted_experiments": sum(
                    record["accepted"]
                    for record in firm.history
                ),
            })

        return pd.DataFrame(rows)


if __name__ == "__main__":
    simulation = Simulation()
    history = simulation.run()
    summary = simulation.summary()

    print("\n===== SIMULATION CONFIGURATION =====")
    print("Firms:", simulation.n_firms)
    print("Rounds:", simulation.n_rounds)
    print("Total experiments:", len(history))

    print("\n===== RESULTS BY TECHNOLOGY =====")
    print(
        summary.groupby("technology")
        .agg(
            firms=("firm_id", "count"),
            mean_growth_pct=("output_growth_pct", "mean"),
            mean_final_share=("final_capital_share", "mean"),
            mean_accepted=("accepted_experiments", "mean"),
        )
        .round(4)
        .to_string()
    )

    print("\n===== OVERALL SUMMARY =====")
    print(
        "Mean output growth:",
        round(summary.output_growth_pct.mean(), 4),
        "%"
    )
    print(
        "Total accepted experiments:",
        int(summary.accepted_experiments.sum())
    )

"""
Minimal Agent-Based Simulation.

Game 1: Independent Learning.

Each firm experiments independently with capital-labor
allocation and retains improvements in production output.
"""

import numpy as np
import pandas as pd

from interfirm_abm.firm import Firm


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
    ):
        if not isinstance(n_firms, int) or n_firms <= 0:
            raise ValueError("n_firms must be a positive integer.")

        if not isinstance(n_rounds, int) or n_rounds <= 0:
            raise ValueError("n_rounds must be a positive integer.")

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
                candidate_share = float(
                    self.rng.uniform(0.05, 0.95)
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

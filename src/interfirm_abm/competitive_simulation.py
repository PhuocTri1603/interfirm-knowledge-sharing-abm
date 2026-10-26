"""
Game 2: Competitive Learning.

Policies:
- information_only: public information does not affect decisions.
- performance_triggered: underperforming firms explore more.

All firms observe previous-round public information.
"""

import numpy as np
import pandas as pd

from interfirm_abm.simulation import Simulation
from interfirm_abm.public_information import (
    PublicInformationTimeline,
)
from interfirm_abm.competitive_learning import (
    performance_triggered_exploration_probability,
)


class CompetitiveSimulation(Simulation):

    def __init__(
        self,
        n_firms=20,
        n_rounds=50,
        budget=100.0,
        seed=2026,
        competitive_policy="information_only",
    ):
        if competitive_policy not in (
            "information_only",
            "performance_triggered",
        ):
            raise ValueError("Unknown competitive policy.")

        super().__init__(
            n_firms=n_firms,
            n_rounds=n_rounds,
            budget=budget,
            seed=seed,
            learning_policy="guided_initial",
            matched_randomness=True,
        )

        self.competitive_policy = competitive_policy
        self.public_timeline = PublicInformationTimeline(
            self.firms
        )
        self.observation_log = []

    def _growth_signals(self, firm, round_number):
        """
        Compute own and same-technology peer growth
        using only completed public snapshots.
        """
        if round_number < 3:
            return None

        previous = {
            record["firm_id"]: record
            for record in self.public_timeline.get_snapshot(
                round_number - 2
            )
        }

        current = {
            record["firm_id"]: record
            for record in self.public_timeline.get_snapshot(
                round_number - 1
            )
        }

        own_growth = (
            current[firm.firm_id]["output"]
            / previous[firm.firm_id]["output"] - 1
        ) * 100

        peer_ids = [
            firm_id
            for firm_id, record in current.items()
            if firm_id != firm.firm_id
            and record["technology"] == firm.technology
        ]

        if not peer_ids:
            return None

        peer_growth = np.mean([
            (
                current[firm_id]["output"]
                / previous[firm_id]["output"] - 1
            ) * 100
            for firm_id in peer_ids
        ])

        return float(own_growth), float(peer_growth)

    def run(self):
        if self.records:
            raise RuntimeError(
                "Simulation has already been run."
            )

        for round_number in range(1, self.n_rounds + 1):
            for firm in self.firms:

                observations = self.public_timeline.observe(
                    observer_id=firm.firm_id,
                    round_number=round_number,
                )

                exploration_probability = 0.20
                signals = None

                if self.competitive_policy == "performance_triggered":
                    signals = self._growth_signals(
                        firm,
                        round_number,
                    )

                    if signals is not None:
                        exploration_probability = (
                            performance_triggered_exploration_probability(
                                own_growth=signals[0],
                                peer_growth=signals[1],
                            )
                        )

                self.observation_log.append({
                    "round": round_number,
                    "firm_id": firm.firm_id,
                    "observed_round": round_number - 1,
                    "n_competitors": len(observations),
                    "exploration_probability": exploration_probability,
                    "own_growth_pct": (
                        signals[0] if signals is not None else None
                    ),
                    "peer_growth_pct": (
                        signals[1] if signals is not None else None
                    ),
                })

                index = (
                    (round_number - 1) * self.n_firms
                    + firm.firm_id - 1
                )
                draw = self.random_schedule.iloc[index]

                if (
                    not firm.history
                    or draw["exploration_draw"]
                    < exploration_probability
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

                    if (
                        firm.produce(0.50)
                        >= best["candidate_output"]
                    ):
                        center = 0.50

                    candidate_share = float(np.clip(
                        center + 0.10 * draw["normal_draw"],
                        0.05,
                        0.95,
                    ))

                record = firm.experiment(
                    candidate_share,
                    round_number,
                )
                self.records.append(record.copy())

            self.public_timeline.record_round(
                self.firms,
                round_number,
            )

        return pd.DataFrame(self.records)

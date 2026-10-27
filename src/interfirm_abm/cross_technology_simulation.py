import numpy as np
import pandas as pd

from interfirm_abm.cooperative_simulation import CooperativeSimulation
from interfirm_abm.production_optimum import (
    remaining_improvement_potential,
    optimal_capital_share,
)
from interfirm_abm.cross_technology_learning import (
    select_transfer_experiment,
)


class CrossTechnologySimulation(CooperativeSimulation):
    """
    Game 3B: cooperative learning with configurable
    source-recipient technology matching.

    Preserves Game 3A's random schedule, learning rules,
    one-round information delay, and one experiment per round.
    """

    def __init__(
        self,
        n_firms=20,
        n_rounds=50,
        budget=100.0,
        seed=2026,
        sharing_probability=0.30,
        transfer_policy="cross_technology",
    ):
        super().__init__(
            n_firms=n_firms,
            n_rounds=n_rounds,
            budget=budget,
            seed=seed,
            sharing_probability=sharing_probability,
        )

        valid_policies = {
            "same_technology",
            "cross_technology",
            "mixed",
        }

        if transfer_policy not in valid_policies:
            raise ValueError(
                f"Unknown transfer policy: {transfer_policy}"
            )

        self.transfer_policy = transfer_policy
        self.transfer_log = []

    def run(self):
        if self.records:
            raise RuntimeError("Simulation has already been run.")

        for round_number in range(1, self.n_rounds + 1):
            for firm in self.firms:
                index = (
                    (round_number - 1) * self.n_firms
                    + firm.firm_id - 1
                )

                draw = self.random_schedule.iloc[index]

                shared_history = self.knowledge_timeline.observe(
                    observer_id=firm.firm_id,
                    round_number=round_number,
                )

                source = None
                selected_peer_id = None

                if (
                    not firm.history
                    or draw["exploration_draw"] < 0.20
                ):
                    candidate_share = (
                        0.05 + 0.90 * draw["uniform_draw"]
                    )
                    source = "random"

                elif (
                    draw["exploration_draw"]
                    < 0.20 + self.sharing_probability
                ):
                    selected = select_transfer_experiment(
                        shared_history=shared_history,
                        recipient_technology=firm.technology,
                        rng=self.knowledge_rng,
                        transfer_policy=self.transfer_policy,
                    )

                    if selected is None:
                        candidate_share = self._own_guided_candidate(
                            firm,
                            draw["normal_draw"],
                        )
                        source = "own_fallback"

                    else:
                        selected_peer_id = selected["firm_id"]

                        candidate_share = float(np.clip(
                            selected["candidate_share"]
                            + 0.10 * draw["normal_draw"],
                            0.05,
                            0.95,
                        ))
                        source = "shared"

                else:
                    candidate_share = self._own_guided_candidate(
                        firm,
                        draw["normal_draw"],
                    )
                    source = "own"

                previous_share = firm.capital_share
                previous_output = firm.current_output
                remaining_potential = (
                    remaining_improvement_potential(
                        firm.technology,
                        previous_output,
                        firm.budget,
                    )
                ) if source == 'shared' else None
                record = firm.experiment(
                    candidate_share,
                    round_number,
                )

                self.records.append(record.copy())
                if source == "shared":
                    self.transfer_log.append({
                        "round": round_number,
                        "recipient_id": firm.firm_id,
                        "recipient_technology": firm.technology,
                        "source_id": selected["firm_id"],
                        "source_technology": selected["technology"],
                        "source_round": selected["round"],
                        "source_candidate_share": selected["candidate_share"],
                        "recipient_candidate_share": candidate_share,
                        "source_output": selected["candidate_output"],
                        "recipient_candidate_output": record["candidate_output"],
                        "recipient_previous_output": previous_output,
                        "recipient_previous_share": previous_share,
                        "allocation_distance_to_optimum": abs(
                            candidate_share
                            - optimal_capital_share(firm.technology)
                        ),
                        "remaining_potential_before_transfer": remaining_potential,
                        "near_optimum": remaining_potential <= 1e-8,
                        "normalized_transfer_gain": (
                            (record["current_output"] - previous_output)
                            / remaining_potential
                            if remaining_potential > 1e-8 else None
                        ),
                        "recipient_accepted": record["accepted"],
                        "recipient_output_gain": (
                            record["current_output"] - previous_output
                        ),
                    })

                self.learning_log.append({
                    "round": round_number,
                    "firm_id": firm.firm_id,
                    "technology": firm.technology,
                    "learning_source": source,
                    "selected_peer_id": selected_peer_id,
                    "candidate_share": candidate_share,
                    "accepted": record["accepted"],
                })

            self.knowledge_timeline.record_round(
                self.firms,
                round_number,
            )

        return pd.DataFrame(self.records)

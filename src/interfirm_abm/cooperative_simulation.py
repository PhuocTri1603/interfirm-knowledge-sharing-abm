import numpy as np
import pandas as pd

from interfirm_abm.simulation import Simulation
from interfirm_abm.shared_knowledge import SharedKnowledgeTimeline
from interfirm_abm.cooperative_learning import select_shared_experiment


class CooperativeSimulation(Simulation):
    """
    Game 3A: free sharing of successful experiments
    between firms with the same technology.

    Policy:
      20% random exploration
      30% shared-knowledge exploration
      50% independent guided exploration

    One experiment per firm per round.
    """

    def __init__(
        self,
        n_firms=20,
        n_rounds=50,
        budget=100.0,
        seed=2026,
        sharing_probability=0.30,
    ):
        super().__init__(
            n_firms=n_firms,
            n_rounds=n_rounds,
            budget=budget,
            seed=seed,
            learning_policy="guided_initial",
            matched_randomness=True,
        )

        if not np.isfinite(sharing_probability) or not 0 <= sharing_probability <= 0.80:
            raise ValueError(
                'sharing_probability must be between 0 and 0.80.'
            )
        self.sharing_probability = float(sharing_probability)
        self.knowledge_timeline = SharedKnowledgeTimeline()
        self.knowledge_rng = np.random.default_rng(seed + 1000000)
        self.learning_log = []

    def _own_guided_candidate(self, firm, normal_draw):
        if not firm.history:
            raise ValueError("Own history is empty.")

        best = max(
            firm.history,
            key=lambda record: record["candidate_output"],
        )

        center = best["candidate_share"]

        if firm.produce(0.50) >= best["candidate_output"]:
            center = 0.50

        return float(np.clip(
            center + 0.10 * normal_draw,
            0.05,
            0.95,
        ))

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

                if not firm.history or draw["exploration_draw"] < 0.20:
                    candidate_share = (
                        0.05 + 0.90 * draw["uniform_draw"]
                    )
                    source = "random"

                elif draw["exploration_draw"] < 0.20 + self.sharing_probability:
                    selected = select_shared_experiment(
                        shared_history=shared_history,
                        recipient_technology=firm.technology,
                        rng=self.knowledge_rng,
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

                record = firm.experiment(
                    candidate_share,
                    round_number,
                )
                self.records.append(record.copy())

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

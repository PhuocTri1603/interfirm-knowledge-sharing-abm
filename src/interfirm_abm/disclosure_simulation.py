"""Game 3C: strategic disclosure and conditional reciprocity."""

import numpy as np
import pandas as pd

from interfirm_abm.disclosure_learning import (
    ContributionHistory,
    DisclosureLearner,
)
from interfirm_abm.cross_technology_simulation import (
    CrossTechnologySimulation,
)
from interfirm_abm.selective_knowledge import SelectiveKnowledgePool


class DisclosureSimulation(CrossTechnologySimulation):
    """Game 3C simulation with selective knowledge access."""

    def __init__(
        self,
        n_firms=20,
        n_rounds=50,
        budget=100.0,
        seed=2026,
        sharing_probability=0.30,
        transfer_policy="mixed",
        disclosure_cost_rate=0.005,
        learning_rate=0.30,
        temperature=0.01,
        selective_disclosure=True,
        conditional_reciprocity=True,
    ):
        super().__init__(
            n_firms=n_firms,
            n_rounds=n_rounds,
            budget=budget,
            seed=seed,
            sharing_probability=sharing_probability,
            transfer_policy=transfer_policy,
        )

        if not 0.0 <= disclosure_cost_rate:
            raise ValueError("disclosure_cost_rate must be nonnegative")
        if not 0.0 < learning_rate <= 1.0:
            raise ValueError("learning_rate must be in (0, 1]")
        if not temperature > 0.0:
            raise ValueError("temperature must be positive")

        self.disclosure_cost_rate = disclosure_cost_rate
        self.selective_disclosure = selective_disclosure
        self.conditional_reciprocity = conditional_reciprocity
        self.knowledge_pool = SelectiveKnowledgePool()
        self.contribution_histories = {
            firm.firm_id: ContributionHistory(window=5)
            for firm in self.firms
        }
        self.access_rng = np.random.default_rng(seed + 2_000_000)
        self.access_cache = {}
        self.access_log = []
        self.disclosure_rng = np.random.default_rng(seed + 3_000_000)
        self.disclosure_learners = {
            firm.firm_id: DisclosureLearner(
                temperature=temperature,
                learning_rate=learning_rate,
            )
            for firm in self.firms
        }
        self.disclosure_log = []
        self.reward_log = []

    def available_knowledge(
        self,
        firm,
        round_number,
        access_granted,
    ):
        """Return accessible knowledge matching the transfer policy."""
        if not access_granted:
            return []

        records = self.knowledge_pool.observe(
            observer_id=firm.firm_id,
            round_number=round_number,
        )

        if self.transfer_policy == "same_technology":
            return [
                record for record in records
                if record["technology"] == firm.technology
            ]

        if self.transfer_policy == "cross_technology":
            return [
                record for record in records
                if record["technology"] != firm.technology
            ]

        return records

    def draw_access(self, firm_id, round_number):
        """Draw access once per firm per round using prior reputation."""
        key = (firm_id, round_number)

        if key in self.access_cache:
            return self.access_cache[key]

        history = self.contribution_histories[firm_id]
        if self.conditional_reciprocity:
            probability = history.access_probability(round_number)
            draw = float(self.access_rng.random())
            granted = bool(draw < probability)
        else:
            probability = 1.0
            draw = None
            granted = True

        self.access_cache[key] = granted
        self.access_log.append(
            {
                "firm_id": firm_id,
                "round": round_number,
                "reputation": history.reputation(round_number),
                "access_probability": probability,
                "access_draw": draw,
                "access_granted": granted,
            }
        )

        return granted

    @staticmethod
    def choose_learning_strategy(draw, shared_available, own_available):
        """Choose a feasible learning strategy using one uniform draw."""
        if not 0.0 <= draw < 1.0:
            raise ValueError("draw must be in [0, 1)")

        if not shared_available and not own_available:
            return "random"

        if not shared_available:
            return "random" if draw < 2.0 / 7.0 else "own"

        if not own_available:
            return "random" if draw < 0.70 else "shared"

        if draw < 0.20:
            return "random"

        if draw < 0.50:
            return "shared"

        return "own"

    def run(self):
        """Run Game 3C with strategic disclosure and selective access."""
        if self.records:
            raise RuntimeError("Simulation has already been run.")

        for round_number in range(1, self.n_rounds + 1):
            for firm in self.firms:
                firm_id = firm.firm_id
                index = (
                    (round_number - 1) * self.n_firms
                    + firm_id - 1
                )
                draw = self.random_schedule.iloc[index]

                access_granted = self.draw_access(
                    firm_id=firm_id,
                    round_number=round_number,
                )
                shared_history = self.available_knowledge(
                    firm=firm,
                    round_number=round_number,
                    access_granted=access_granted,
                )

                strategy = self.choose_learning_strategy(
                    draw=float(draw["exploration_draw"]),
                    shared_available=bool(shared_history),
                    own_available=bool(firm.history),
                )

                selected = None
                selected_peer_id = None

                if strategy == "random":
                    candidate_share = (
                        0.05 + 0.90 * float(draw["uniform_draw"])
                    )
                elif strategy == "shared":
                    selected = shared_history[
                        int(self.knowledge_rng.integers(len(shared_history)))
                    ]
                    selected_peer_id = selected["firm_id"]
                    candidate_share = float(np.clip(
                        selected["candidate_share"]
                        + 0.10 * float(draw["normal_draw"]),
                        0.05,
                        0.95,
                    ))
                else:
                    candidate_share = self._own_guided_candidate(
                        firm,
                        draw["normal_draw"],
                    )

                previous_output = firm.current_output
                record = firm.experiment(
                    candidate_share,
                    round_number,
                )
                self.records.append(record.copy())

                if strategy == "shared":
                    gain = max(
                        0.0,
                        record["current_output"] - previous_output,
                    )
                    self.disclosure_learners[
                        firm_id
                    ].observe_shared_gain(round_number, gain)

                self.learning_log.append({
                    "round": round_number,
                    "firm_id": firm_id,
                    "technology": firm.technology,
                    "learning_source": strategy,
                    "selected_peer_id": selected_peer_id,
                    "candidate_share": candidate_share,
                    "accepted": record["accepted"],
                })

                if record["accepted"]:
                    learner = self.disclosure_learners[firm_id]
                    if self.selective_disclosure:
                        probability = learner.share_probability()
                        shared = bool(
                            self.disclosure_rng.random() < probability
                        )

                        learner.record_decision(
                            round_number=round_number,
                            shared=shared,
                            baseline_output=record["current_output"],
                            disclosure_cost_rate=self.disclosure_cost_rate,
                        )
                    else:
                        probability = 1.0
                        shared = True

                    self.contribution_histories[firm_id].record(
                        round_number=round_number,
                        shared=shared,
                    )

                    self.knowledge_pool.publish(
                        experiment=record,
                        shared=shared,
                    )

                    self.disclosure_log.append({
                        "round": round_number,
                        "firm_id": firm_id,
                        "accepted": True,
                        "shared": shared,
                        "share_probability": probability,
                    })

            for firm in self.firms:
                learner = self.disclosure_learners[firm.firm_id]
                matured = learner.finalize_rewards(round_number)

                for reward in matured:
                    self.reward_log.append({
                        "firm_id": firm.firm_id,
                        "evaluation_round": round_number,
                        **reward,
                    })

        return pd.DataFrame(self.records)

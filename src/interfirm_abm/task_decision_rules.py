"""Researcher-configured candidate-plan decision rules for task allocation.

This implements a transparent finite-choice optimization operator, not an
assumption about firms' information, forecasting, or task technology.
Candidates and expected-payoff evaluator must be supplied by the researcher.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Callable, Mapping

from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm
from interfirm_abm.task_economic_policy import MarketObservation


TaskPlan = tuple[TaskAllocation, ...]
CandidateGenerator = Callable[[TaskBasedFirm, MarketObservation], Mapping[str, TaskPlan]]
ExpectedBenefit = Callable[[TaskBasedFirm, MarketObservation, str, TaskPlan], float]


@dataclass
class FiniteChoiceOptimization:
    candidates: CandidateGenerator
    expected_benefit: ExpectedBenefit

    def decide_tasks(
        self, firm: TaskBasedFirm, observation: MarketObservation
    ) -> TaskPlan:
        options = self.candidates(firm, observation)
        if not options:
            raise ValueError("candidate plans must be nonempty")
        scored = []
        for option_id, plan in options.items():
            if not option_id:
                raise ValueError("candidate ID must be nonempty")
            plan = tuple(plan)
            firm.evaluate_allocation(list(plan))
            benefit = float(self.expected_benefit(firm, observation, option_id, plan))
            if not isfinite(benefit):
                raise ValueError("expected benefit must be finite")
            scored.append((benefit, option_id, plan))
        # Deterministic tie-breaking makes Monte Carlo comparisons auditable.
        return sorted(scored, key=lambda item: (-item[0], item[1]))[0][2]

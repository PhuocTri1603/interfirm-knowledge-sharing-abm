"""Information contracts for adaptive task strategies.

A forecast is an explicitly supplied belief, not a realized market outcome.
Realized feedback is delivered only after simultaneous market clearing.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Callable, Mapping

from interfirm_abm.task_based_firm import TaskBasedFirm
from interfirm_abm.task_decision_rules import TaskPlan
from interfirm_abm.task_economic_policy import MarketObservation


@dataclass(frozen=True)
class ExpectedMarketState:
    expected_price: float
    expected_quantity: float | None = None

    def __post_init__(self):
        for value in (self.expected_price, self.expected_quantity):
            if value is not None and (not isfinite(value) or value < 0):
                raise ValueError("market expectations must be finite and nonnegative")


BeliefProvider = Callable[[TaskBasedFirm, MarketObservation], ExpectedMarketState]
OutputEvaluator = Callable[[TaskBasedFirm, TaskPlan], float]
CostEvaluator = Callable[[TaskBasedFirm, TaskPlan], float]


@dataclass
class BeliefBasedProfit:
    beliefs: BeliefProvider
    output: OutputEvaluator
    cost: CostEvaluator

    def __call__(
        self, firm: TaskBasedFirm, observation: MarketObservation,
        candidate_id: str, plan: TaskPlan,
    ) -> float:
        belief = self.beliefs(firm, observation)
        if not isinstance(belief, ExpectedMarketState):
            raise TypeError("belief provider must return ExpectedMarketState")
        quantity = float(self.output(firm, plan))
        cost = float(self.cost(firm, plan))
        if not isfinite(quantity) or quantity < 0 or not isfinite(cost) or cost < 0:
            raise ValueError("candidate output and cost must be finite and nonnegative")
        expected_profit = belief.expected_price * quantity - cost
        if not isfinite(expected_profit):
            raise ValueError("expected profit must be finite")
        return expected_profit

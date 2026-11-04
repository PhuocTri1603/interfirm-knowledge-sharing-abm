"""Explicit adaptive price beliefs using completed market observations only.

The smoothing coefficient and initial expectation are researcher inputs.
No learning speed, initial price, or information advantage is assumed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite

from interfirm_abm.task_based_firm import TaskBasedFirm
from interfirm_abm.task_economic_policy import MarketObservation
from interfirm_abm.task_market_beliefs import ExpectedMarketState


@dataclass
class AdaptivePriceBeliefs:
    initial_price: float
    adjustment_rate: float
    last_updated_round: dict[str, int] = field(default_factory=dict)
    current_expectation: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        if not isfinite(self.initial_price) or self.initial_price < 0:
            raise ValueError("initial expected price must be finite and nonnegative")
        if not isfinite(self.adjustment_rate) or not 0 <= self.adjustment_rate <= 1:
            raise ValueError("adjustment rate must be finite and in [0,1]")

    def __call__(
        self, firm: TaskBasedFirm, observation: MarketObservation
    ) -> ExpectedMarketState:
        key = firm.firm_id
        price = self.current_expectation.get(key, self.initial_price)
        last = self.last_updated_round.get(key, 0)
        completed = observation.round_number - 1
        if completed < last:
            raise ValueError("market observation cannot move backward")
        if completed > last:
            if observation.last_market_price is None or not isfinite(observation.last_market_price) or observation.last_market_price < 0:
                raise ValueError("completed market price required for belief update")
            if completed != last + 1:
                raise ValueError("missing intermediate market observations")
            price = (
                (1 - self.adjustment_rate) * price
                + self.adjustment_rate * observation.last_market_price
            )
            if not isfinite(price):
                raise ValueError("updated price expectation must be finite")
            self.current_expectation[key] = price
            self.last_updated_round[key] = completed
        return ExpectedMarketState(expected_price=price)

"""Game 1 economic policy contracts; no unapproved behavioral assumptions.

A strategy is an executable decision rule, not merely a label. The market
engine may use these contracts after the researcher approves production,
demand, information and cost specifications.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Callable, Mapping, Protocol


@dataclass(frozen=True)
class MarketObservation:
    round_number: int
    last_market_price: float | None
    last_market_quantity: float | None

    def __post_init__(self) -> None:
        if self.round_number < 1:
            raise ValueError("round_number must be positive")


@dataclass(frozen=True)
class PlayerState:
    player_id: str
    capital_endowment: float
    labor_endowment: float
    cumulative_profit: float = 0.0

    def __post_init__(self) -> None:
        if not self.player_id:
            raise ValueError("player_id must not be empty")
        if (not isfinite(self.capital_endowment) or not isfinite(self.labor_endowment)
                or not isfinite(self.cumulative_profit)
                or self.capital_endowment < 0 or self.labor_endowment < 0):
            raise ValueError("endowments must be nonnegative")


@dataclass(frozen=True)
class ProductionDecision:
    """Proposed resource usage; feasibility and output require a supplied model."""
    capital: float
    labor: float

    def __post_init__(self) -> None:
        if (not isfinite(self.capital) or not isfinite(self.labor)
                or self.capital < 0 or self.labor < 0):
            raise ValueError("input use must be nonnegative")


class EconomicStrategy(Protocol):
    def decide(self, player: PlayerState, observation: MarketObservation) -> ProductionDecision: ...


@dataclass(frozen=True)
class EconomicSpecification:
    """Explicitly injected technology, cost and demand; no implicit defaults."""
    output: Callable[[PlayerState, ProductionDecision], float]
    cost: Callable[[PlayerState, ProductionDecision], float]
    inverse_demand: Callable[[float], float]


def evaluate_joint_decisions(
    players: Mapping[str, PlayerState],
    decisions: Mapping[str, ProductionDecision],
    specification: EconomicSpecification,
) -> dict:
    """Evaluate one simultaneous round with a common endogenous market price.

    This evaluates externally supplied decisions; it does not claim equilibrium,
    learning, global optimization or an approved scientific calibration.
    """
    if not players or set(players) != set(decisions):
        raise ValueError("decisions must match a nonempty player roster")
    outputs: dict[str, float] = {}
    costs: dict[str, float] = {}
    for player_id, player in players.items():
        if player.player_id != player_id:
            raise ValueError("player key and ID mismatch")
        decision = decisions[player_id]
        if decision.capital > player.capital_endowment or decision.labor > player.labor_endowment:
            raise ValueError(f"infeasible resources for {player_id}")
        output = float(specification.output(player, decision))
        cost = float(specification.cost(player, decision))
        from math import isfinite
        if not isfinite(output) or output < 0 or not isfinite(cost) or cost < 0:
            raise ValueError("output and cost must be finite and nonnegative")
        outputs[player_id], costs[player_id] = output, cost
    quantity = sum(outputs.values())
    price = float(specification.inverse_demand(quantity))
    from math import isfinite
    if not isfinite(price) or price < 0:
        raise ValueError("market price must be finite and nonnegative")
    payoffs = {key: price * outputs[key] - costs[key] for key in players}
    return {
        "market_quantity": quantity,
        "market_price": price,
        "player_outputs": outputs,
        "player_costs": costs,
        "round_payoffs": payoffs,
        "execution_status": "externally_specified_decisions_not_validated_equilibrium",
    }

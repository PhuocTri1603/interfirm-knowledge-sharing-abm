"""One-market accounting with externally supplied outputs and inverse demand.

This is a neutral evaluation layer, NOT an equilibrium solver or a firm
decision rule. All firms face the same price for the same market total.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping
import math

from interfirm_abm.task_strategy_population import SharedMarketPopulation


def _nonnegative_finite(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return value


@dataclass(frozen=True)
class MarketAgentOutcome:
    agent_id: str
    base_firm_id: str
    strategy_id: str
    output: float
    total_cost: float
    revenue: float
    profit: float


@dataclass(frozen=True)
class MarketRoundOutcome:
    round_index: int
    strategy_roster: tuple[str, ...]
    total_supply: float
    common_price: float
    agents: tuple[MarketAgentOutcome, ...]

    @property
    def total_profit(self) -> float:
        return sum(agent.profit for agent in self.agents)


def evaluate_shared_market_round(
    population: SharedMarketPopulation,
    *,
    round_index: int,
    outputs: Mapping[str, float],
    total_costs: Mapping[str, float],
    inverse_demand: Callable[[float], float],
) -> MarketRoundOutcome:
    """Evaluate one given joint action profile in a shared market.

    Output and total cost for each agent are externally supplied. Inverse
    demand is injected, not calibrated or chosen here. No rationing, inventory,
    optimization, learning, market clearing or dynamic state is inferred.
    """
    if not isinstance(round_index, int) or isinstance(round_index, bool) or round_index < 0:
        raise ValueError("round_index must be a nonnegative integer")
    agent_ids = {clone.agent_id for clone in population.clones}
    if not agent_ids:
        raise ValueError("Market population cannot be empty")
    if set(outputs) != agent_ids or set(total_costs) != agent_ids:
        raise ValueError("Outputs and costs must cover exactly the market agents")
    quantities = {
        key: _nonnegative_finite(f"output for {key}", outputs[key])
        for key in agent_ids
    }
    costs = {
        key: _nonnegative_finite(f"total cost for {key}", total_costs[key])
        for key in agent_ids
    }
    supply = _nonnegative_finite("total supply", math.fsum(quantities.values()))
    price = _nonnegative_finite("common market price", inverse_demand(supply))
    agents = tuple(
        MarketAgentOutcome(
            agent_id=clone.agent_id,
            base_firm_id=clone.base_firm_id,
            strategy_id=clone.strategy_id,
            output=quantities[clone.agent_id],
            total_cost=costs[clone.agent_id],
            revenue=price * quantities[clone.agent_id],
            profit=price * quantities[clone.agent_id] - costs[clone.agent_id],
        )
        for clone in population.clones
    )
    if any(not math.isfinite(a.revenue) or not math.isfinite(a.profit) for a in agents):
        raise ValueError("Nonfinite market accounting result")
    return MarketRoundOutcome(
        round_index=round_index,
        strategy_roster=population.strategy_roster,
        total_supply=supply,
        common_price=price,
        agents=agents,
    )

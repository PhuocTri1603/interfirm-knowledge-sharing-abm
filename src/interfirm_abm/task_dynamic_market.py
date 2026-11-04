"""Dynamic 20-task allocation tournament with simultaneous shared-market pricing.

Every policy supplies a fresh allocation each round. This runner selects no
production aggregator, optimization method, or economic parameter.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Callable, Mapping, Protocol

from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm
from interfirm_abm.task_economic_policy import MarketObservation


class TaskAllocationPolicy(Protocol):
    def decide_tasks(
        self, firm: TaskBasedFirm, observation: MarketObservation
    ) -> tuple[TaskAllocation, ...]: ...


@dataclass(frozen=True)
class DynamicTaskMarket:
    firms: Mapping[str, TaskBasedFirm]
    aggregate_tasks: Callable[[Mapping[str, float]], float]
    inverse_demand: Callable[[float], float]
    capital_unit_cost: float
    labor_unit_cost: float

    def __post_init__(self) -> None:
        if not self.firms or any(k != v.firm_id for k, v in self.firms.items()):
            raise ValueError("firm roster must be nonempty and keyed by firm ID")
        for cost in (self.capital_unit_cost, self.labor_unit_cost):
            if not isfinite(cost) or cost < 0:
                raise ValueError("input unit costs must be finite and nonnegative")


def run_dynamic_task_market(
    market: DynamicTaskMarket,
    policies: Mapping[str, TaskAllocationPolicy],
    rounds: int = 200,
) -> dict:
    if rounds <= 0 or set(policies) != set(market.firms):
        raise ValueError("positive rounds and complete explicit policy roster required")
    profits = {key: 0.0 for key in market.firms}
    observation = MarketObservation(1, None, None)
    trajectory = []
    for round_number in range(1, rounds + 1):
        outputs, costs, uses = {}, {}, {}
        for key, firm in market.firms.items():
            allocation = tuple(policies[key].decide_tasks(firm, observation))
            activities = firm.evaluate_allocation(list(allocation))
            output = float(market.aggregate_tasks(activities))
            if not isfinite(output) or output < 0:
                raise ValueError("task output must be finite and nonnegative")
            capital = sum(a.capital for a in allocation)
            labor = sum(a.labor for a in allocation)
            outputs[key] = output
            uses[key] = (capital, labor)
            costs[key] = market.capital_unit_cost * capital + market.labor_unit_cost * labor
        quantity = sum(outputs.values())
        price = float(market.inverse_demand(quantity))
        if not isfinite(price) or price < 0:
            raise ValueError("market price must be finite and nonnegative")
        round_profit = 0.0
        for key in market.firms:
            payoff = price * outputs[key] - costs[key]
            if not isfinite(payoff):
                raise ValueError("payoff must be finite")
            profits[key] += payoff
            round_profit += payoff
        concentration = (
            sum((q / quantity) ** 2 for q in outputs.values()) if quantity > 0 else None
        )
        trajectory.append({
            "round": round_number,
            "market_quantity": quantity,
            "market_price": price,
            "round_total_profit": round_profit,
            "capital_used": sum(v[0] for v in uses.values()),
            "labor_used": sum(v[1] for v in uses.values()),
            "total_production_cost": sum(costs.values()),
            "output_concentration_hhi": concentration,
        })
        observation = MarketObservation(round_number + 1, price, quantity)
    ranking = sorted(
        ({"player_id": key, "total_benefit": benefit} for key, benefit in profits.items()),
        key=lambda item: (-item["total_benefit"], item["player_id"]),
    )
    for rank, item in enumerate(ranking, 1):
        item["rank"] = rank
    return {
        "rounds": rounds, "players": len(market.firms),
        "trajectory": trajectory, "ranking": ranking,
        "execution_status": "injected_task_policies_not_research_validated",
    }

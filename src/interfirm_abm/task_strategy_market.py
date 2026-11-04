"""Map strategy clones to a single dynamic task market without assigning behavior.

The 100 base firm profiles are alternative initial conditions, not a default
multiplier of strategy players. This bridge accepts one selected profile per
strategy or an explicitly supplied population; no silent cloning is done.
"""
from __future__ import annotations

from typing import Callable, Mapping

from interfirm_abm.task_based_firm import TaskBasedFirm
from interfirm_abm.task_dynamic_market import DynamicTaskMarket, TaskAllocationPolicy


def build_strategy_market(
    initial_firms: Mapping[str, TaskBasedFirm],
    *,
    aggregate_tasks: Callable,
    inverse_demand: Callable,
    capital_unit_cost: float,
    labor_unit_cost: float,
) -> DynamicTaskMarket:
    """Use one firm per strategy-player ID; reject ambiguous rosters."""
    if not initial_firms or any(key != firm.firm_id for key, firm in initial_firms.items()):
        raise ValueError("initial firms must be keyed by unique strategy-player IDs")
    return DynamicTaskMarket(
        firms=dict(initial_firms),
        aggregate_tasks=aggregate_tasks,
        inverse_demand=inverse_demand,
        capital_unit_cost=capital_unit_cost,
        labor_unit_cost=labor_unit_cost,
    )


def require_strategy_policies(
    market: DynamicTaskMarket,
    policy_factory: Callable[[str, TaskBasedFirm], TaskAllocationPolicy],
) -> dict[str, TaskAllocationPolicy]:
    """Require an explicit policy for every strategy-player; no fallback."""
    policies = {}
    for player_id, firm in market.firms.items():
        policy = policy_factory(player_id, firm)
        if not callable(getattr(policy, "decide_tasks", None)):
            raise TypeError(f"missing task decision policy for {player_id}")
        policies[player_id] = policy
    return policies

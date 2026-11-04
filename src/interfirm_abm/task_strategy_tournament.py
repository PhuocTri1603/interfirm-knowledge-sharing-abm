"""Run independent initial configurations for an explicit L1-L6 player roster.

All economic functions, initial profiles and executable task policies must be
supplied by the researcher. No policy is inferred from a strategy label.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Mapping

from interfirm_abm.task_based_firm import TaskBasedFirm
from interfirm_abm.task_dynamic_market import DynamicTaskMarket, TaskAllocationPolicy
from interfirm_abm.task_economic_export import export_dynamic_task_results
from interfirm_abm.task_policy_binding import parse_player_identity
from interfirm_abm.task_strategy_market import build_strategy_market, require_strategy_policies


def export_strategy_configuration_tournament(
    output_path: str | Path,
    initial_configurations: Mapping[str, Mapping[str, TaskBasedFirm]],
    *,
    aggregate_tasks: Callable,
    inverse_demand: Callable,
    capital_unit_cost: float,
    labor_unit_cost: float,
    policy_factory: Callable[[str, str, TaskBasedFirm], TaskAllocationPolicy],
    rounds: int = 200,
) -> dict:
    if not initial_configurations:
        raise ValueError("at least one initial configuration is required")
    expected_players = None
    markets: dict[str, DynamicTaskMarket] = {}
    for config_id, roster in initial_configurations.items():
        if not config_id or not roster:
            raise ValueError("configuration name and roster must be nonempty")
        for player_id in roster:
            parse_player_identity(player_id)
        if expected_players is None:
            expected_players = frozenset(roster)
        elif frozenset(roster) != expected_players:
            raise ValueError("each configuration must contain the same strategy players")
        markets[config_id] = build_strategy_market(
            roster,
            aggregate_tasks=aggregate_tasks,
            inverse_demand=inverse_demand,
            capital_unit_cost=capital_unit_cost,
            labor_unit_cost=labor_unit_cost,
        )

    def fresh_policies(config_id: str, market: DynamicTaskMarket):
        return require_strategy_policies(
            market,
            lambda player_id, firm: policy_factory(config_id, player_id, firm),
        )

    return export_dynamic_task_results(
        output_path, markets, fresh_policies, rounds=rounds
    )

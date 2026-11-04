"""Mixed-market benchmark: simultaneous quantity choices, one endogenous price.

Economic rationale: homogeneous-good Cournot quantity competition and
agent-based interacting markets (Tesfatsion 2006; Vives 2008). This is an
experiment design, not a claim of Cournot-Nash equilibrium.

No production, demand, cost, or learning parameters are silently chosen.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

from interfirm_abm.task_based_firm import TaskBasedFirm
from interfirm_abm.task_dynamic_market import TaskAllocationPolicy
from interfirm_abm.task_experiment_dimensions import strategy_player_ids
from interfirm_abm.task_strategy_tournament import export_strategy_configuration_tournament


@dataclass(frozen=True)
class MixedMarketSpecification:
    aggregate_tasks: Callable
    inverse_demand: Callable
    capital_unit_cost: float
    labor_unit_cost: float
    policy_factory: Callable[[str, str, TaskBasedFirm], TaskAllocationPolicy]


def run_mixed_benchmark(
    output_path,
    initial_configurations: Mapping[str, Mapping[str, TaskBasedFirm]],
    specification: MixedMarketSpecification,
    *,
    rounds: int = 200,
    require_full_experiment: bool = True,
) -> dict:
    """Run shared-price competition, with explicit inputs and fresh policies.

    Full mode requires 100 independent configurations with 3072 players each.
    Small mode is intended solely for unit/integration tests.
    """
    if require_full_experiment:
        expected_configs = {f"profile_{i:03d}" for i in range(1, 101)}
        expected_players = frozenset(strategy_player_ids())
        if set(initial_configurations) != expected_configs:
            raise ValueError("Mixed benchmark requires 100 original configuration IDs")
        if any(frozenset(roster) != expected_players for roster in initial_configurations.values()):
            raise ValueError("Mixed benchmark requires all 3072 strategy players per configuration")
    payload = export_strategy_configuration_tournament(
        output_path,
        initial_configurations,
        aggregate_tasks=specification.aggregate_tasks,
        inverse_demand=specification.inverse_demand,
        capital_unit_cost=specification.capital_unit_cost,
        labor_unit_cost=specification.labor_unit_cost,
        policy_factory=specification.policy_factory,
        rounds=rounds,
    )
    payload["market_design"] = "mixed"
    payload["benchmark_theory"] = "simultaneous_quantities_shared_inverse_demand"
    return payload

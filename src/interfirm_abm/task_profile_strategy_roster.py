"""Instantiate strategy-player rosters from original economic profiles.

Only shared endowments are transferred automatically. The task capability
mapping must be explicitly provided by the researcher because four original
production forms cannot be inferred as 20-task technologies.
"""
from __future__ import annotations

from typing import Callable, Mapping

from interfirm_abm.task_based_firm import TaskBasedFirm, TaskCapability
from interfirm_abm.task_experiment_dimensions import strategy_player_ids
from interfirm_abm.task_initial_profile_bridge import InitialEconomicProfile


def build_profile_strategy_roster(
    profile: InitialEconomicProfile,
    *,
    task_capability_factory: Callable[[InitialEconomicProfile], tuple[TaskCapability, ...]],
) -> dict[str, TaskBasedFirm]:
    if not callable(task_capability_factory):
        raise TypeError("researcher-supplied task capability factory is required")
    # Technology is fixed by configuration, never by player identity.
    tasks = tuple(task_capability_factory(profile))
    result = {}
    for strategy_id in strategy_player_ids():
        result[strategy_id] = TaskBasedFirm(
            firm_id=strategy_id,
            capital_endowment=profile.capital_endowment,
            labor_endowment=profile.labor_endowment,
            tasks=tasks,
        )
    return result


def build_profile_configuration_rosters(
    profiles: tuple[InitialEconomicProfile, ...],
    *,
    task_capability_factory: Callable[[InitialEconomicProfile, str], tuple[TaskCapability, ...]],
) -> dict[str, dict[str, TaskBasedFirm]]:
    if len(profiles) != 100 or len({p.configuration_id for p in profiles}) != 100:
        raise ValueError("exactly 100 unique initial profiles are required")
    return {
        profile.configuration_id: build_profile_strategy_roster(
            profile, task_capability_factory=task_capability_factory
        )
        for profile in profiles
    }

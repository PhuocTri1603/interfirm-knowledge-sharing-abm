"""Run a tournament only when every L1-L6 player has an explicit policy."""
from __future__ import annotations

from typing import Mapping

from interfirm_abm.task_economic_policy import EconomicStrategy
from interfirm_abm.task_economic_tournament import (
    EconomicMarketConfiguration, run_economic_sequential,
)
from interfirm_abm.task_policy_binding import validate_policy_roster


def run_registered_tournament(
    configurations: tuple[EconomicMarketConfiguration, ...],
    policies: Mapping[str, EconomicStrategy],
    rounds: int = 200,
) -> list[dict]:
    if not configurations:
        raise ValueError("at least one configuration required")
    roster = tuple(configurations[0].players)
    validate_policy_roster(roster, policies)
    for configuration in configurations[1:]:
        if set(configuration.players) != set(roster):
            raise ValueError("all configurations must use the same strategy roster")
    return run_economic_sequential(configurations, policies, rounds)

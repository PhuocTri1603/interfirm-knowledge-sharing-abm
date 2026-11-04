"""Canonical Game 1 experiment dimensions, without invented economic policies.

L3-L6 identify strategy players; L1-L2 are configuration-level technology choices; L7 identifies market design; initial profiles
are independent configurations. Counting combinations does not execute them.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Mapping

from interfirm_abm.task_layer_registry import LAYERS

STRATEGY_LAYERS = tuple(item for item in LAYERS if item[0] in ('L3', 'L4', 'L5', 'L6'))
MARKET_LAYER = next(item for item in LAYERS if item[0] == 'L7')
DEFAULT_INITIAL_CONFIGURATIONS = 100
DEFAULT_ROUNDS = 200


def strategy_player_ids() -> tuple[str, ...]:
    return tuple(
        "|".join(f"{name}={value}" for (name, _), value in zip(STRATEGY_LAYERS, options))
        for options in product(*(values for _, values in STRATEGY_LAYERS))
    )


def market_designs() -> tuple[str, ...]:
    return MARKET_LAYER[1]


@dataclass(frozen=True)
class ExperimentDimensions:
    strategy_players: int
    market_designs: int
    initial_configurations: int
    rounds_per_configuration: int

    @property
    def catalog_combinations(self) -> int:
        return self.strategy_players * self.market_designs

    @property
    def player_configuration_runs_per_design(self) -> int:
        return self.strategy_players * self.initial_configurations

    @property
    def player_round_decisions_per_design(self) -> int:
        return self.player_configuration_runs_per_design * self.rounds_per_configuration

    @property
    def player_round_decisions_all_designs(self) -> int:
        return self.player_round_decisions_per_design * self.market_designs


def experiment_dimensions(
    initial_configurations: int = DEFAULT_INITIAL_CONFIGURATIONS,
    rounds: int = DEFAULT_ROUNDS,
) -> ExperimentDimensions:
    if initial_configurations <= 0 or rounds <= 0:
        raise ValueError("configuration count and rounds must be positive")
    return ExperimentDimensions(
        len(strategy_player_ids()), len(market_designs()), initial_configurations, rounds
    )


def validate_experiment_rosters(
    configurations: Mapping[str, Mapping],
    *,
    expected_configurations: int = DEFAULT_INITIAL_CONFIGURATIONS,
    require_complete_roster: bool = True,
) -> None:
    if len(configurations) != expected_configurations:
        raise ValueError(f"expected {expected_configurations} initial configurations")
    expected = frozenset(strategy_player_ids())
    for config_id, roster in configurations.items():
        if not isinstance(config_id, str) or not config_id.strip():
            raise ValueError("configuration IDs must be nonempty")
        if require_complete_roster and frozenset(roster) != expected:
            raise ValueError("each initial configuration must contain all 256 strategy players")
        if len(roster) != len(set(roster)):
            raise ValueError("duplicate player IDs")

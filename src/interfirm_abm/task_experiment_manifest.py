"""Deterministic 100-configuration experiment manifest.

This is a schedule and identity registry, not a generator of economic
endowments, task technologies, demand curves, or executable policies.
Those require explicit researcher-supplied specifications.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Mapping

from interfirm_abm.task_experiment_dimensions import (
    DEFAULT_INITIAL_CONFIGURATIONS,
    DEFAULT_ROUNDS,
    market_designs,
    strategy_player_ids,
    validate_experiment_rosters,
)


@dataclass(frozen=True)
class ConfigurationRecord:
    configuration_id: str
    market_design: str
    rounds: int
    expected_strategy_players: int
    economic_inputs_status: str = "researcher_specification_required"


def build_experiment_manifest(
    *,
    configuration_count: int = DEFAULT_INITIAL_CONFIGURATIONS,
    rounds: int = DEFAULT_ROUNDS,
) -> dict:
    if configuration_count <= 0 or rounds <= 0:
        raise ValueError("configuration count and rounds must be positive")
    players = strategy_player_ids()
    designs = market_designs()
    records = [
        asdict(ConfigurationRecord(
            f"profile_{index:03d}", design, rounds, len(players)
        ))
        for design in designs
        for index in range(1, configuration_count + 1)
    ]
    return {
        "schema": "game1-experiment-manifest-v1",
        "status": "structure_only_no_economic_inputs",
        "strategy_players": len(players),
        "strategy_player_ids": list(players),
        "market_designs": list(designs),
        "initial_configurations_per_design": configuration_count,
        "rounds_per_configuration": rounds,
        "runs": records,
        "researcher_inputs_required": [
            "initial_task_capabilities_and_endowments",
            "task_aggregation_and_technology",
            "inverse_market_demand",
            "capital_and_labor_costs",
            "executable_strategy_policies",
            "market_design_semantics",
        ],
    }


def write_experiment_manifest(path: str | Path, **kwargs) -> dict:
    payload = build_experiment_manifest(**kwargs)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def bind_researcher_initial_configurations(
    initial_configurations: Mapping[str, Mapping],
    *,
    configuration_count: int = DEFAULT_INITIAL_CONFIGURATIONS,
) -> Mapping[str, Mapping]:
    """Validate supplied firm rosters without generating or mutating them."""
    validate_experiment_rosters(
        initial_configurations,
        expected_configurations=configuration_count,
    )
    expected_ids = {f"profile_{i:03d}" for i in range(1, configuration_count + 1)}
    if set(initial_configurations) != expected_ids:
        raise ValueError("configuration IDs must match the deterministic manifest")
    return initial_configurations

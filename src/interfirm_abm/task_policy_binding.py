"""Strict bindings between L3-L6 player identities and executable policies.

This module does not invent strategy mechanisms. It prevents a strategy label
from silently receiving a generic fallback policy.
"""
from __future__ import annotations

from typing import Mapping

from interfirm_abm.task_layer_registry import LAYERS
from interfirm_abm.task_economic_policy import EconomicStrategy

PLAYER_LAYERS = tuple(name for name, _ in LAYERS if name in ("L3", "L4", "L5", "L6"))
PLAYER_OPTIONS = {name: frozenset(options) for name, options in LAYERS if name != "L7"}


def parse_player_identity(player_id: str) -> dict[str, str]:
    if not isinstance(player_id, str):
        raise ValueError("player ID must be a string")
    components = player_id.split("|")
    if len(components) != len(PLAYER_LAYERS):
        raise ValueError("player identity must specify L3-L6 exactly once")
    choices: dict[str, str] = {}
    for component in components:
        if component.count("=") != 1:
            raise ValueError("invalid player identity component")
        layer, option = component.split("=", 1)
        if layer not in PLAYER_OPTIONS or layer in choices or option not in PLAYER_OPTIONS[layer]:
            raise ValueError("unknown or repeated player layer/option")
        choices[layer] = option
    if set(choices) != set(PLAYER_LAYERS):
        raise ValueError("missing player layer")
    return choices


def validate_policy_roster(
    player_ids: tuple[str, ...], policies: Mapping[str, EconomicStrategy]
) -> None:
    if not player_ids or len(set(player_ids)) != len(player_ids):
        raise ValueError("player roster must be nonempty and unique")
    for player_id in player_ids:
        parse_player_identity(player_id)
    if set(player_ids) != set(policies):
        raise ValueError("all player IDs require explicit policies; no fallback allowed")
    for player_id, policy in policies.items():
        if not callable(getattr(policy, "decide", None)):
            raise ValueError(f"policy for {player_id} lacks decide()")

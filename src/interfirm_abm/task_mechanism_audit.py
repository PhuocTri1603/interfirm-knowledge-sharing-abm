"""Research-readiness audit for the mixed-market strategy tournament.

Rejects an apparently complete tournament where all strategy labels receive
the same behavior/technology, or where initial conditions differ within a
configuration. This is a structural audit, not proof of economic validity.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from math import isclose
from typing import Mapping

from interfirm_abm.task_based_firm import TaskBasedFirm
from interfirm_abm.task_policy_binding import parse_player_identity


@dataclass(frozen=True)
class PlayerMechanism:
    """Researcher-declared executable mechanism IDs, not strategy labels."""
    production_mechanism: str
    decision_mechanism: str
    information_mechanism: str


def audit_mixed_configuration(
    firms: Mapping[str, TaskBasedFirm],
    mechanisms: Mapping[str, PlayerMechanism],
    *,
    expected_players: int = 256,
) -> dict:
    if len(firms) != expected_players or set(firms) != set(mechanisms):
        raise ValueError("complete firm and mechanism rosters required")
    by_layer = defaultdict(lambda: defaultdict(set))
    capitals = set()
    labors = set()
    for player_id, firm in firms.items():
        if firm.firm_id != player_id:
            raise ValueError("firm identity must equal strategy identity")
        choices = parse_player_identity(player_id)
        mechanism = mechanisms[player_id]
        if not all((mechanism.production_mechanism, mechanism.decision_mechanism,
                    mechanism.information_mechanism)):
            raise ValueError("mechanism IDs cannot be blank")
        capitals.add(firm.capital_endowment)
        labors.add(firm.labor_endowment)
        for layer, option in choices.items():
            by_layer[layer][option].add((
                mechanism.production_mechanism,
                mechanism.decision_mechanism,
                mechanism.information_mechanism,
            ))
    if len(capitals) != 1 or len(labors) != 1:
        raise ValueError("mixed benchmark requires common initial K and L")
    signatures = {(
        mechanism.production_mechanism,
        mechanism.decision_mechanism,
        mechanism.information_mechanism,
    ) for mechanism in mechanisms.values()}
    if len(signatures) == 1:
        raise ValueError("all strategies have identical declared mechanisms")
    return {
        "players": len(firms),
        "unique_mechanism_signatures": len(signatures),
        "common_initial_capital": next(iter(capitals)),
        "common_initial_labor": next(iter(labors)),
        "layer_option_counts": {
            layer: {option: len(values) for option, values in options.items()}
            for layer, options in by_layer.items()
        },
        "status": "structural_audit_only_not_research_validated",
    }

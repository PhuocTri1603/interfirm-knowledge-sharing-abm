"""A5 technology wired into the EXISTING DIAGNOSTIC market, not validated A6.

The normalized output index is temporarily treated as an offer quantity by
the legacy illustrative clearing rule. Prices/profits are NOT economically
interpretable until the researcher approves an A6 unit convention.
"""
from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
from random import Random

from interfirm_abm.task_a5_normalized import paired_technologies
from interfirm_abm.task_multi_action_diagnostic import configurations, market_factory, ROSTER
from interfirm_abm.task_strategy_actions import build_actions, score_action
from interfirm_abm.task_strategy_engine import ComposedStrategyPolicy, DecisionParameters
from interfirm_abm.task_mixed_market import run_mixed_market


def run_a5_diagnostic(config_id: str, sigma: float, *, rounds: int = 2, roster=None):
    """Return diagnostic market trajectories; never label them validated profit."""
    if rounds < 1:
        raise ValueError("rounds must be positive")
    if not config_id.startswith("C") or not config_id[1:].isdigit():
        raise ValueError("invalid configuration ID")
    index = int(config_id[1:])
    if not 0 <= index < 100:
        raise ValueError("configuration index outside C000..C099")
    if roster is None:
        roster = configurations(index + 1)[config_id]
    first_firm = next(iter(roster.values()))
    treatments = paired_technologies(first_firm)
    if sigma not in treatments:
        raise ValueError("sigma must be one of the approved scenarios")
    tech = treatments[sigma]
    # Preserve same profile, strategy roster, and legacy diagnostic clearing
    # across sigma variants. A6 conversion is intentionally NOT invented.
    market = replace(market_factory(config_id, roster), aggregate_tasks=tech.output_index)
    policies = {}

    for identity in ROSTER:
        seed = int.from_bytes(sha256(
            f"{config_id}|{identity.strategy_id}|a5-paired".encode()
        ).digest()[:8], "big")
        policies[identity.strategy_id] = ComposedStrategyPolicy(
            identity, build_actions,
            lambda ident, firm, info, action, agg=tech.output_index:
                score_action(ident, firm, info, action, agg),
            DecisionParameters(.15, 1.), Random(seed),
        )
    result = run_mixed_market(market, policies, rounds)
    result.update({
        "config_id": config_id, "sigma": sigma,
        "production_measure": "dimensionless_within_configuration_index",
        "economic_validation": "NOT_VALIDATED_A6_DIAGNOSTIC_ONLY",
        "research_validated": False,
    })
    return result

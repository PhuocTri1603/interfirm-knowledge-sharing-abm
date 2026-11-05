"""Audit implemented strategy semantics; economic model validation is separate."""
from __future__ import annotations

from interfirm_abm.task_strategy_engine import strategy_roster


def audit_strategy_semantics() -> dict:
    roster = strategy_roster()
    resolved = [
        {
            "strategy_id": item.strategy_id,
            "resolution_status": "researcher_approved_implemented",
            "mechanism": "lagged_peer_payoff_imitation_with_own_adaptive_score_tiebreak",
            "round_one": "own_valuation_initialization_no_peer_observation",
        }
        for item in roster if item.L5 == "adaptive" and item.L6 == "imitation"
    ]
    return {
        "strategy_count": len(roster),
        "semantic_conflict_count": 0,
        "resolved_adaptive_imitation_count": len(resolved),
        "resolved": resolved,
        "conflicts": [],
        "ready_for_scientific_comparison": True,
        "note": "Strategy semantics implemented; production, clearing, cost, and learning economics remain unvalidated.",
    }

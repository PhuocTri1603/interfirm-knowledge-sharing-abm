"""Preflight audit of Game 1 strategy semantics before scientific simulation.

A catalog entry is not proof that its mechanism is implemented. In particular,
adaptive behavior is own-history only, while imitation ordinarily needs peers.
"""
from __future__ import annotations

from interfirm_abm.task_strategy_engine import strategy_roster


def audit_strategy_semantics() -> dict:
    roster = strategy_roster()
    conflicts = [
        {
            "strategy_id": item.strategy_id,
            "issue": "adaptive_own_history_vs_peer_imitation",
            "resolution_status": "requires_researcher_decision",
            "current_engine_behavior": "own_score_optimization_fallback_not_peer_imitation",
        }
        for item in roster if item.L5 == "adaptive" and item.L6 == "imitation"
    ]
    return {
        "strategy_count": len(roster),
        "semantic_conflict_count": len(conflicts),
        "conflicts": conflicts,
        "ready_for_scientific_comparison": not conflicts,
        "note": "A working diagnostic simulation does not establish strategy-mechanism validity.",
    }

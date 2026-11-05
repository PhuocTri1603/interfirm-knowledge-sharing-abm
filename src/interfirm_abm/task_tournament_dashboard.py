"""Convert injected Game 1 tournament records to the existing static dashboard schema.

Explicitly diagnostic: no publication, scientific validation, or economic
mechanisms are implied by this serialization layer.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Mapping


def tournament_dashboard_payload(result: Mapping, *, max_configurations: int | None = None) -> dict:
    if result.get("execution_status") != "economic_models_injected_not_research_validated":
        raise ValueError("unsupported provenance status")
    n = result["configuration_count"]
    rounds = result["rounds_per_configuration"]
    players = result["strategy_count"]
    if any(type(x) is not int or x <= 0 for x in (n, rounds, players)):
        raise ValueError("invalid tournament dimensions")
    if max_configurations is not None and (type(max_configurations) is not int or max_configurations <= 0):
        raise ValueError("max_configurations must be a positive integer")
    selected = [s["config_id"] for s in result["configuration_summaries"]]
    if len(selected) != n or len(set(selected)) != n:
        raise ValueError("configuration IDs must be unique")
    selected = selected[:max_configurations]
    market = defaultdict(list)
    player = defaultdict(list)
    ranks = defaultdict(list)
    for row in result["market_trajectory"]:
        market[row["config_id"]].append(row)
    for row in result["player_trajectory"]:
        player[row["config_id"]].append(row)
    for row in result["ranking_by_configuration"]:
        ranks[row["config_id"]].append(row)
    if set(market) != set(s["config_id"] for s in result["configuration_summaries"]) or set(player) != set(market) or set(ranks) != set(market):
        raise ValueError("inconsistent configuration coverage")
    configurations = []
    for config_id in selected:
        m = sorted(market[config_id], key=lambda r: r["round"])
        p = sorted(player[config_id], key=lambda r: (r["round"], r["player_id"]))
        ranking = sorted(ranks[config_id], key=lambda r: r["rank"])
        if [r["round"] for r in m] != list(range(1, rounds + 1)):
            raise ValueError("market rounds missing or duplicated")
        if len(p) != rounds * players or len(ranking) != players:
            raise ValueError("player or ranking count mismatch")
        if len({r["player_id"] for r in ranking}) != players:
            raise ValueError("duplicate ranking player IDs")
        if {r["player_id"] for r in p} != {r["player_id"] for r in ranking}:
            raise ValueError("trajectory and ranking rosters differ")
        if len({(r["round"], r["player_id"]) for r in p}) != len(p):
            raise ValueError("duplicate player-round records")
        if any(r["average_transaction_price"] is None for r in m):
            raise ValueError("price chart requires nonempty transactions every round")
        configurations.append({
            "id": config_id,
            "price_trajectory": [{"round": r["round"], "price": r["average_transaction_price"]} for r in m],
            "top_10": [{"rank": r["rank"], "player_id": r["player_id"], "total_benefit": r["total_benefit"]} for r in ranking[:10]],
            "player_trajectory": [
                {"round": r["round"], "player_id": r["player_id"],
                 "cumulative_profit": r["cumulative_profit"], "round_profit": r["round_profit"],
                 "output": r["produced_quantity"], "capital_used": r["capital_used"],
                 "labor_used": r["labor_used"]}
                for r in p
            ],
        })
    return {
        "status": "externally_injected_policies_not_research_validated",
        "warning": "ILLUSTRATIVE / EXTERNALLY INJECTED MODEL ONLY. No strategy winners or economic findings are established.",
        "players": players,
        "rounds": rounds,
        "configurations": configurations,
        "total_initial_configurations": n,
        "preview_only": len(configurations) != n,
    }


def write_tournament_dashboard(result: Mapping, path: str | Path, *, max_configurations: int | None = None) -> Path:
    payload = tournament_dashboard_payload(result, max_configurations=max_configurations)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, allow_nan=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return path

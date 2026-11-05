"""Deterministic Game 1 tournament exports for downstream dashboards.

These files expose the injected-model outputs without asserting research validity.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Mapping

TABLES = {
    "configuration_summaries": ("config_id", "players", "rounds", "market_total_profit", "highest_ranked_player"),
    "market_trajectory": ("config_id", "round", "quantity_sold", "quantity_produced", "total_revenue", "total_cost", "total_profit", "average_transaction_price"),
    "player_trajectory": ("config_id", "round", "player_id", "action_id", "offered_price", "produced_quantity", "sold_quantity", "realized_unit_price", "revenue", "capital_used", "labor_used", "production_and_extra_cost", "round_profit", "cumulative_profit"),
    "ranking_by_configuration": ("config_id", "player_id", "total_benefit", "rank"),
}


def export_tournament(result: Mapping, directory: str | Path, *, overwrite: bool = False) -> dict[str, Path]:
    """Write four machine-readable tables and explicit provenance metadata.

    Refuses to overwrite by default and validates the full row schema before
    creating any file. No inferred economic findings or statistical claims.
    """
    if result.get("execution_status") != "economic_models_injected_not_research_validated":
        raise ValueError("unexpected execution status; export requires explicit provenance")
    tables = {}
    for name, columns in TABLES.items():
        rows = result.get(name)
        if not isinstance(rows, list):
            raise ValueError(f"{name} must be a list")
        for row in rows:
            if not isinstance(row, dict) or set(row) != set(columns):
                raise ValueError(f"{name} has invalid column schema")
        tables[name] = rows
    n_config = result.get("configuration_count")
    n_players = result.get("strategy_count")
    n_rounds = result.get("rounds_per_configuration")
    if not all(type(x) is int and x > 0 for x in (n_config, n_players, n_rounds)):
        raise ValueError("invalid experiment dimensions")
    if len(tables["configuration_summaries"]) != n_config:
        raise ValueError("configuration summary count mismatch")
    if len(tables["market_trajectory"]) != n_config * n_rounds:
        raise ValueError("market trajectory count mismatch")
    if len(tables["player_trajectory"]) != n_config * n_players * n_rounds:
        raise ValueError("player trajectory count mismatch")
    if len(tables["ranking_by_configuration"]) != n_config * n_players:
        raise ValueError("ranking count mismatch")
    directory = Path(directory)
    names = [f"{name}.csv" for name in TABLES] + ["manifest.json"]
    if directory.exists() and not overwrite and any((directory / name).exists() for name in names):
        raise FileExistsError("output files exist; use overwrite=True explicitly")
    directory.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for name, columns in TABLES.items():
        path = directory / f"{name}.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            writer.writerows(tables[name])
        outputs[name] = path
    manifest = {
        "schema_version": "game1-tournament-v1",
        "execution_status": result["execution_status"],
        "research_validated": False,
        "configuration_count": n_config,
        "strategy_count": n_players,
        "rounds_per_configuration": n_rounds,
        "player_round_observations": len(tables["player_trajectory"]),
        "tables": {name: {"file": f"{name}.csv", "rows": len(rows)} for name, rows in tables.items()},
        "warning": "Injected economic specifications may be illustrative. Do not report as research findings without approval and validation.",
    }
    manifest_path = directory / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    outputs["manifest"] = manifest_path
    return outputs

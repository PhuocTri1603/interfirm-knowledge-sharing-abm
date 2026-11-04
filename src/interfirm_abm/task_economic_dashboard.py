"""Convert validated economic tournament outputs to dashboard-ready records.

No synthetic rankings or proxy prices are manufactured here. Callers must
provide results from the injected-policy economic tournament.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping, Sequence


def economic_dashboard_payload(results: Sequence[Mapping]) -> dict:
    if not results:
        raise ValueError("economic results must be nonempty")
    configurations = []
    seen = set()
    for result in results:
        config_id = result["config_id"]
        if config_id in seen:
            raise ValueError("duplicate configuration ID")
        seen.add(config_id)
        if result.get("execution_status") not in (
            "injected_policies_not_research_validated",
            "injected_task_policies_not_research_validated",
        ):
            raise ValueError("unsupported economic result status")
        trajectory = result["trajectory"]
        ranking = result["ranking"]
        if len(trajectory) != result["rounds"] or len(ranking) != result["players"]:
            raise ValueError("incomplete tournament result")
        configurations.append({
            "id": config_id,
            "price_trajectory": [
                {"round": point["round"], "price": point["market_price"],
                 "market_quantity": point["market_quantity"],
                 "capital_used": point["capital_used"],
                 "labor_used": point["labor_used"],
                 "total_production_cost": point["total_production_cost"],
                 "output_concentration_hhi": point["output_concentration_hhi"]}
                for point in trajectory
            ],
            "top_10": ranking[:10],
            "total_market_benefit": sum(row["total_benefit"] for row in ranking),
            "note": "Externally injected policies; not a calibrated or validated research result.",
        })
    if len({r["players"] for r in results}) != 1 or len({r["rounds"] for r in results}) != 1:
        raise ValueError("dashboard requires a common player count and round horizon")
    return {
        "status": "externally_injected_policies_not_research_validated",
        "warning": "Economic functions and policies are externally supplied; no research superiority is established.",
        "rounds": results[0]["rounds"],
        "players": results[0]["players"],
        "configurations": configurations,
    }


def write_economic_dashboard(path: Path, results: Sequence[Mapping]) -> dict:
    payload = economic_dashboard_payload(results)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return payload

"""Strict structural checks for economic dashboard tournament payloads.

These checks establish completeness and accounting consistency, not scientific
validity of externally selected economic assumptions.
"""
from __future__ import annotations

from math import isclose, isfinite
from typing import Mapping


def validate_economic_dashboard(
    data: Mapping,
    *,
    expected_players: int = 3072,
    expected_rounds: int = 200,
    expected_configurations: int | None = None,
) -> None:
    if data.get("status") != "externally_injected_policies_not_research_validated":
        raise ValueError("dashboard is not marked as unvalidated economic data")
    if data.get("players") != expected_players or data.get("rounds") != expected_rounds:
        raise ValueError("unexpected strategy player count or round horizon")
    configurations = data.get("configurations")
    if not isinstance(configurations, list) or not configurations:
        raise ValueError("missing configurations")
    if expected_configurations is not None and len(configurations) != expected_configurations:
        raise ValueError("unexpected configuration count")
    names = set()
    for config in configurations:
        name = config.get("id")
        if not isinstance(name, str) or not name or name in names:
            raise ValueError("configuration IDs must be nonempty and unique")
        names.add(name)
        trajectory = config.get("price_trajectory")
        if not isinstance(trajectory, list) or len(trajectory) != expected_rounds:
            raise ValueError("incomplete price trajectory")
        for index, point in enumerate(trajectory, start=1):
            if point.get("round") != index:
                raise ValueError("round sequence must be consecutive from one")
            for field in ("price", "market_quantity", "capital_used",
                          "labor_used", "total_production_cost"):
                value = point.get(field)
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value < 0:
                    raise ValueError(f"invalid {field} in round {index}")
            hhi = point.get("output_concentration_hhi")
            if hhi is not None and (
                isinstance(hhi, bool) or not isinstance(hhi, (int, float))
                or not isfinite(hhi) or not 0 <= hhi <= 1 + 1e-9
            ):
                raise ValueError("invalid output concentration")
        top = config.get("top_10")
        if not isinstance(top, list) or len(top) != min(10, expected_players):
            raise ValueError("incomplete top ten")
        seen_players = set()
        previous = None
        for rank, item in enumerate(top, start=1):
            if item.get("rank") != rank:
                raise ValueError("nonconsecutive ranking")
            player = item.get("player_id")
            benefit = item.get("total_benefit")
            if not isinstance(player, str) or not player or player in seen_players:
                raise ValueError("duplicate or invalid player ID")
            seen_players.add(player)
            if isinstance(benefit, bool) or not isinstance(benefit, (int, float)) or not isfinite(benefit):
                raise ValueError("nonfinite benefit")
            if previous is not None and benefit > previous + 1e-9:
                raise ValueError("top ten not sorted by benefit")
            previous = benefit
        total = config.get("total_market_benefit")
        if isinstance(total, bool) or not isinstance(total, (int, float)) or not isfinite(total):
            raise ValueError("invalid total market benefit")

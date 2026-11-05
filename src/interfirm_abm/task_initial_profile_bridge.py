"""Bind the 100 original economic-firm profiles to Game 1 configuration IDs.

Each source CSV row defines a shared initial economic environment for all
L1-L6 strategies. This module does NOT duplicate firms into players or infer
how L7 market-design labels change competition.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from interfirm_abm.task_experiment_dimensions import DEFAULT_INITIAL_CONFIGURATIONS


@dataclass(frozen=True)
class InitialEconomicProfile:
    configuration_id: str
    source_firm_id: int
    technology: str
    productivity_A: float
    alpha: float | None
    kappa: float | None
    rho: float | None
    capital_endowment: float
    labor_endowment: float
    cash: float
    profile_status: str


def _optional_float(value: str | None) -> float | None:
    return None if value is None or value.strip() == "" else float(value)


def load_initial_economic_profiles(
    csv_path: str | Path, *, expected_count: int = DEFAULT_INITIAL_CONFIGURATIONS
) -> tuple[InitialEconomicProfile, ...]:
    with Path(csv_path).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != expected_count:
        raise ValueError(f"expected {expected_count} original firm profiles")
    profiles = []
    seen = set()
    for row in rows:
        firm_id = int(row["firm_id"])
        if firm_id in seen or not 1 <= firm_id <= expected_count:
            raise ValueError("source firm IDs must be unique and in range")
        seen.add(firm_id)
        profiles.append(InitialEconomicProfile(
            configuration_id=f"profile_{firm_id:03d}",
            source_firm_id=firm_id,
            technology=row["technology"],
            productivity_A=float(row["productivity_A"]),
            alpha=_optional_float(row["alpha"]),
            kappa=_optional_float(row["kappa"]),
            rho=_optional_float(row["rho"]),
            capital_endowment=float(row["capital_endowment"]),
            labor_endowment=float(row["labor_endowment"]),
            cash=float(row["cash"]),
            profile_status=row["profile_status"],
        ))
    if seen != set(range(1, expected_count + 1)):
        raise ValueError("missing source firm IDs")
    return tuple(sorted(profiles, key=lambda item: item.source_firm_id))

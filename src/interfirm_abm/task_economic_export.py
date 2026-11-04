"""Export independently supplied dynamic task-market results for the website.

No default production technology, policy, demand curve or synthetic results.
Call this only after an explicitly specified scenario has been executed.
"""
from __future__ import annotations

from pathlib import Path
from typing import Mapping, Callable

from interfirm_abm.task_dynamic_market import (
    DynamicTaskMarket, TaskAllocationPolicy, run_dynamic_task_scenarios,
)
from interfirm_abm.task_economic_dashboard import write_economic_dashboard


def export_dynamic_task_results(
    output_path: str | Path,
    configurations: Mapping[str, DynamicTaskMarket],
    policy_factory: Callable[
        [str, DynamicTaskMarket], Mapping[str, TaskAllocationPolicy]
    ],
    rounds: int = 200,
) -> dict:
    results = run_dynamic_task_scenarios(configurations, policy_factory, rounds)
    return write_economic_dashboard(Path(output_path), results)

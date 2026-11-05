"""Task-based production feasibility for the approved 100-firm population.

Task execution follows an Acemoglu–Restrepo-inspired pure-mode baseline:
one task uses labor or eligible capital, never both simultaneously.
Task aggregation, optimal choice, and AI adoption remain separate layers.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
import math


def _nonnegative(name: str, value: float) -> None:
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and nonnegative")


@dataclass(frozen=True)
class TaskCapability:
    task_id: str
    labor_productivity: float
    capital_productivity: float
    automation_eligible: bool

    def __post_init__(self):
        for name in ("labor_productivity", "capital_productivity"):
            value = getattr(self, name)
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and positive")


@dataclass(frozen=True)
class TaskAllocation:
    task_id: str
    labor: float
    capital: float

    def __post_init__(self):
        _nonnegative("labor", self.labor)
        _nonnegative("capital", self.capital)


@dataclass(frozen=True)
class TaskBasedFirm:
    firm_id: str
    capital_endowment: float
    labor_endowment: float
    tasks: tuple[TaskCapability, ...]

    def __post_init__(self):
        _nonnegative("capital_endowment", self.capital_endowment)
        _nonnegative("labor_endowment", self.labor_endowment)
        ids = [task.task_id for task in self.tasks]
        if len(ids) != 20 or len(set(ids)) != 20:
            raise ValueError("Each approved firm must have 20 distinct tasks")
        if set(ids) != {f"T{j:02d}" for j in range(1, 21)}:
            raise ValueError("Task identifiers must be T01 through T20")

    def evaluate_allocation(self, allocations: list[TaskAllocation]) -> dict[str, float]:
        """Check input feasibility and return task activity, not final output.

        Within a task, activity = a_L * L + a_K * K when automation is
        eligible. This is a provisional accounting convention, NOT an
        approved economic production function or task aggregator.
        """
        if len(allocations) != 20 or len({a.task_id for a in allocations}) != 20:
            raise ValueError("Exactly one allocation per task is required")
        capabilities = {t.task_id: t for t in self.tasks}
        used_labor = used_capital = 0.0
        activity: dict[str, float] = {}
        for allocation in allocations:
            if allocation.task_id not in capabilities:
                raise ValueError(f"Unknown task: {allocation.task_id}")
            task = capabilities[allocation.task_id]
            if allocation.capital > 0 and allocation.labor > 0:
                raise ValueError(f"Simultaneous labor and capital prohibited for {task.task_id}")
            if allocation.capital > 0 and not task.automation_eligible:
                raise ValueError(f"Automation not eligible for {task.task_id}")
            used_labor += allocation.labor
            used_capital += allocation.capital
            activity[allocation.task_id] = (
                task.labor_productivity * allocation.labor
                + task.capital_productivity * allocation.capital
            )
        if used_labor > self.labor_endowment + 1e-9:
            raise ValueError("Labor allocation exceeds endowment")
        if used_capital > self.capital_endowment + 1e-9:
            raise ValueError("Capital allocation exceeds endowment")
        return activity


def load_approved_population(profiles_csv: str | Path, tasks_csv: str | Path) -> list[TaskBasedFirm]:
    """Read the approved GitHub CSV schema; reject incomplete populations."""
    with open(profiles_csv, encoding="utf-8-sig", newline="") as f:
        profiles = list(csv.DictReader(f))
    with open(tasks_csv, encoding="utf-8-sig", newline="") as f:
        task_rows = list(csv.DictReader(f))
    grouped: dict[str, list[TaskCapability]] = {}
    for row in task_rows:
        flag = row["Automation eligible"]
        if flag not in ("0", "1"):
            raise ValueError("Automation eligible must be 0 or 1")
        grouped.setdefault(row["Firm ID"], []).append(TaskCapability(
            task_id=row["Task ID"],
            labor_productivity=float(row["Labor productivity"]),
            capital_productivity=float(row["Potential capital productivity"]),
            automation_eligible=flag == "1",
        ))
    firms = [
        TaskBasedFirm(
            firm_id=row["Firm ID"],
            capital_endowment=float(row["Capital K"]),
            labor_endowment=float(row["Labor L"]),
            tasks=tuple(grouped.get(row["Firm ID"], [])),
        )
        for row in profiles
    ]
    if len(firms) != 100 or len({f.firm_id for f in firms}) != 100:
        raise ValueError("Approved population must contain exactly 100 unique firms")
    if set(grouped) != {f.firm_id for f in firms} or len(task_rows) != 2000:
        raise ValueError("Task records must match the 100 approved firms")
    return firms

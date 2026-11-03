"""Tests for the task-based production feasibility layer."""
import csv
from pathlib import Path
import pytest

from interfirm_abm.task_based_firm import (
    TaskAllocation, TaskBasedFirm, TaskCapability, load_approved_population,
)


ROOT = Path(__file__).resolve().parents[1]


def population():
    return load_approved_population(
        ROOT / "data/firms/task_based_100_firms_profiles.csv",
        ROOT / "data/firms/task_based_100_firms_tasks.csv",
    )


def test_approved_population_shape():
    firms = population()
    assert len(firms) == 100
    assert sum(len(f.tasks) for f in firms) == 2000
    assert all(2 <= sum(t.automation_eligible for t in f.tasks) <= 12 for f in firms)


def test_zero_allocation_feasible():
    firm = population()[0]
    result = firm.evaluate_allocation(
        [TaskAllocation(t.task_id, 0.0, 0.0) for t in firm.tasks]
    )
    assert len(result) == 20
    assert all(value == 0 for value in result.values())


def test_labor_activity_accounting():
    firm = population()[0]
    first = firm.tasks[0]
    allocations = [TaskAllocation(t.task_id, 1.0 if t == first else 0.0, 0.0)
                   for t in firm.tasks]
    result = firm.evaluate_allocation(allocations)
    assert result[first.task_id] == pytest.approx(first.labor_productivity)


def test_automation_constraint():
    firm = population()[0]
    blocked = next(t for t in firm.tasks if not t.automation_eligible)
    allocations = [TaskAllocation(t.task_id, 0.0, 1.0 if t == blocked else 0.0)
                   for t in firm.tasks]
    with pytest.raises(ValueError, match="not eligible"):
        firm.evaluate_allocation(allocations)


def test_endowment_constraint():
    firm = population()[0]
    allocations = [TaskAllocation(t.task_id, firm.labor_endowment + 1 if j == 0 else 0, 0)
                   for j, t in enumerate(firm.tasks)]
    with pytest.raises(ValueError, match="Labor"):
        firm.evaluate_allocation(allocations)


def test_duplicate_task_allocation_rejected():
    firm = population()[0]
    allocations = [TaskAllocation(firm.tasks[0].task_id, 0, 0) for _ in range(20)]
    with pytest.raises(ValueError, match="Exactly one"):
        firm.evaluate_allocation(allocations)

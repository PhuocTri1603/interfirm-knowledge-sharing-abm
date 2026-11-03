"""Shared-resource bundle tests. No task choice is interpreted as optimal."""
import pytest

from interfirm_abm.task_based_firm import TaskBasedFirm, TaskCapability
from interfirm_abm.task_execution import TaskUnitCosts
from interfirm_abm.task_bundle import TaskChoice, evaluate_task_bundle, feasible_allocations


def firm(k=10, l=10):
    return TaskBasedFirm(
        "FTEST", k, l,
        tuple(TaskCapability(f"T{j:02d}", 1, 2, j <= 5) for j in range(1, 21))
    )


def choices(mode="labor", q=0):
    return [TaskChoice(f"T{j:02d}", mode if j <= 5 else "labor", q)
            for j in range(1, 21)]


def test_zero_bundle_feasible():
    result = evaluate_task_bundle(firm(), choices(), prices=TaskUnitCosts(3, 2))
    assert result.feasible
    assert result.variable_cost == 0
    assert len(feasible_allocations(result)) == 20


def test_shared_labor_limit():
    result = evaluate_task_bundle(firm(), choices(q=1), prices=TaskUnitCosts(3, 2))
    assert not result.feasible
    assert result.violations == ("labor_endowment_exceeded",)
    with pytest.raises(ValueError, match="infeasible"):
        feasible_allocations(result)


def test_capital_quote_and_resource_limit():
    selection = choices()
    selection[0] = TaskChoice("T01", "capital", 8)
    result = evaluate_task_bundle(firm(k=3), selection, prices=TaskUnitCosts(3, 2))
    assert result.capital_used == pytest.approx(4)
    assert not result.feasible
    assert "capital_endowment_exceeded" in result.violations


def test_feasible_bundle_reconciles_with_firm_activity():
    selection = choices()
    selection[0] = TaskChoice("T01", "capital", 4)
    selection[5] = TaskChoice("T06", "labor", 3)
    target = firm()
    result = evaluate_task_bundle(target, selection, prices=TaskUnitCosts(3, 2))
    assert result.feasible
    activities = target.evaluate_allocation(feasible_allocations(result))
    assert activities["T01"] == pytest.approx(4)
    assert activities["T06"] == pytest.approx(3)
    assert result.variable_cost == pytest.approx(13)


def test_missing_or_duplicate_task_rejected():
    with pytest.raises(ValueError, match="Exactly one"):
        evaluate_task_bundle(firm(), choices()[:-1], prices=TaskUnitCosts(1, 1))


def test_ineligible_capital_rejected():
    selection = choices()
    selection[9] = TaskChoice("T10", "capital", 1)
    with pytest.raises(ValueError, match="not eligible"):
        evaluate_task_bundle(firm(), selection, prices=TaskUnitCosts(1, 1))

"""Tests for task execution cost quotations, not behavioral assumptions."""
import pytest

from interfirm_abm.task_based_firm import TaskCapability
from interfirm_abm.task_execution import (
    TaskUnitCosts, compare_pure_task_modes, quote_pure_task_mode,
)


def test_labor_quote():
    task = TaskCapability("T01", 2.0, 4.0, True)
    quote = quote_pure_task_mode(
        task, mode="labor", target_activity=8.0, prices=TaskUnitCosts(3.0, 5.0)
    )
    assert quote.required_labor == pytest.approx(4.0)
    assert quote.required_capital == 0.0
    assert quote.variable_cost == pytest.approx(12.0)


def test_capital_quote():
    task = TaskCapability("T01", 2.0, 4.0, True)
    quote = quote_pure_task_mode(
        task, mode="capital", target_activity=8.0, prices=TaskUnitCosts(3.0, 5.0)
    )
    assert quote.required_capital == pytest.approx(2.0)
    assert quote.variable_cost == pytest.approx(10.0)


def test_automation_eligibility_enforced():
    task = TaskCapability("T02", 2.0, 4.0, False)
    with pytest.raises(ValueError, match="not eligible"):
        quote_pure_task_mode(
            task, mode="capital", target_activity=1, prices=TaskUnitCosts(3, 5)
        )
    result = compare_pure_task_modes(task, target_activity=1, prices=TaskUnitCosts(3, 5))
    assert result["capital"] is None
    assert result["labor_minus_capital_cost"] is None


def test_cost_difference_is_not_adoption_decision():
    task = TaskCapability("T01", 2.0, 4.0, True)
    result = compare_pure_task_modes(
        task, target_activity=8, prices=TaskUnitCosts(3, 5)
    )
    assert result["labor_minus_capital_cost"] == pytest.approx(2.0)


def test_zero_activity():
    task = TaskCapability("T01", 1.0, 1.0, True)
    result = compare_pure_task_modes(
        task, target_activity=0, prices=TaskUnitCosts(1, 1)
    )
    assert result["labor"].variable_cost == 0
    assert result["capital"].variable_cost == 0


def test_negative_prices_and_activity_rejected():
    with pytest.raises(ValueError):
        TaskUnitCosts(-1, 1)
    task = TaskCapability("T01", 1, 1, True)
    with pytest.raises(ValueError):
        quote_pure_task_mode(
            task, mode="labor", target_activity=-1, prices=TaskUnitCosts(1, 1)
        )

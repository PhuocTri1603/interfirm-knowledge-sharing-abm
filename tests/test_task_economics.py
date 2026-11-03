"""Accounting identities and validation without choosing a task aggregator."""
import pytest

from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm, TaskCapability
from interfirm_abm.task_economics import EconomicPrices, evaluate_task_plan


def firm():
    return TaskBasedFirm("FTEST", 10.0, 20.0, tuple(
        TaskCapability(f"T{j:02d}", 1.0, 1.0, j <= 5)
        for j in range(1, 21)
    ))


def plan():
    return [TaskAllocation(f"T{j:02d}", 2.0 if j == 1 else 0.0,
                           3.0 if j == 2 else 0.0) for j in range(1, 21)]


def test_accounting_identity_with_explicit_test_aggregator():
    # The sum below is a TEST STUB, not an approved production aggregator.
    result = evaluate_task_plan(
        firm(), plan(), aggregate_tasks=lambda activities: sum(activities.values()),
        prices=EconomicPrices(output_price=4.0, capital_unit_cost=2.0, labor_unit_cost=3.0),
        fixed_cost=5.0, adoption_cost=7.0,
    )
    assert result["output"] == 5.0
    assert result["revenue"] == 20.0
    assert result["capital_cost"] == 6.0
    assert result["labor_cost"] == 6.0
    assert result["total_cost"] == 24.0
    assert result["profit"] == -4.0


def test_invalid_price_rejected():
    with pytest.raises(ValueError, match="output_price"):
        EconomicPrices(-1, 1, 1)


def test_invalid_aggregated_output_rejected():
    with pytest.raises(ValueError, match="output"):
        evaluate_task_plan(
            firm(), plan(), aggregate_tasks=lambda _: float("nan"),
            prices=EconomicPrices(1, 1, 1),
        )


def test_infeasible_plan_rejected_before_aggregation():
    allocations = [TaskAllocation(f"T{j:02d}", 0.0, 1.0 if j == 20 else 0.0)
                   for j in range(1, 21)]
    with pytest.raises(ValueError, match="not eligible"):
        evaluate_task_plan(
            firm(), allocations, aggregate_tasks=lambda _: 0.0,
            prices=EconomicPrices(1, 1, 1),
        )

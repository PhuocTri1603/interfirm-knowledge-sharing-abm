import pytest

from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm, TaskCapability
from interfirm_abm.task_aggregators import weighted_linear
from interfirm_abm.task_economic_policy import PlayerState, ProductionDecision, evaluate_joint_decisions
from interfirm_abm.task_market_bridge import TaskMarketTechnology


def sample():
    tasks = tuple(TaskCapability(f"T{i:02d}", 1, 2, True) for i in range(1, 21))
    firm = TaskBasedFirm("firm", 2, 2, tasks)
    allocation = tuple(TaskAllocation(f"T{i:02d}", 0.1, 0.1) for i in range(1, 21))
    bridge = TaskMarketTechnology(
        {"firm": firm}, {"firm": allocation},
        lambda activities: weighted_linear(activities, {key: 0.05 for key in activities}),
        2, 1, lambda quantity: 10 - quantity,
    )
    return bridge


def test_task_output_flows_to_shared_market():
    result = evaluate_joint_decisions(
        {"firm": PlayerState("firm", 2, 2)},
        {"firm": ProductionDecision(2, 2)},
        sample().specification(),
    )
    assert result["market_quantity"] == pytest.approx(0.3)
    assert result["market_price"] == pytest.approx(9.7)
    assert result["player_costs"]["firm"] == pytest.approx(6)


def test_decision_must_match_task_allocation():
    with pytest.raises(ValueError, match="match"):
        evaluate_joint_decisions(
            {"firm": PlayerState("firm", 2, 2)},
            {"firm": ProductionDecision(1, 2)},
            sample().specification(),
        )

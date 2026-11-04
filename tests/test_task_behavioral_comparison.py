import pytest
"""Controlled demonstration: different L6 choice operators, identical technology.

This is a test fixture, not a calibrated economic experiment.
"""
from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm, TaskCapability
from interfirm_abm.task_decision_rules import FiniteChoiceOptimization
from interfirm_abm.task_learning_choices import SoftmaxChoice
from interfirm_abm.task_dynamic_market import DynamicTaskMarket, run_dynamic_task_market


def test_same_technology_different_decisions_change_market_outcomes():
    ids = (
        "L3=flexible|L4=eligibility|L5=competitive|L6=optimization",
        "L3=flexible|L4=eligibility|L5=competitive|L6=softmax",
    )
    shared_tasks = tuple(TaskCapability(f"T{i:02d}", 1, 1, True) for i in range(1, 21))
    firms = {key: TaskBasedFirm(key, 2, 2, shared_tasks) for key in ids}
    assert len({firm.tasks for firm in firms.values()}) == 1

    def candidates(firm, observation):
        return {
            "high": tuple(TaskAllocation(f"T{i:02d}", 0, 0.1) for i in range(1, 21)),
            "low": tuple(TaskAllocation(f"T{i:02d}", 0, 0.0) for i in range(1, 21)),
        }

    def expected_benefit(firm, observation, name, plan):
        return 2.0 if name == "high" else 0.0

    class FixedRandom:
        def random(self):
            return 0.999999

    policies = {
        ids[0]: FiniteChoiceOptimization(candidates, expected_benefit),
        ids[1]: SoftmaxChoice(candidates, expected_benefit, 100.0, FixedRandom()),
    }
    market = DynamicTaskMarket(
        firms, aggregate_tasks=lambda activities: sum(activities.values()),
        inverse_demand=lambda q: max(0.0, 10.0 - q),
        capital_unit_cost=1.0, labor_unit_cost=1.0,
    )
    result = run_dynamic_task_market(market, policies, rounds=2)
    assert result["players"] == 2
    assert [r["market_quantity"] for r in result["trajectory"]] == pytest.approx([2.0, 2.0])
    assert result["ranking"][0]["player_id"] == ids[0]
    assert result["ranking"][0]["total_benefit"] == pytest.approx(28.0)
    assert result["ranking"][1]["total_benefit"] == 0.0
    assert result["execution_status"] == "injected_task_policies_not_research_validated"

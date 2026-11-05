import pytest

from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm, TaskCapability
from interfirm_abm.task_economic_policy import MarketObservation
from interfirm_abm.task_market_beliefs import ExpectedMarketState, BeliefBasedProfit
from interfirm_abm.task_decision_rules import FiniteChoiceOptimization


def test_choice_uses_supplied_belief_not_realized_market_price():
    firm = TaskBasedFirm(
        "p", 3, 3,
        tuple(TaskCapability(f"T{i:02d}", 1, 2, True) for i in range(1, 21)),
    )
    plans = {
        "low": tuple(TaskAllocation(f"T{i:02d}", 0.05, 0) for i in range(1, 21)),
        "high": tuple(TaskAllocation(f"T{i:02d}", 0.10, 0) for i in range(1, 21)),
    }
    scorer = BeliefBasedProfit(
        lambda f, o: ExpectedMarketState(expected_price=2),
        lambda f, plan: sum(a.labor for a in plan),
        lambda f, plan: 0.5 * sum(a.labor for a in plan),
    )
    rule = FiniteChoiceOptimization(lambda f, o: plans, scorer)
    assert rule.decide_tasks(firm, MarketObservation(1, None, None)) == plans["high"]
    assert rule.decide_tasks(firm, MarketObservation(2, 0.01, 999)) == plans["high"]


def test_invalid_market_beliefs_rejected():
    with pytest.raises(ValueError):
        ExpectedMarketState(float("nan"))
    with pytest.raises(ValueError):
        ExpectedMarketState(2, -1)

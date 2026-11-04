import pytest

from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm, TaskCapability
from interfirm_abm.task_economic_policy import MarketObservation
from interfirm_abm.task_decision_rules import FiniteChoiceOptimization


def firm():
    return TaskBasedFirm(
        "p", 3, 3,
        tuple(TaskCapability(f"T{i:02d}", 1, 2, True) for i in range(1, 21)),
    )


def plan(amount):
    return tuple(TaskAllocation(f"T{i:02d}", amount, 0) for i in range(1, 21))


def test_optimization_selects_highest_explicit_expected_benefit():
    rule = FiniteChoiceOptimization(
        lambda f, o: {"low": plan(0.05), "high": plan(0.1)},
        lambda f, o, name, p: {"low": 1, "high": 2}[name],
    )
    assert rule.decide_tasks(firm(), MarketObservation(1, None, None)) == plan(0.1)


def test_ties_resolve_by_candidate_id():
    rule = FiniteChoiceOptimization(
        lambda f, o: {"z": plan(0.1), "a": plan(0.05)},
        lambda f, o, name, p: 2,
    )
    assert rule.decide_tasks(firm(), MarketObservation(1, None, None)) == plan(0.05)


def test_invalid_candidate_is_rejected():
    rule = FiniteChoiceOptimization(
        lambda f, o: {"bad": plan(1)},
        lambda f, o, name, p: 100,
    )
    with pytest.raises(ValueError):
        rule.decide_tasks(firm(), MarketObservation(1, None, None))


def test_missing_candidates_rejected():
    rule = FiniteChoiceOptimization(lambda f, o: {}, lambda f, o, name, p: 1)
    with pytest.raises(ValueError):
        rule.decide_tasks(firm(), MarketObservation(1, None, None))

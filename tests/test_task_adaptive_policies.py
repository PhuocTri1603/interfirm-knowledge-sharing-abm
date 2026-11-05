from random import Random

from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm, TaskCapability
from interfirm_abm.task_economic_policy import MarketObservation
from interfirm_abm.task_adaptive_policies import (
    AdaptivePolicySpecification, adaptive_optimization, adaptive_softmax,
)


def setup():
    firm = TaskBasedFirm(
        "p", 3, 3,
        tuple(TaskCapability(f"T{i:02d}", 1, 2, True) for i in range(1, 21)),
    )
    plans = {
        "low": tuple(TaskAllocation(f"T{i:02d}", 0.05, 0) for i in range(1, 21)),
        "high": tuple(TaskAllocation(f"T{i:02d}", 0.10, 0) for i in range(1, 21)),
    }
    spec = AdaptivePolicySpecification(
        lambda f, o: plans,
        lambda f, p: sum(a.labor for a in p),
        lambda f, p: 1.5 * sum(a.labor for a in p),
        initial_expected_price=2,
        adjustment_rate=1,
    )
    return firm, plans, spec


def test_adaptive_optimization_changes_choice_after_observed_price():
    firm, plans, spec = setup()
    policy = adaptive_optimization(spec)
    assert policy.decide_tasks(firm, MarketObservation(1, None, None)) == plans["high"]
    assert policy.decide_tasks(firm, MarketObservation(2, 1, 10)) == plans["low"]


def test_adaptive_softmax_changes_choice_probabilities():
    firm, plans, spec = setup()
    policy = adaptive_softmax(spec, temperature=0.001, rng=Random(8))
    assert policy.decide_tasks(firm, MarketObservation(1, None, None)) == plans["high"]
    assert policy.decide_tasks(firm, MarketObservation(2, 1, 10)) == plans["low"]


def test_new_policy_has_fresh_belief_state():
    firm, plans, spec = setup()
    first = adaptive_optimization(spec)
    first.decide_tasks(firm, MarketObservation(2, 1, 10))
    second = adaptive_optimization(spec)
    assert second.decide_tasks(firm, MarketObservation(1, None, None)) == plans["high"]

from random import Random

import pytest

from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm, TaskCapability
from interfirm_abm.task_economic_policy import MarketObservation
from interfirm_abm.task_learning_choices import TrialAndErrorChoice, SoftmaxChoice, ImitationChoice


def fixture():
    firm = TaskBasedFirm(
        "p", 3, 3,
        tuple(TaskCapability(f"T{i:02d}", 1, 2, True) for i in range(1, 21)),
    )
    plans = {
        "a": tuple(TaskAllocation(f"T{i:02d}", 0.05, 0) for i in range(1, 21)),
        "b": tuple(TaskAllocation(f"T{i:02d}", 0.10, 0) for i in range(1, 21)),
    }
    return firm, plans, MarketObservation(1, None, None)


def test_trial_and_error_reproducible_and_sticky_without_exploration():
    firm, plans, obs = fixture()
    make = lambda: TrialAndErrorChoice(
        lambda f, o: plans, lambda f, o, name, plan: 1, 0, Random(17)
    )
    first, second = make(), make()
    assert [first.decide_tasks(firm, obs) for _ in range(4)] == [
        second.decide_tasks(firm, obs) for _ in range(4)
    ]


def test_softmax_reproducible_with_explicit_seed():
    firm, plans, obs = fixture()
    make = lambda: SoftmaxChoice(
        lambda f, o: plans,
        lambda f, o, name, plan: {"a": 0, "b": 3}[name],
        1.0, Random(5),
    )
    assert [make().decide_tasks(firm, obs) for _ in range(1)] == [
        make().decide_tasks(firm, obs) for _ in range(1)
    ]


def test_imitation_uses_only_explicit_peer_scores():
    firm, plans, obs = fixture()
    rule = ImitationChoice(lambda f, o: plans, lambda f, o: {"a": 2, "b": 5})
    assert rule.decide_tasks(firm, obs) == plans["b"]


def test_imitation_rejects_missing_peer_evidence():
    firm, plans, obs = fixture()
    rule = ImitationChoice(lambda f, o: plans, lambda f, o: {})
    with pytest.raises(ValueError):
        rule.decide_tasks(firm, obs)


def test_softmax_requires_positive_temperature():
    with pytest.raises(ValueError):
        SoftmaxChoice(lambda f, o: {}, lambda f, o, name, p: 0, 0, Random(1))

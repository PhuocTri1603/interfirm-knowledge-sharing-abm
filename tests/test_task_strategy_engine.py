from random import Random
import pytest

from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm, TaskCapability
from interfirm_abm.task_economic_policy import MarketObservation
from interfirm_abm.task_strategy_engine import (
    Action, ComposedStrategyPolicy, DecisionParameters, StrategyIdentity,
    compose_all_policies, strategy_roster,
)


def firm():
    tasks = tuple(TaskCapability(f"T{i:02d}", 1, 1, True) for i in range(1, 21))
    return TaskBasedFirm("test", 10, 10, tasks)


def candidates(identity, firm, info):
    return {
        "a": Action("a", tuple(TaskAllocation(f"T{i:02d}", .1, 0) for i in range(1, 21)),
                    offered_price=3 if identity.L5 == "price" else None),
        "b": Action("b", tuple(TaskAllocation(f"T{i:02d}", .2, 0) for i in range(1, 21)),
                    offered_price=4 if identity.L5 == "price" else None),
    }


def value(identity, firm, info, action):
    return 1.0 if action.action_id == "a" else 2.0


def test_full_cartesian_roster_no_exclusions():
    roster = strategy_roster()
    assert len(roster) == 256
    assert len({r.strategy_id for r in roster}) == 256
    assert sum(r.L5 == "adaptive" and r.L6 == "imitation" for r in roster) == 16
    assert sum(r.L5 == "price" for r in roster) == 64


def test_factory_creates_256_independent_policies_and_reproducible_seeds():
    p = DecisionParameters(.1, 1.0)
    left = compose_all_policies(candidates, value, p, 17)
    right = compose_all_policies(candidates, value, p, 17)
    assert len(left) == 256
    assert left.keys() == right.keys()
    assert len({id(v.own_history) for v in left.values()}) == 256
    assert [v.rng.random() for v in left.values()] == [v.rng.random() for v in right.values()]


def test_adaptive_does_not_request_peer_data():
    identity = next(x for x in strategy_roster() if x.L5 == "adaptive" and x.L6 == "optimization")
    def forbidden_peer(*args):
        raise AssertionError("Adaptive must not observe rivals")
    p = ComposedStrategyPolicy(identity, candidates, value, DecisionParameters(0, 1), Random(1), forbidden_peer)
    obs = MarketObservation(1, None, None)
    assert p.decide_tasks(firm(), obs)[0].labor == .2
    p.observe_payoff(firm(), 1, 9)
    assert len(p.own_history) == 1


def test_price_bid_rejected_by_allocation_only_runner():
    identity = next(x for x in strategy_roster() if x.L5 == "price" and x.L6 == "optimization")
    p = ComposedStrategyPolicy(identity, candidates, value, DecisionParameters(0, 1), Random(1))
    assert p.decide_action(firm(), MarketObservation(1, None, None)).offered_price == 4
    p.observe_payoff(firm(), 1, 2)
    with pytest.raises(ValueError, match="cannot settle price bids"):
        p.decide_tasks(firm(), MarketObservation(2, None, None))


def test_self_imitation_does_not_access_peer_provider():
    identity = next(x for x in strategy_roster() if x.L5 == "adaptive" and x.L6 == "imitation")
    def forbidden_peer(*args):
        raise AssertionError("Game 1 cannot access rivals")
    p = ComposedStrategyPolicy(identity, candidates, value, DecisionParameters(0, 1), Random(1), forbidden_peer)
    observation = MarketObservation(1, None, None)
    assert p.decide_action(firm(), observation).action_id == "b"
    p.observe_payoff(firm(), 1, 2)
    p.own_history.append(type(p.own_history[0])(0, "a", 8))
    assert p.decide_action(firm(), observation).action_id == "a"


def test_imitation_uses_own_history():
    identity = next(x for x in strategy_roster() if x.L5 == "cournot" and x.L6 == "imitation")
    p = ComposedStrategyPolicy(identity, candidates, value, DecisionParameters(0, 1), Random(1))
    assert p.decide_action(firm(), MarketObservation(1, None, None)).action_id == "b"
    p.observe_payoff(firm(), 1, 1)
    p.own_history.append(type(p.own_history[0])(0, "a", 10))
    assert p.decide_action(firm(), MarketObservation(2, None, None)).action_id == "a"

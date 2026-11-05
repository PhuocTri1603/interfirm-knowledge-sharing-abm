"""Mechanism-level verification with transparent analytical benchmarks.

These tests establish implementation consistency, not empirical validity or
researcher approval of any illustrative economic specification.
"""
from random import Random

import pytest

from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm, TaskCapability
from interfirm_abm.task_economic_policy import (
    EconomicSpecification, PlayerState, ProductionDecision, evaluate_joint_decisions,
    MarketObservation,
)
from interfirm_abm.task_strategy_engine import (
    Action, ComposedStrategyPolicy, DecisionParameters, strategy_roster,
)


def test_inverse_demand_competition_and_accounting():
    players = {"a": PlayerState("a", 10, 10), "b": PlayerState("b", 10, 10)}
    spec = EconomicSpecification(
        lambda p, d: d.capital + d.labor,
        lambda p, d: 2 * d.capital + d.labor,
        lambda q: max(0, 20 - q),
    )
    low = evaluate_joint_decisions(
        players, {"a": ProductionDecision(1, 0), "b": ProductionDecision(1, 0)}, spec
    )
    high = evaluate_joint_decisions(
        players, {"a": ProductionDecision(2, 0), "b": ProductionDecision(2, 0)}, spec
    )
    assert low["market_price"] == 18
    assert high["market_price"] == 16
    assert sum(low["round_payoffs"].values()) == pytest.approx(32)
    assert sum(high["round_payoffs"].values()) == pytest.approx(56)


def test_task_eligibility_and_resource_feasibility():
    tasks = tuple(TaskCapability(f"T{i:02d}", 1, 2, i != 1) for i in range(1, 21))
    firm = TaskBasedFirm("firm", 5, 5, tasks)
    feasible = [TaskAllocation(f"T{i:02d}", .1, 0) for i in range(1, 21)]
    assert sum(firm.evaluate_allocation(feasible).values()) == pytest.approx(2)
    prohibited = feasible.copy()
    prohibited[0] = TaskAllocation("T01", 0, 1)
    with pytest.raises(ValueError, match="not eligible"):
        firm.evaluate_allocation(prohibited)
    excessive = [TaskAllocation(f"T{i:02d}", 1, 0) for i in range(1, 21)]
    with pytest.raises(ValueError, match="exceeds endowment"):
        firm.evaluate_allocation(excessive)


def test_optimization_selects_higher_valued_action():
    identity = next(x for x in strategy_roster()
                    if x.L5 == "competitive" and x.L6 == "optimization")
    tasks = tuple(TaskCapability(f"T{i:02d}", 1, 1, True) for i in range(1, 21))
    firm = TaskBasedFirm("firm", 10, 10, tasks)

    def candidates(identity, firm, info):
        return {
            key: Action(key, tuple(TaskAllocation(f"T{i:02d}", labor, 0)
                                   for i in range(1, 21)))
            for key, labor in (("low", .1), ("high", .2))
        }

    def valuation(identity, firm, info, action):
        return 10 if action.action_id == "high" else 1

    policy = ComposedStrategyPolicy(
        identity, candidates, valuation, DecisionParameters(0, 1), Random(42)
    )
    assert policy.decide_action(firm, MarketObservation(1, None, None)).action_id == "high"
    policy.observe_payoff(firm, 1, 10)
    assert len(policy.own_history) == 1


def test_optimization_is_not_equivalent_to_random_exploration():
    identities = strategy_roster()
    optimization = next(x for x in identities
                        if x.L5 == "competitive" and x.L6 == "optimization")
    trial = next(x for x in identities
                 if x.L5 == "competitive" and x.L6 == "trial_error")
    tasks = tuple(TaskCapability(f"T{i:02d}", 1, 1, True) for i in range(1, 21))
    firm = TaskBasedFirm("firm", 10, 10, tasks)

    def candidates(identity, firm, info):
        return {
            key: Action(key, tuple(TaskAllocation(f"T{i:02d}", labor, 0)
                                   for i in range(1, 21)))
            for key, labor in (("a", .1), ("b", .2))
        }

    def valuation(identity, firm, info, action):
        return 1 if action.action_id == "a" else 2

    opt = ComposedStrategyPolicy(
        optimization, candidates, valuation, DecisionParameters(1, 1), Random(17)
    )
    explore = ComposedStrategyPolicy(
        trial, candidates, valuation, DecisionParameters(1, 1), Random(17)
    )
    opt_choices, trial_choices = [], []
    for round_number in range(1, 31):
        obs = MarketObservation(round_number, None, None)
        opt_choices.append(opt.decide_action(firm, obs).action_id)
        explore_choice = explore.decide_action(firm, obs).action_id
        trial_choices.append(explore_choice)
        opt.observe_payoff(firm, round_number, 2)
        explore.observe_payoff(firm, round_number, 2)
    assert set(opt_choices) == {"b"}
    assert "a" in trial_choices and "b" in trial_choices

"""Mechanism verification for the *illustrative* Game 1, not empirical validation."""
from __future__ import annotations

from math import isclose, isfinite, fsum
from random import Random

import pytest

from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm, TaskCapability
from interfirm_abm.task_economic_policy import MarketObservation
from interfirm_abm.task_multi_action_diagnostic import (
    action_factory, configurations, market_factory, policy_factory,
)
from interfirm_abm.task_mixed_market import SupplyOffer
from interfirm_abm.task_strategy_engine import (
    ComposedStrategyPolicy, DecisionInformation, DecisionParameters, OwnOutcome,
    strategy_roster,
)


def test_execution_roster_and_distinct_initial_conditions():
    configs = configurations(100)
    assert len(configs) == 100
    assert all(len(roster) == 256 for roster in configs.values())
    signatures = {
        (next(iter(roster.values())).capital_endowment,
         next(iter(roster.values())).labor_endowment,
         next(iter(roster.values())).tasks[0].capital_productivity,
         next(iter(roster.values())).tasks[0].labor_productivity)
        for roster in configs.values()
    }
    assert len(signatures) == 100


def test_production_feasibility_and_noneligible_capital():
    firm = next(iter(configurations(1)["C000"].values()))
    identity = strategy_roster()[0]
    info = DecisionInformation(MarketObservation(1, None, None), ())
    candidates = action_factory(identity, firm, info)
    assert len(candidates) >= 2
    assert len({(sum(x.capital for x in a.allocation),
                 sum(x.labor for x in a.allocation)) for a in candidates.values()}) > 1
    for action in candidates.values():
        firm.evaluate_allocation(list(action.allocation))
    bad = [TaskAllocation(t.task_id, 0., 1.) for t in firm.tasks]
    with pytest.raises(ValueError, match="Automation not eligible"):
        firm.evaluate_allocation(bad)


def test_market_clearing_respects_quantity_and_reserve_price():
    roster = configurations(1)["C000"]
    market = market_factory("C000", roster)
    offers = {key: SupplyOffer(key, 2., 100. if i % 2 else None)
              for i, key in enumerate(roster)}
    sales = market.clearing(1, offers)
    assert set(sales) == set(offers)
    assert all(0 <= sale.quantity <= offers[key].available_quantity
               for key, sale in sales.items())
    assert all(sale.quantity == 0 for key, sale in sales.items()
               if offers[key].offered_price == 100.)
    assert all(isfinite(sale.unit_price) and sale.unit_price >= 0
               for sale in sales.values())


def test_four_learning_mechanisms_and_history_feedback():
    roster = configurations(1)["C000"]
    firm = next(iter(roster.values()))
    for identity in strategy_roster():
        if identity.L5 == "adaptive" and identity.L6 == "imitation":
            continue  # unresolved semantic conflict; do not silently certify
        policy = policy_factory("C000", market_factory("C000", roster))[identity.strategy_id]
        action = policy.decide_action(firm, MarketObservation(1, None, None))
        policy.observe_payoff(firm, 1, 1.25)
        assert policy.pending_action is None
        assert policy.own_history[-1].action_id == action.action_id
        assert policy.own_history[-1].profit == 1.25


def test_reproducibility_and_seed_sensitivity():
    roster = configurations(1)["C000"]
    market = market_factory("C000", roster)
    first = policy_factory("C000", market)
    second = policy_factory("C000", market)
    observation = MarketObservation(1, None, None)
    assert {k: p.decide_action(roster[k], observation).action_id for k, p in first.items()} == {
        k: p.decide_action(roster[k], observation).action_id for k, p in second.items()
    }
    # Stochastic learning must not be conflated with a proof of convergence.
    assert any(x.L6 in ("softmax", "trial_error") for x in strategy_roster())


def test_unresolved_semantics_prevent_scientific_flag():
    from interfirm_abm.task_strategy_audit import audit_strategy_semantics
    audit = audit_strategy_semantics()
    assert audit["semantic_conflict_count"] == 16
    assert audit["ready_for_scientific_comparison"] is False

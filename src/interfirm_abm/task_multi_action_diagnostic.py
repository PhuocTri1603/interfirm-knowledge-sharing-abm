"""Illustrative multi-action Game 1 scenario; NOT researcher-approved economics.

Replaces the single-action integration-test fixture for diagnostic runs.
Explicit assumptions: discrete feasible K/L plans, linear task aggregation,
linear inverse demand, proportional rationing, and myopic price expectations.
"""
from __future__ import annotations

from hashlib import sha256
from math import fsum
from random import Random

from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm, TaskCapability
from interfirm_abm.task_economic_policy import MarketObservation
from interfirm_abm.task_experiment_dimensions import strategy_player_ids
from interfirm_abm.task_mixed_market import MixedMarket, Sale
from interfirm_abm.task_strategy_engine import (
    Action, ComposedStrategyPolicy, DecisionParameters, strategy_roster,
)

ROSTER = strategy_roster()
ACTION_PLANS = {
    "labor_low": (.0, .25),
    "labor_high": (.0, .45),
    "capital_low": (.25, .0),
    "capital_high": (.45, .0),
    "balanced": (.20, .20),
}


def configurations(n=100):
    if n < 1 or n > 100:
        raise ValueError("n must be in [1,100]")
    result = {}
    for i in range(n):
        # Distinct, reproducible configurations, common within each market.
        k = 7.0 + (i % 10) * .4
        l = 7.0 + (i // 10) * .4
        capital_productivity = .8 + (i % 5) * .1
        labor_productivity = .8 + (i // 5 % 5) * .1
        tasks = tuple(
            TaskCapability(f"T{t:02d}", labor_productivity,
                           capital_productivity, t > 5)
            for t in range(1, 21)
        )
        result[f"C{i:03d}"] = {
            sid: TaskBasedFirm(sid, k, l, tasks)
            for sid in strategy_player_ids()
        }
    return result


def action_factory(identity, firm, info):
    result = {}
    for name, (k, l) in ACTION_PLANS.items():
        if k and any(not task.automation_eligible for task in firm.tasks):
            # Non-eligible tasks receive labor, never capital.
            allocation = tuple(
                TaskAllocation(task.task_id, l if not task.automation_eligible else l,
                               k if task.automation_eligible else 0)
                for task in firm.tasks
            )
        else:
            allocation = tuple(TaskAllocation(task.task_id, l, k) for task in firm.tasks)
        try:
            activity = firm.evaluate_allocation(list(allocation))
        except ValueError:
            continue
        for price in ((1.5, 2.0, 2.5) if identity.L5 == "price" else (None,)):
            suffix = "" if price is None else f"_p{price:.1f}"
            key = name + suffix
            result[key] = Action(key, allocation, offered_price=price)
    if len(result) < 2:
        raise ValueError("Each strategy requires at least two feasible actions")
    return result


def valuation(identity, firm, info, action):
    # Illustrative one-period expected margin, not a solved equilibrium.
    activity = firm.evaluate_allocation(list(action.allocation))
    output = fsum(activity.values())
    cost = fsum(a.capital + a.labor for a in action.allocation)
    anticipated_price = info.market.last_market_price if info.market.last_market_price is not None else 2.0
    price = action.offered_price if action.offered_price is not None else anticipated_price
    return price * output - cost


def market_factory(config_id, roster):
    # Demand: Q_d=max(0, intercept - slope*P). Supply is rationed at
    # a common market price; offers above it receive no sales.
    i = int(config_id[1:])
    intercept = 850 + 5 * (i // 10)
    slope = 100 + (i % 10) * 3

    def clearing(round_number, offers):
        total_supply = fsum(o.available_quantity for o in offers.values())
        price = max(.0, (intercept - total_supply) / slope)
        # Price bids are reserve prices, not automatically accepted.
        eligible = {key: offer for key, offer in offers.items()
                    if offer.offered_price is None or offer.offered_price <= price}
        eligible_supply = fsum(o.available_quantity for o in eligible.values())
        # Fixed-point price with price-floor exclusions is not assumed:
        # use provisional market price and ration only eligible supply.
        demand = max(0., intercept - slope * price)
        fraction = min(1., demand / eligible_supply) if eligible_supply else 0.
        return {key: Sale(offer.available_quantity * fraction if key in eligible else 0.,
                          price)
                for key, offer in offers.items()}

    return MixedMarket(roster, lambda activity: fsum(activity.values()),
                       clearing, 1., 1., lambda key, action, round_number: 0.)


def policy_factory(config_id, market):
    policies = {}
    # Peer data comes from prior realized outcomes only, not current-round results.
    def peer_provider(firm, observation):
        peers = [(sid, p) for sid, p in policies.items()
                 if sid != firm.firm_id and p.own_history]
        if not peers:
            # First-round bootstrap; subsequent rounds use realized peer outcomes.
            return ({firm.firm_id: "balanced_p1.5" if "L5=price" in firm.firm_id else "balanced"},\n                    {firm.firm_id: 0.})
        return ({sid: p.own_history[-1].action_id for sid, p in peers},
                {sid: p.own_history[-1].profit for sid, p in peers})

    for identity in ROSTER:
        seed = int.from_bytes(sha256(
            f"{config_id}|{identity.strategy_id}|diagnostic-v2".encode()
        ).digest()[:8], "big")
        policies[identity.strategy_id] = ComposedStrategyPolicy(
            identity, action_factory, valuation,
            DecisionParameters(.15, 1.), Random(seed), peer_provider
        )
    return policies

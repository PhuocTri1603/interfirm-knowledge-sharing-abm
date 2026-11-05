"""Illustrative multi-action Game 1 scenario; NOT researcher-approved economics.

Replaces the single-action integration-test fixture for diagnostic runs.
Explicit assumptions: strategy-generated feasible pure-mode K/L plans, equal-weight Cobb-Douglas task aggregation,
linear inverse demand, proportional rationing, and myopic price expectations.
"""
from __future__ import annotations

from hashlib import sha256
from math import fsum
from random import Random
from pathlib import Path

from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm, load_approved_population
from interfirm_abm.task_aggregators import task_ces
from interfirm_abm.task_strategy_actions import build_actions, score_action
from interfirm_abm.task_economic_policy import MarketObservation
from interfirm_abm.task_experiment_dimensions import strategy_player_ids
from interfirm_abm.task_mixed_market import MixedMarket, Sale
from interfirm_abm.task_strategy_engine import (
    Action, ComposedStrategyPolicy, DecisionParameters, strategy_roster,
)

ROSTER = strategy_roster()
TASK_WEIGHTS = {f"T{j:02d}": 1.0 / 20 for j in range(1, 21)}


def aggregate_20_tasks(activity):
    """20-task Cobb-Douglas baseline (CES sigma=1), equal task shares.

    This selects only the across-task aggregator. Within-task production,
    demand, costs and learning parameters remain diagnostic assumptions.
    """
    return task_ces(activity, TASK_WEIGHTS, sigma=1.0)


def configurations(n=100):
    """Map C000..C099 to the 100 *approved* task-based technologies.

    Each configuration uses one original F001..F100 task capability schedule,
    eligibility mask, and K/L endowments. All 256 strategy players in that
    configuration face exactly that same technology and initial resources.
    No synthetic technology coefficients or task eligibility are generated.
    """
    if type(n) is not int or not 1 <= n <= 100:
        raise ValueError("n must be in [1,100]")
    root = Path(__file__).resolve().parents[2] / "data" / "firms"
    population = load_approved_population(
        root / "task_based_100_firms_profiles.csv",
        root / "task_based_100_firms_tasks.csv",
    )
    result = {}
    for i, original in enumerate(population[:n]):
        config_id = f"C{i:03d}"
        result[config_id] = {
            sid: TaskBasedFirm(
                firm_id=sid,
                capital_endowment=original.capital_endowment,
                labor_endowment=original.labor_endowment,
                tasks=original.tasks,
            )
            for sid in strategy_player_ids()
        }
    return result


def action_factory(identity, firm, info):
    return build_actions(identity, firm, info)


def valuation(identity, firm, info, action):
    return score_action(identity, firm, info, action, aggregate_20_tasks)


def market_factory(config_id, roster):
    # Demand: Q_d=max(0, intercept - slope*P). Supply is rationed at
    # a common market price; offers above it receive no sales.
    i = int(config_id[1:])
    intercept = 1400 + 15 * (i // 10)
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

    return MixedMarket(roster, aggregate_20_tasks,
                       clearing, 1., 1., lambda key, action, round_number: 0.)


def policy_factory(config_id, market):
    policies = {}
    # Peer data comes from prior realized outcomes only, not current-round results.
    def peer_provider(firm, observation):
        peers = [(sid, p) for sid, p in policies.items()
                 if sid != firm.firm_id and p.own_history]
        if not peers:
            # No realized peers exist in round one; do not invent self-as-peer.
            return ({}, {})
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

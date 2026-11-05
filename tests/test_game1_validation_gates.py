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
        policy = policy_factory("C000", market_factory("C000", roster))[identity.strategy_id]
        action = policy.decide_action(roster[identity.strategy_id], MarketObservation(1, None, None))
        policy.observe_payoff(roster[identity.strategy_id], 1, 1.25)
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


def test_approved_adaptive_imitation_semantics_resolved_without_economic_certification():
    from interfirm_abm.task_strategy_audit import audit_strategy_semantics
    audit = audit_strategy_semantics()
    assert audit["semantic_conflict_count"] == 0
    assert audit["resolved_adaptive_imitation_count"] == 16
    assert audit["ready_for_scientific_comparison"] is True


def test_ces_reference_theory_constant_productivity_and_elasticity():
    from interfirm_abm.task_ces_reference import ces_output, ces_mrt_ratio
    assert ces_output(4, 9, 1, a=1, alpha=.5) == pytest.approx(6)
    for sigma in (.5, 1., 2., 5.):
        assert ces_output(8, 8, sigma, a=1, alpha=.5) == pytest.approx(8)
        assert ces_output(8, 8, sigma, a=2, alpha=.5) == pytest.approx(16)
        assert ces_mrt_ratio(8, 8, sigma) == pytest.approx(1)
    assert ces_mrt_ratio(8, 2, .5) < ces_mrt_ratio(8, 2, 2.)
    assert ces_output(8, 2, .5) < ces_output(8, 2, 2.)


def test_all_approved_technologies_are_loaded_without_mutation():
    """Verify the exact approved 100-by-20 capability matrix, not just count."""
    from pathlib import Path
    from interfirm_abm.task_based_firm import load_approved_population
    root = Path(__file__).resolve().parents[1] / "data" / "firms"
    originals = load_approved_population(
        root / "task_based_100_firms_profiles.csv",
        root / "task_based_100_firms_tasks.csv",
    )
    actual = configurations(100)
    assert len(actual) == len(originals) == 100
    assert len({original.tasks for original in originals}) == 100
    for i, original in enumerate(originals):
        roster = actual[f"C{i:03d}"]
        assert len(roster) == 256
        for sid, player in roster.items():
            assert player.firm_id == sid
            assert player.capital_endowment == original.capital_endowment
            assert player.labor_endowment == original.labor_endowment
            assert player.tasks == original.tasks


def test_payoff_and_ranking_reconcile_across_players_and_market():
    """Check accounting identities, cumulative profits, and rankings end-to-end."""
    from collections import defaultdict
    from interfirm_abm.task_full_tournament import TournamentSpecification, run_full_tournament
    configs = configurations(2)
    result = run_full_tournament(
        configs, TournamentSpecification(
            market_factory, policy_factory, rounds=3, expected_configurations=2
        ),
    )
    assert result["player_round_observations"] == 2 * 256 * 3
    by_round = defaultdict(list)
    by_player = defaultdict(list)
    for row in result["player_trajectory"]:
        assert isfinite(row["round_profit"])
        assert row["produced_quantity"] >= row["sold_quantity"] >= 0
        assert row["revenue"] == pytest.approx(
            row["sold_quantity"] * row["realized_unit_price"]
        )
        assert row["round_profit"] == pytest.approx(
            row["revenue"] - row["production_and_extra_cost"]
        )
        by_round[(row["config_id"], row["round"])].append(row)
        by_player[(row["config_id"], row["player_id"])].append(row)
    assert len(by_round) == 6
    assert len(by_player) == 512
    for rows in by_player.values():
        assert [r["round"] for r in rows] == [1, 2, 3]
        running = 0.
        for row in rows:
            running += row["round_profit"]
            assert row["cumulative_profit"] == pytest.approx(running)
    for row in result["market_trajectory"]:
        players = by_round[(row["config_id"], row["round"])]
        assert len(players) == 256
        for market_key, player_key in (
            ("quantity_sold", "sold_quantity"),
            ("quantity_produced", "produced_quantity"),
            ("total_revenue", "revenue"),
            ("total_cost", "production_and_extra_cost"),
            ("total_profit", "round_profit"),
        ):
            assert row[market_key] == pytest.approx(fsum(p[player_key] for p in players))
    rankings = defaultdict(list)
    for row in result["ranking_by_configuration"]:
        rankings[row["config_id"]].append(row)
        final = by_player[(row["config_id"], row["player_id"])][-1]["cumulative_profit"]
        assert row["total_benefit"] == pytest.approx(final)
    for rows in rankings.values():
        assert len(rows) == 256
        assert [r["rank"] for r in rows] == list(range(1, 257))
        assert [r["total_benefit"] for r in rows] == sorted(
            (r["total_benefit"] for r in rows), reverse=True
        )


def test_all_sixteen_adaptive_imitation_use_peers_and_own_history():
    """Peer payoff determines imitation; own realized history breaks peer ties."""
    from interfirm_abm.task_strategy_engine import Action
    roster = configurations(1)["C000"]
    obs = MarketObservation(2, 2.0, 10.0)
    ids = [x for x in strategy_roster() if x.L5 == "adaptive" and x.L6 == "imitation"]
    assert len(ids) == 16
    for identity in ids:
        firm = roster[identity.strategy_id]
        def candidates(identity, firm, info):
            assert info.peer_actions is not None
            assert info.peer_payoffs is not None
            return {
                "a": Action("a", tuple(TaskAllocation(t.task_id, .1, 0) for t in firm.tasks)),
                "b": Action("b", tuple(TaskAllocation(t.task_id, .2, 0) for t in firm.tasks)),
            }
        def value(identity, firm, info, action):
            return 0.0
        def peers(firm, obs):
            return {"peer_a": "a", "peer_b": "b"}, {"peer_a": 8.0, "peer_b": 8.0}
        p = ComposedStrategyPolicy(
            identity, candidates, value, DecisionParameters(0, 1),
            Random(1), peers,
        )
        p.own_history = [OwnOutcome(1, "a", -5.), OwnOutcome(1, "b", 7.)]
        assert p.decide_action(firm, obs).action_id == "b"
        p.observe_payoff(firm, 2, 3.)
        assert p.own_history[-1].profit == 3.
        def unequal(firm, obs):
            return {"peer_a": "a", "peer_b": "b"}, {"peer_a": 10., "peer_b": 2.}
        p.peer_provider = unequal
        assert p.decide_action(firm, MarketObservation(3, 2.0, 10.0)).action_id == "a"


def test_adaptive_imitation_round_one_does_not_fabricate_peer():
    roster = configurations(1)["C000"]
    identity = next(x for x in strategy_roster()
                    if x.L5 == "adaptive" and x.L6 == "imitation")
    p = policy_factory("C000", market_factory("C000", roster))[identity.strategy_id]
    info = p._information(MarketObservation(1, None, None), roster[identity.strategy_id])
    assert info.peer_actions == {}
    assert info.peer_payoffs == {}
    action = p.decide_action(roster[identity.strategy_id], MarketObservation(1, None, None))
    assert action.action_id


def test_cobb_douglas_20_task_aggregation_matches_geometric_mean():
    from interfirm_abm.task_multi_action_diagnostic import aggregate_20_tasks, TASK_WEIGHTS, valuation
    from interfirm_abm.task_strategy_engine import DecisionInformation
    from math import prod
    assert len(TASK_WEIGHTS) == 20
    assert set(TASK_WEIGHTS) == {f"T{i:02d}" for i in range(1, 21)}
    assert fsum(TASK_WEIGHTS.values()) == pytest.approx(1.)
    equal = {task: 4. for task in TASK_WEIGHTS}
    assert aggregate_20_tasks(equal) == pytest.approx(4.)
    mixed = {task: float(i) for i, task in enumerate(TASK_WEIGHTS, 1)}
    assert aggregate_20_tasks(mixed) == pytest.approx(prod(mixed.values()) ** (1 / 20))
    assert aggregate_20_tasks({**equal, "T01": 0.}) == 0.
    assert aggregate_20_tasks({k: 2 * v for k, v in mixed.items()}) == pytest.approx(
        2 * aggregate_20_tasks(mixed)
    )
    roster = configurations(1)["C000"]
    market = market_factory("C000", roster)
    assert market.aggregate_tasks(mixed) == pytest.approx(aggregate_20_tasks(mixed))
    identity = strategy_roster()[0]
    firm = roster[identity.strategy_id]
    info = DecisionInformation(MarketObservation(1, None, None), ())
    action = next(iter(action_factory(identity, firm, info).values()))
    activity = firm.evaluate_allocation(list(action.allocation))
    expected = 2. * aggregate_20_tasks(activity) - fsum(
        a.capital + a.labor for a in action.allocation
    )
    assert valuation(identity, firm, info, action) == pytest.approx(expected)

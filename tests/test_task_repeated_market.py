"""Repeated-market tests with synthetic actions and prices (not economic results)."""
from pathlib import Path

import pytest

from interfirm_abm.task_based_firm import load_approved_population
from interfirm_abm.task_strategy_population import StrategySpec, build_shared_market_population
from interfirm_abm.task_repeated_market import RoundActions, evaluate_repeated_market

ROOT = Path(__file__).resolve().parents[1]


def market(n=1, roster=("A", "B", "C")):
    firms = load_approved_population(
        ROOT / "data/firms/task_based_100_firms_profiles.csv",
        ROOT / "data/firms/task_based_100_firms_tasks.csv",
    )
    return build_shared_market_population(firms[:n], [StrategySpec(s) for s in roster])


def test_three_round_joint_market_and_cumulative_payoffs():
    m = market()
    ids = [c.agent_id for c in m.clones]
    actions = [
        RoundActions(dict(zip(ids, values)), {k: 1.0 for k in ids})
        for values in ((1.0, 1.0, 1.0), (2.0, 1.0, 1.0), (1.0, 2.0, 1.0))
    ]
    result = evaluate_repeated_market(
        m, actions, inverse_demand=lambda t, q: 10.0 - q
    )
    assert len(result.rounds) == 3
    assert [r.total_supply for r in result.rounds] == [3.0, 4.0, 4.0]
    assert [r.common_price for r in result.rounds] == [7.0, 6.0, 6.0]
    a = result.trajectories[0]
    assert a.profits == pytest.approx((6.0, 11.0, 5.0))
    assert a.cumulative_profits == pytest.approx((6.0, 17.0, 22.0))
    assert result.first_round_reaching(a.agent_id, 17.0) == 1
    assert result.first_round_reaching(a.agent_id, 1000.0) is None
    assert result.strategy_roster == ("A", "B", "C")


def test_arbitrary_strategy_roster_and_400_agents():
    m = market(n=100, roster=("A", "B", "C", "1AXXXX"))
    actions = [
        RoundActions(
            {c.agent_id: 1.0 for c in m.clones},
            {c.agent_id: 0.0 for c in m.clones},
        )
        for _ in range(2)
    ]
    result = evaluate_repeated_market(m, actions, inverse_demand=lambda t, q: 2.0)
    assert len(result.trajectories) == 400
    assert len(result.rounds) == 2
    assert all(t.cumulative_profits == (2.0, 4.0) for t in result.trajectories)


def test_negative_profit_and_cumulative_loss():
    m = market(roster=("A",))
    key = m.clones[0].agent_id
    result = evaluate_repeated_market(
        m, [RoundActions({key: 0.0}, {key: 3.0})] * 2,
        inverse_demand=lambda t, q: 1.0,
    )
    assert result.trajectories[0].cumulative_profits == (-3.0, -6.0)
    assert result.first_round_reaching(key, -4.0) == 0


def test_round_specific_price_schedule():
    m = market(roster=("A",))
    key = m.clones[0].agent_id
    actions = [RoundActions({key: 1.0}, {key: 0.0})] * 2
    result = evaluate_repeated_market(m, actions, inverse_demand=lambda t, q: t + 1.0)
    assert [r.common_price for r in result.rounds] == [1.0, 2.0]


def test_missing_round_and_missing_agent_rejected():
    m = market()
    with pytest.raises(ValueError, match="At least one"):
        evaluate_repeated_market(m, [], inverse_demand=lambda t, q: 1.0)
    with pytest.raises(ValueError, match="exactly"):
        evaluate_repeated_market(
            m, [RoundActions({}, {})], inverse_demand=lambda t, q: 1.0
        )


def test_unknown_agent_and_invalid_threshold_rejected():
    m = market(roster=("A",))
    key = m.clones[0].agent_id
    result = evaluate_repeated_market(
        m, [RoundActions({key: 1.0}, {key: 0.0})],
        inverse_demand=lambda t, q: 1.0,
    )
    with pytest.raises(ValueError, match="Unknown"):
        result.first_round_reaching("unknown", 1.0)
    with pytest.raises(ValueError, match="finite"):
        result.first_round_reaching(key, float("nan"))


def test_deterministic_repeated_evaluation():
    m = market()
    action = RoundActions(
        {c.agent_id: 1.0 for c in m.clones},
        {c.agent_id: 0.0 for c in m.clones},
    )
    run = lambda: evaluate_repeated_market(
        m, [action, action], inverse_demand=lambda t, q: 10.0
    )
    assert run() == run()

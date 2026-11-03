"""Policy interface tests use synthetic behaviors, not approved economic strategies."""
from pathlib import Path

import pytest

from interfirm_abm.task_based_firm import load_approved_population
from interfirm_abm.task_strategy_population import StrategySpec, build_shared_market_population
from interfirm_abm.task_strategy_policy import (
    AgentDecision, generate_policy_actions, run_policy_market,
)

ROOT = Path(__file__).resolve().parents[1]


def market(n=2, roster=("A", "B")):
    firms = load_approved_population(
        ROOT / "data/firms/task_based_100_firms_profiles.csv",
        ROOT / "data/firms/task_based_100_firms_tasks.csv",
    )
    return build_shared_market_population(firms[:n], [StrategySpec(s) for s in roster])


def test_policies_observe_only_completed_rounds_and_share_market():
    m = market()
    observed = []
    def policy(ctx):
        observed.append((ctx.round_index, len(ctx.completed_rounds)))
        return AgentDecision(output=ctx.round_index + 1.0, total_cost=1.0)
    result = run_policy_market(
        m, number_of_rounds=3, policies={"A": policy, "B": policy},
        inverse_demand=lambda t, q: 20.0 - q,
    )
    assert observed == [(t, t) for t in range(3) for _ in range(4)]
    assert [r.total_supply for r in result.rounds] == [4.0, 8.0, 12.0]
    assert [r.common_price for r in result.rounds] == [16.0, 12.0, 8.0]
    assert all(len(x.cumulative_profits) == 3 for x in result.trajectories)


def test_different_policy_labels_have_no_automatic_advantage():
    m = market(n=1, roster=("A", "B", "1AXXXX"))
    p = lambda ctx: AgentDecision(output=1.0, total_cost=0.5)
    result = run_policy_market(
        m, number_of_rounds=2, policies={s: p for s in m.strategy_roster},
        inverse_demand=lambda t, q: 5.0,
    )
    assert len({t.cumulative_profits for t in result.trajectories}) == 1


def test_400_agents_are_supported():
    m = market(n=100, roster=("A", "B", "C", "1AXXXX"))
    p = lambda ctx: AgentDecision(1.0, 0.0)
    result = run_policy_market(
        m, number_of_rounds=2, policies={s: p for s in m.strategy_roster},
        inverse_demand=lambda t, q: 2.0,
    )
    assert len(result.trajectories) == 400
    assert all(t.cumulative_profits == (2.0, 4.0) for t in result.trajectories)


def test_missing_or_extra_policy_rejected():
    m = market()
    with pytest.raises(ValueError, match="exactly"):
        generate_policy_actions(m, round_index=0, completed_rounds=(), policies={"A": lambda ctx: AgentDecision(1, 1)})


def test_bad_decision_rejected():
    with pytest.raises(ValueError):
        AgentDecision(-1, 0)
    with pytest.raises(ValueError):
        AgentDecision(1, float("nan"))
    m = market()
    with pytest.raises(TypeError, match="AgentDecision"):
        generate_policy_actions(
            m, round_index=0, completed_rounds=(),
            policies={"A": lambda ctx: None, "B": lambda ctx: AgentDecision(1, 1)}
        )


def test_invalid_rounds_and_history_rejected():
    m = market()
    p = {s: lambda ctx: AgentDecision(1, 1) for s in m.strategy_roster}
    with pytest.raises(ValueError):
        run_policy_market(m, number_of_rounds=0, policies=p, inverse_demand=lambda t, q: 1)
    with pytest.raises(ValueError, match="history"):
        generate_policy_actions(m, round_index=1, completed_rounds=(), policies=p)


def test_determinism_with_stateless_policies():
    m = market()
    p = {s: lambda ctx: AgentDecision(1 + ctx.round_index, 0) for s in m.strategy_roster}
    run = lambda: run_policy_market(
        m, number_of_rounds=2, policies=p, inverse_demand=lambda t, q: 10
    )
    assert run() == run()

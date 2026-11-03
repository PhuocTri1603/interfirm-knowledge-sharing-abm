"""Shared market integration tests; all economics inputs are test fixtures."""
from pathlib import Path
import pytest

from interfirm_abm.task_based_firm import load_approved_population
from interfirm_abm.task_strategy_population import StrategySpec, build_shared_market_population
from interfirm_abm.task_shared_market import evaluate_shared_market_round

ROOT = Path(__file__).resolve().parents[1]


def market(n=2, roster=("A", "B", "C")):
    firms = load_approved_population(
        ROOT / "data/firms/task_based_100_firms_profiles.csv",
        ROOT / "data/firms/task_based_100_firms_tasks.csv",
    )
    return build_shared_market_population(firms[:n], [StrategySpec(s) for s in roster])


def evaluate(m, outputs, costs=None, demand=None):
    if costs is None:
        costs = {k: 0.0 for k in outputs}
    if demand is None:
        demand = lambda q: max(0.0, 100.0 - q)  # TEST STUB ONLY
    return evaluate_shared_market_round(
        m, round_index=0, outputs=outputs, total_costs=costs, inverse_demand=demand
    )


def test_every_agent_shares_price_from_joint_supply():
    m = market()
    outputs = {c.agent_id: float(j + 1) for j, c in enumerate(m.clones)}
    costs = {c.agent_id: 2.0 for c in m.clones}
    result = evaluate(m, outputs, costs)
    assert result.total_supply == pytest.approx(21.0)
    assert result.common_price == pytest.approx(79.0)
    assert len(result.agents) == 6
    assert result.strategy_roster == ("A", "B", "C")
    assert all(a.revenue == pytest.approx(a.output * 79.0) for a in result.agents)
    assert all(a.profit == pytest.approx(a.revenue - 2.0) for a in result.agents)


def test_one_agents_output_changes_all_agents_common_price():
    m = market(n=1)
    baseline = {c.agent_id: 1.0 for c in m.clones}
    changed = dict(baseline)
    changed[m.clones[0].agent_id] = 2.0
    first, second = evaluate(m, baseline), evaluate(m, changed)
    assert first.common_price == 97.0
    assert second.common_price == 96.0
    assert second.agents[1].revenue < first.agents[1].revenue


def test_100_base_firms_four_strategies_single_market():
    m = market(n=100, roster=("A", "B", "C", "1AXXXX"))
    outputs = {c.agent_id: 1.0 for c in m.clones}
    result = evaluate(m, outputs, demand=lambda q: 2.0)
    assert len(result.agents) == 400
    assert result.total_supply == 400.0
    assert result.common_price == 2.0
    assert result.total_profit == 800.0


def test_zero_supply_and_negative_profits_allowed():
    m = market(n=1, roster=("A",))
    key = m.clones[0].agent_id
    result = evaluate(m, {key: 0.0}, {key: 5.0})
    assert result.total_supply == 0.0
    assert result.agents[0].profit == -5.0


@pytest.mark.parametrize("bad", [-1.0, float("nan"), float("inf")])
def test_invalid_output_rejected(bad):
    m = market(n=1, roster=("A",))
    with pytest.raises(ValueError):
        evaluate(m, {m.clones[0].agent_id: bad})


def test_incomplete_or_unknown_agent_rejected():
    m = market(n=1)
    with pytest.raises(ValueError, match="exactly"):
        evaluate(m, {m.clones[0].agent_id: 1.0})
    outputs = {c.agent_id: 1.0 for c in m.clones}
    outputs["unknown"] = 1.0
    with pytest.raises(ValueError, match="exactly"):
        evaluate(m, outputs)


def test_negative_price_and_nonfinite_cost_rejected():
    m = market(n=1, roster=("A",))
    key = m.clones[0].agent_id
    with pytest.raises(ValueError):
        evaluate(m, {key: 1.0}, demand=lambda q: -1.0)
    with pytest.raises(ValueError):
        evaluate(m, {key: 1.0}, {key: float("inf")})


def test_market_result_is_deterministic():
    m = market(n=3)
    outputs = {c.agent_id: 1.0 for c in m.clones}
    assert evaluate(m, outputs) == evaluate(m, outputs)

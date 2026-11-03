"""Tests for shared-market, extensible strategy clone construction."""
from pathlib import Path

import pytest

from interfirm_abm.task_based_firm import load_approved_population
from interfirm_abm.task_strategy_population import (
    StrategySpec, build_shared_market_population,
)

ROOT = Path(__file__).resolve().parents[1]


def firms():
    return load_approved_population(
        ROOT / "data/firms/task_based_100_firms_profiles.csv",
        ROOT / "data/firms/task_based_100_firms_tasks.csv",
    )


def test_three_strategies_create_300_independent_agents():
    market = build_shared_market_population(
        firms(), [StrategySpec(s) for s in ("A", "B", "C")]
    )
    assert market.strategy_roster == ("A", "B", "C")
    assert len(market.clones) == 300
    assert len({c.agent_id for c in market.clones}) == 300
    for base, group_start in zip(firms(), range(0, 300, 3)):
        group = market.clones[group_start:group_start + 3]
        assert {c.base_firm_id for c in group} == {base.firm_id}
        assert {c.strategy_id for c in group} == {"A", "B", "C"}
        assert all(c.firm.capital_endowment == base.capital_endowment for c in group)
        assert all(c.firm.labor_endowment == base.labor_endowment for c in group)
        assert all(c.firm.tasks == base.tasks for c in group)
        assert len({id(c.firm) for c in group}) == 3


def test_fourth_arbitrary_strategy_creates_400_agents():
    market = build_shared_market_population(
        firms(), [StrategySpec(s) for s in ("A", "B", "C", "AXXXX")]
    )
    assert len(market.clones) == 400
    assert market.strategy_roster[-1] == "AXXXX"
    assert sum(c.strategy_id == "AXXXX" for c in market.clones) == 100


def test_strategy_registration_is_not_hardcoded():
    market = build_shared_market_population(firms()[:1], [StrategySpec("1AXXXX")])
    assert len(market.clones) == 1
    assert market.clones[0].agent_id.endswith("::1AXXXX")


@pytest.mark.parametrize("names", [("A", "A"), ("",), (" A",), ("A::B",)])
def test_invalid_strategy_roster_rejected(names):
    with pytest.raises(ValueError):
        build_shared_market_population(firms()[:1], [StrategySpec(s) for s in names])


def test_duplicate_base_firms_rejected():
    base = firms()[0]
    with pytest.raises(ValueError, match="Duplicate base"):
        build_shared_market_population([base, base], [StrategySpec("A")])


def test_empty_population_or_roster_rejected():
    with pytest.raises(ValueError):
        build_shared_market_population([], [StrategySpec("A")])
    with pytest.raises(ValueError):
        build_shared_market_population(firms()[:1], [])


def test_construction_is_deterministic():
    first = build_shared_market_population(firms(), [StrategySpec("A"), StrategySpec("B")])
    second = build_shared_market_population(firms(), [StrategySpec("A"), StrategySpec("B")])
    assert first == second

"""Economic mechanism checks; numerical values are test-only scenarios."""
import pytest
from dataclasses import replace
from interfirm_abm.task_a6_market import A6Parameters, approved_profiles, run_a6_market
from interfirm_abm.task_l34_economics import (
    L34Parameters, effective_firm, capacity_limited, economic_extra_cost)
from interfirm_abm.task_based_firm import TaskAllocation
from interfirm_abm.task_strategy_engine import strategy_roster

def scenario():
    return L34Parameters(capacity_ratio=0.8, adjustment_unit_cost=2.,
                         efficiency_gain=0.25, adoption_fee=3.)

def identity(l3, l4):
    return next(x for x in strategy_roster() if x.L3 == l3 and x.L4 == l4
                and x.L5 == "competitive" and x.L6 == "optimization")

def test_parameters_required_and_validated():
    f = approved_profiles()[0]
    with pytest.raises(TypeError):
        run_a6_market(f, 1., A6Parameters(10., .01, .1, 1., .5, 1))
    with pytest.raises(ValueError):
        L34Parameters(0., 0., 0., 0.)
    with pytest.raises(ValueError):
        L34Parameters(1., -1., 0., 0.)

def test_l4_unlock_efficiency_and_combined():
    f = approved_profiles()[0]
    p = scenario()
    eligibility = effective_firm(f, "eligibility", p)
    efficiency = effective_firm(f, "efficiency", p)
    combined = effective_firm(f, "combined", p)
    for original, e, ef, both in zip(f.tasks, eligibility.tasks, efficiency.tasks, combined.tasks):
        assert e.automation_eligible
        assert ef.automation_eligible == original.automation_eligible
        assert both.automation_eligible
        assert e.capital_productivity == original.capital_productivity
        assert ef.capital_productivity == pytest.approx(original.capital_productivity * 1.25)
        assert both.capital_productivity == ef.capital_productivity

def test_l3_capacity_is_binding_at_task_level():
    f = approved_profiles()[0]
    p = scenario()
    plan = tuple(TaskAllocation(t.task_id, f.labor_endowment / 20, 0.) for t in f.tasks)
    limited = capacity_limited(plan, f, f, p)
    assert all(a.labor == pytest.approx(b.labor * .8) for a, b in zip(limited, plan))
    f.evaluate_allocation(list(limited))

def test_d3_adjustment_applies_to_all_strategies_from_zero_initial_inputs():
    f = approved_profiles()[0]
    p = scenario()
    old = tuple(TaskAllocation(t.task_id, .1, 0.) for t in f.tasks)
    new = tuple(TaskAllocation(t.task_id, .2, 0.) for t in f.tasks)
    for l3 in ("flexible", "capacity", "adjustment", "investment"):
        i = identity(l3, "eligibility")
        first, _, _ = economic_extra_cost(i, new, None, f, frozenset(), p,
            wage=1., rental=1., delta=.1, adoption_fee=.0025)
        later, _, _ = economic_extra_cost(i, new, old, f, frozenset(), p,
            wage=1., rental=1., delta=.1, adoption_fee=.0025)
        assert first == pytest.approx(.4)
        assert later == pytest.approx(.2)


def test_d3_adoption_fee_once_for_all_l4_strategies():
    f = approved_profiles()[0]
    task = f.tasks[0]
    plan = tuple(TaskAllocation(x.task_id, 0., .1 if x.task_id == task.task_id else 0.)
                 for x in f.tasks)
    for l4 in ("eligibility", "efficiency", "adoption_cost", "combined"):
        i = identity("flexible", l4)
        kw = dict(wage=1., rental=1., delta=.1, adoption_fee=.0025)
        _, fee, adopted = economic_extra_cost(i, plan, None, f, frozenset(), scenario(), **kw)
        assert fee == pytest.approx(.0025)
        assert adopted == frozenset({task.task_id})
        assert economic_extra_cost(i, plan, None, f, adopted, scenario(), **kw)[1] == 0


def test_runner_cost_identity_and_no_repeated_fee():
    f = approved_profiles()[0]
    i = identity("flexible", "combined")
    params = A6Parameters(100., .01, .1, 1., .5, 1, wage=1e-6, rental=1e-6)
    r = run_a6_market(f, 1., params, l34_parameters=scenario(), identities=(i,), rounds=3)
    assert len(r["players"]) == 3
    for row in r["players"]:
        assert row["profit"] == pytest.approx(row["price"] * row["quantity"] - row["cost"])
        assert row["adoption_cost"] >= 0
        assert row["adjustment_cost"] >= 0
    assert r["research_validated"] is False

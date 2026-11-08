"""Focused invariants for the new nine-strategy experimental runner."""
import pytest

from interfirm_abm.game1_nine_strategy import (
    ACTIONS, BUDGETS, Game1Params, adjustment, candidate,
    plan_cost, run_game1, strategy_ids, zero_plan, allocate,
)
from interfirm_abm.task_a5_normalized import technology_for_profile
from interfirm_abm.task_based_firm import TaskBasedFirm, TaskCapability, TaskAllocation


def firm():
    return TaskBasedFirm(
        "synthetic", 20., 20.,
        tuple(TaskCapability(f"T{i:02d}", 1. + i / 40., 2., True)
              for i in range(1, 21)),
    )


def params():
    return Game1Params(2., 0.01, 0.02, 0.02, 0.1, 0.01, 0.1, 0.1)


def test_roster_and_action_space():
    assert len(strategy_ids()) == 9
    assert len(ACTIONS) == 5
    assert len(BUDGETS) == 4


def test_adjustment_is_task_specific():
    before = zero_plan()
    before = (TaskAllocation("T01", 1., 0.),) + before[1:]
    after = (TaskAllocation("T01", 0., 0.),
             TaskAllocation("T02", 1., 0.)) + before[2:]
    assert adjustment(after, before, params()) > 0


def test_one_time_adoption_and_reentry():
    plan = (TaskAllocation("T01", 0., 1.),) + zero_plan()[1:]
    cost_first, new = plan_cost(plan, zero_plan(), frozenset(), params())
    assert new == frozenset({"T01"})
    cost_again, new_again = plan_cost(plan, zero_plan(), new, params())
    assert new_again == frozenset()
    assert cost_first - cost_again == pytest.approx(params().adoption_fee)


def test_no_automation():
    f = firm()
    tech = technology_for_profile(f, 1.)
    for l3 in ("uniform", "productivity", "cost_adjusted"):
        result = candidate(f, tech, l3, "no_automation", .48, 1.,
                           zero_plan(), frozenset(), params())
        assert all(a.capital == 0 for a in result[1])


def test_market_updates_and_reproducibility():
    f = firm()
    a = run_game1(f, 1., params(), rounds=2)
    b = run_game1(f, 1., params(), rounds=2)
    assert a == b
    assert len(a["players"]) == 18
    assert all(v == 2 for v in a["feedback_counts"].values())
    assert all(row["price"] == a["market"][row["round"] - 1]["price"]
               for row in a["players"])
    assert a["research_validated"] is False


def test_productivity_uses_entire_assigned_labor_budget():
    f = firm()
    tech = technology_for_profile(f, 1.)
    plan = allocate(f, tech, (False,) * 20, "productivity", .48,
                    1., zero_plan(), frozenset(), params())
    assert sum(a.labor for a in plan) == pytest.approx(.48 * f.labor_endowment, abs=1e-5)
    assert all(a.capital == 0 for a in plan)


def test_cost_adjusted_can_leave_expensive_resources_unused():
    f = firm()
    tech = technology_for_profile(f, 1.)
    p = Game1Params(2., .01, 10., 10., 0., 0., .1, .1)
    plan = allocate(f, tech, (False,) * 20, "cost_adjusted", .48,
                    1., zero_plan(), frozenset(), p)
    assert sum(a.labor for a in plan) < .48 * f.labor_endowment - 1e-4


def test_profit_based_is_single_task_local_optimum():
    f = firm()
    tech = technology_for_profile(f, 1.)
    p = params()
    best = candidate(f, tech, "uniform", "profit_based", .48, 1.,
                     zero_plan(), frozenset(), p)
    for j, task in enumerate(f.tasks):
        if not task.automation_eligible:
            continue
        modes = list(best[5])
        modes[j] = not modes[j]
        plan = allocate(f, tech, tuple(modes), "uniform", .48, 1.,
                        zero_plan(), frozenset(), p)
        q = tech.output_from_allocation(f, list(plan))
        cost, _ = plan_cost(plan, zero_plan(), frozenset(), p)
        assert q - cost <= best[0] + 1e-8


def test_cost_based_respects_automation_eligibility():
    f = firm()
    tech = technology_for_profile(f, 1.)
    result = candidate(f, tech, "uniform", "cost_based", .48, 1.,
                       zero_plan(), frozenset(), params())
    f.evaluate_allocation(list(result[1]))
    assert all(a.capital == 0 or task.automation_eligible
               for a, task in zip(result[1], f.tasks))


@pytest.mark.parametrize("sigma", [0.5, 1.0, 2.0])
@pytest.mark.parametrize("l3", ["productivity", "cost_adjusted"])
def test_optimizer_feasible_for_heterogeneous_task_modes(sigma, l3):
    f = TaskBasedFirm(
        "heterogeneous", 30., 18.,
        tuple(TaskCapability(f"T{i:02d}", .6 + i / 20.,
                             .8 + (21-i) / 9., i % 4 != 0)
              for i in range(1, 21)),
    )
    tech = technology_for_profile(f, sigma)
    modes = tuple(t.automation_eligible and j % 2 == 0
                  for j, t in enumerate(f.tasks))
    p = params()
    plan = allocate(f, tech, modes, l3, .66, 1.,
                    zero_plan(), frozenset(), p)
    f.evaluate_allocation(list(plan))
    labor = sum(a.labor for a in plan)
    capital = sum(a.capital for a in plan)
    assert labor <= .66 * f.labor_endowment + 1e-6
    assert capital <= .66 * f.capital_endowment + 1e-6
    assert all(not (a.labor > 0 and a.capital > 0) for a in plan)
    if l3 == "productivity":
        assert labor == pytest.approx(.66 * f.labor_endowment, abs=1e-5)
        assert capital == pytest.approx(.66 * f.capital_endowment, abs=1e-5)


def test_optimizer_handles_infeasible_intermediate_trial_without_budget_violation():
    """Optimizer objective must tolerate infeasible trial points; final result must not."""
    f = firm()
    tech = technology_for_profile(f, 1.0)
    for l3 in ("productivity", "cost_adjusted"):
        plan = allocate(f, tech, (False,) * 20, l3, .84, 1.,
                        zero_plan(), frozenset(), params())
        assert sum(a.labor for a in plan) <= .84 * f.labor_endowment + 1e-6
        f.evaluate_allocation(list(plan))


@pytest.mark.parametrize("sigma", [0.5, 1.0, 2.0])
def test_ai_mechanism_never_automates_ineligible_tasks(sigma):
    f = TaskBasedFirm(
        "ai_eligibility", 20., 20.,
        tuple(TaskCapability(f"T{i:02d}", 1., 3., i % 3 != 0)
              for i in range(1, 21)))
    tech = technology_for_profile(f, sigma)
    for l4 in ("no_automation", "cost_based", "profit_based"):
        value, plan, q, cost, newly_adopted, modes = candidate(
            f, tech, "uniform", l4, .48, 1., zero_plan(), frozenset(), params())
        f.evaluate_allocation(list(plan))
        assert all(not mode or task.automation_eligible
                   for mode, task in zip(modes, f.tasks))
        assert all(not (a.labor > 0 and a.capital > 0) for a in plan)
        assert newly_adopted == frozenset(
            a.task_id for a in plan if a.capital > 1e-9)
        if l4 == "no_automation":
            assert not newly_adopted
            assert all(not m for m in modes)


def test_solver_rejects_infeasible_reported_success(monkeypatch):
    """A solver's success flag cannot override firm-level budget feasibility."""
    import numpy as np
    import interfirm_abm.game1_nine_strategy as module
    from types import SimpleNamespace

    original = module.minimize
    seen = []
    def mocked(fun, x0, **kwargs):
        result = original(fun, x0, **kwargs)
        if not seen:
            seen.append("injected")
            return SimpleNamespace(success=True, x=np.full_like(x0, 1000.),
                                   fun=-1e9, message="injected false success")
        return result
    monkeypatch.setattr(module, "minimize", mocked)
    f = firm()
    plan = module.allocate(f, technology_for_profile(f, 1.), (False,) * 20,
                           "productivity", .48, 1., zero_plan(),
                           frozenset(), params())
    assert seen
    f.evaluate_allocation(list(plan))

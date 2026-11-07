"""Focused invariants for the new nine-strategy experimental runner."""
import pytest

from interfirm_abm.game1_nine_strategy import (
    ACTIONS, BUDGETS, Game1Params, adjustment, candidate,
    plan_cost, run_game1, strategy_ids, zero_plan,
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

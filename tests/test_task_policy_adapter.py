"""Task-policy bridge tests: hypothetical task plans, not approved production."""
from pathlib import Path

import pytest

from interfirm_abm.task_based_firm import load_approved_population
from interfirm_abm.task_bundle import TaskChoice
from interfirm_abm.task_execution import TaskUnitCosts
from interfirm_abm.task_strategy_population import StrategySpec, build_shared_market_population
from interfirm_abm.task_strategy_policy import DecisionContext, run_policy_market
from interfirm_abm.task_policy_adapter import adapt_task_plan_policy, evaluate_policy_task_plan

ROOT = Path(__file__).resolve().parents[1]


def population():
    firms = load_approved_population(
        ROOT / "data/firms/task_based_100_firms_profiles.csv",
        ROOT / "data/firms/task_based_100_firms_tasks.csv",
    )
    return build_shared_market_population(firms[:2], (StrategySpec("A"), StrategySpec("B")))


def labor_plan(ctx):
    return tuple(TaskChoice(task.task_id, "labor", 0.1) for task in ctx.clone.firm.tasks)


def aggregator(activities):
    return sum(activities.values())  # TEST FIXTURE ONLY; not approved economics


def test_task_plan_maps_K_L_and_cost_to_market():
    pop = population()
    policy = adapt_task_plan_policy(
        labor_plan, unit_costs=TaskUnitCosts(wage=2.0, capital_rental_rate=3.0),
        aggregate_tasks=aggregator,
    )
    result = run_policy_market(
        pop, number_of_rounds=2, policies={"A": policy, "B": policy},
        inverse_demand=lambda t, q: 5.0,
    )
    assert len(result.trajectories) == 4
    assert all(a.output == pytest.approx(2.0) for a in result.rounds[0].agents)
    assert all(a.total_cost >= 0 for a in result.rounds[0].agents)
    assert all(a.profit == pytest.approx(5 * a.output - a.total_cost) for a in result.rounds[0].agents)


def test_plan_exposes_input_allocation_and_rejects_infeasibility():
    pop = population()
    ctx = DecisionContext(0, pop.clones[0], ())
    result = evaluate_policy_task_plan(
        ctx, labor_plan(ctx), unit_costs=TaskUnitCosts(1, 2),
        aggregate_tasks=aggregator,
    )
    assert result.capital_used == 0
    assert result.labor_used > 0
    assert result.total_cost == pytest.approx(result.labor_used)
    excessive = tuple(TaskChoice(t.task_id, "labor", 1e9) for t in ctx.clone.firm.tasks)
    with pytest.raises(ValueError, match="Infeasible"):
        evaluate_policy_task_plan(
            ctx, excessive, unit_costs=TaskUnitCosts(1, 2),
            aggregate_tasks=aggregator,
        )


def test_no_auto_selection_or_preassigned_strategy_advantage():
    pop = population()
    policy = adapt_task_plan_policy(
        labor_plan, unit_costs=TaskUnitCosts(1, 1),
        aggregate_tasks=aggregator,
    )
    result = run_policy_market(
        pop, number_of_rounds=1, policies={"A": policy, "B": policy},
        inverse_demand=lambda t, q: 5.0,
    )
    for i in range(0, len(result.trajectories), 2):
        assert result.trajectories[i].profits == result.trajectories[i + 1].profits

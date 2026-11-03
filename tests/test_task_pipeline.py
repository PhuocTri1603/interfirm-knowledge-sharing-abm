"""Integration tests use synthetic inputs, not economic findings."""
import pytest
from interfirm_abm.task_based_firm import TaskBasedFirm, TaskCapability
from interfirm_abm.task_bundle import TaskChoice
from interfirm_abm.task_plan_selection import CandidatePlan
from interfirm_abm.task_economics import EconomicPrices
from interfirm_abm.task_pipeline import evaluate_local_neighborhood

def firm(k=10, l=10):
    return TaskBasedFirm("TEST", k, l, tuple(
        TaskCapability(f"T{j:02d}", 1, 2, j <= 5) for j in range(1, 21)))

def baseline(activity=0):
    return CandidatePlan("base", tuple(
        TaskChoice(f"T{j:02d}", "labor", activity) for j in range(1, 21)))

def evaluate(target, starting=0):
    return evaluate_local_neighborhood(
        target, baseline(starting), activity_step=1,
        aggregate_tasks=lambda q: sum(q.values()),
        prices=EconomicPrices(4, 2, 3))

def test_pipeline_scores_generated_candidates():
    result = evaluate(firm())
    assert result.generated_candidate_count == 26
    assert result.feasible_candidate_count == 26
    assert result.baseline_profit == pytest.approx(0)
    assert result.comparison.best_candidate_id == "base__T01__up"
    assert result.best_profit_gain_over_baseline == pytest.approx(1)

def test_infeasible_baseline_has_no_gain():
    result = evaluate(firm(k=0, l=0), starting=1)
    assert result.baseline_profit is None
    assert result.best_profit_gain_over_baseline is None
    assert result.feasible_candidate_count == 0

def test_deterministic():
    assert evaluate(firm()) == evaluate(firm())

def test_invalid_step():
    with pytest.raises(ValueError, match="activity_step"):
        evaluate_local_neighborhood(
            firm(), baseline(), activity_step=0,
            aggregate_tasks=lambda q: sum(q.values()),
            prices=EconomicPrices(4, 2, 3))

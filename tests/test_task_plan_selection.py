"""Tests for finite candidate ranking; test aggregator is not a model choice."""
import pytest

from interfirm_abm.task_based_firm import TaskBasedFirm, TaskCapability
from interfirm_abm.task_bundle import TaskChoice
from interfirm_abm.task_economics import EconomicPrices
from interfirm_abm.task_plan_selection import CandidatePlan, compare_candidate_plans


def firm():
    return TaskBasedFirm("FTEST", 5, 10, tuple(
        TaskCapability(f"T{j:02d}", 1, 2, j <= 5) for j in range(1, 21)
    ))


def candidate(cid, mode="labor", activity=0, adoption_cost=0):
    choices = tuple(TaskChoice(
        f"T{j:02d}", mode if j == 1 else "labor",
        activity if j == 1 else 0,
    ) for j in range(1, 21))
    return CandidatePlan(cid, choices, adoption_cost=adoption_cost)


def compare(candidates, prices=None):
    # A simple sum is deliberately injected only as a TEST STUB.
    return compare_candidate_plans(
        firm(), candidates,
        aggregate_tasks=lambda activities: sum(activities.values()),
        prices=prices or EconomicPrices(4, 2, 3),
    )


def test_ranks_feasible_plans():
    result = compare([candidate("zero"), candidate("labor", activity=4),
                      candidate("capital", mode="capital", activity=4)])
    assert result.best_candidate_id == "capital"
    assert result.best_profit == pytest.approx(12)
    assert len(result.results) == 3


def test_fixed_adoption_cost_can_reverse_ranking():
    result = compare([candidate("labor", activity=4),
                      candidate("capital", mode="capital", activity=4, adoption_cost=20)])
    assert result.best_candidate_id == "labor"


def test_resource_infeasible_candidate_excluded():
    result = compare([candidate("too_much", activity=20), candidate("zero")])
    assert not result.results[0].feasible
    assert result.results[0].profit is None
    assert result.best_candidate_id == "zero"


def test_all_infeasible_returns_no_selection():
    result = compare([candidate("a", activity=20), candidate("b", activity=30)])
    assert result.best_candidate_id is None
    assert result.best_profit is None


def test_tie_preserves_first_candidate():
    result = compare([candidate("first"), candidate("second")])
    assert result.best_candidate_id == "first"


def test_empty_or_duplicate_candidates_rejected():
    with pytest.raises(ValueError, match="At least one"):
        compare([])
    with pytest.raises(ValueError, match="unique"):
        compare([candidate("same"), candidate("same")])


def test_negative_adoption_cost_rejected():
    with pytest.raises(ValueError, match="adoption_cost"):
        compare([candidate("bad", adoption_cost=-1)])

"""Local candidate generation tests: not tests of behavioral rationality."""
import pytest
from interfirm_abm.task_based_firm import TaskBasedFirm, TaskCapability
from interfirm_abm.task_bundle import TaskChoice
from interfirm_abm.task_plan_selection import CandidatePlan
from interfirm_abm.task_candidate_generation import generate_local_candidates


def firm():
    return TaskBasedFirm("FTEST", 10, 10, tuple(
        TaskCapability(f"T{j:02d}", 1, 2, j <= 5) for j in range(1, 21)
    ))


def baseline(activity=0):
    return CandidatePlan("base", tuple(
        TaskChoice(f"T{j:02d}", "labor", activity) for j in range(1, 21)
    ), fixed_cost=2, adoption_cost=3)


def test_zero_baseline_one_step_candidates():
    plans = generate_local_candidates(firm(), baseline(), activity_step=1)
    assert len(plans) == 1 + 20 + 5
    assert plans[0] == baseline()
    assert len({p.candidate_id for p in plans}) == len(plans)
    assert all(p.fixed_cost == 2 and p.adoption_cost == 3 for p in plans)


def test_positive_baseline_has_down_neighbors():
    plans = generate_local_candidates(firm(), baseline(activity=2), activity_step=1)
    assert len(plans) == 1 + 20 + 20 + 5


def test_no_ineligible_capital():
    plans = generate_local_candidates(firm(), baseline(), activity_step=1)
    for plan in plans:
        assert all(c.mode == "labor" for c in plan.choices[5:])


def test_switches_can_be_disabled():
    plans = generate_local_candidates(
        firm(), baseline(), activity_step=1, include_mode_switches=False
    )
    assert len(plans) == 21


def test_invalid_step_rejected():
    with pytest.raises(ValueError, match="activity_step"):
        generate_local_candidates(firm(), baseline(), activity_step=0)


def test_invalid_baseline_rejected():
    bad = CandidatePlan("bad", baseline().choices[:-1])
    with pytest.raises(ValueError, match="20 unique"):
        generate_local_candidates(firm(), bad, activity_step=1)


def test_reproducible():
    a = generate_local_candidates(firm(), baseline(2), activity_step=0.5)
    b = generate_local_candidates(firm(), baseline(2), activity_step=0.5)
    assert a == b

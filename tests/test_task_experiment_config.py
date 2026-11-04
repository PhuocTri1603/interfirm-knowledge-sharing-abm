import pytest
from interfirm_abm.task_experiment_config import (
    ExperimentPlan, deterministic_seed, iter_plan_runs, preview_plan,
)


def test_full_design_has_one_run_per_cell_without_simulation():
    plan = ExperimentPlan("study", (), 1, 2026)
    runs = list(iter_plan_runs(plan))
    assert len(runs) == 12288
    assert len({r.market_id for r in runs}) == 12288
    assert all(r.execution_status == "not_executed" for r in runs)
    assert all(r.compatibility_status == "not_assessed" for r in runs)


def test_filter_and_replicate():
    plan = ExperimentPlan("pilot", (("L1", ("assignment",)), ("L7", ("separate",))), 3, 77)
    runs = list(iter_plan_runs(plan))
    assert len(runs) == 768 * 3
    assert len({r.market_id for r in runs}) == len(runs)
    assert {r.replication_id for r in runs} == {0, 1, 2}
    assert {r.population_regime for r in runs} == {"separate"}
    assert runs[:4] == list(iter_plan_runs(plan))[:4]


def test_deterministic_seed_is_stable_and_distinguishes_replications():
    a = deterministic_seed(42, "L1=assignment", 0)
    assert a == deterministic_seed(42, "L1=assignment", 0)
    assert a != deterministic_seed(42, "L1=assignment", 1)
    assert a != deterministic_seed(43, "L1=assignment", 0)


def test_preview_is_bounded():
    plan = ExperimentPlan("pilot", (), 100, 42)
    assert len(preview_plan(plan, 3)) == 3
    assert preview_plan(plan, 0) == ()


def test_reject_invalid_plan():
    with pytest.raises(ValueError):
        ExperimentPlan("", (), 1, 1)
    with pytest.raises(ValueError):
        ExperimentPlan("x", (), 0, 1)
    with pytest.raises(ValueError):
        ExperimentPlan("x", (("L1", ("unknown",)),), 1, 1)
    with pytest.raises(ValueError):
        ExperimentPlan("x", (("L1", ("assignment",)), ("L1", ("ces",))), 1, 1)
    with pytest.raises(ValueError):
        ExperimentPlan("x", (), 1, -1)

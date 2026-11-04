import pytest
from interfirm_abm.task_experiment_config import ExperimentPlan, preview_plan
from interfirm_abm.task_experiment_pipeline import register_planned_run


def planned(regime):
    plan = ExperimentPlan("pilot", (("L7", (regime,)),), 2, 123)
    return preview_plan(plan, 1)[0]


def test_separate_market_end_to_end():
    result = register_planned_run(
        planned("separate"), ("F1", "F2"),
        ex_ante_clusters={"F1": "labor", "F2": "capital"},
        cluster_definition_version="ex-ante-v1",
    )
    assert result.scenario.market_agent_ids == ("F1", "F2")
    assert result.scenario.specification_status == "not_yet_specified"
    assert result.scenario.seed == planned("separate").seed
    assert len(result.analysis_keys) == 4
    assert {m.cluster_timing for m in result.memberships} == {"ex_ante"}


def test_clones_require_explicit_mapping_and_preserve_identity():
    run = planned("clones")
    with pytest.raises(ValueError):
        register_planned_run(run, ("F1", "F2"))
    result = register_planned_run(
        run, ("F1", "F2"),
        agent_to_base=(("F1::A", "F1"), ("F1::B", "F1"), ("F2::A", "F2")),
    )
    assert len(result.scenario.market_agent_ids) == 3
    assert len(result.scenario.base_firm_ids) == 2
    assert result.memberships[1].base_firm_id == "F1"


def test_reject_missing_base_and_bad_cluster_coverage():
    with pytest.raises(ValueError):
        register_planned_run(planned("mixed"), ("F1", "F2"),
                             agent_to_base=(("a", "F1"), ("b", "F1")))
    with pytest.raises(ValueError):
        register_planned_run(planned("separate"), ("F1", "F2"),
                             ex_ante_clusters={"F1": "labor"},
                             cluster_definition_version="v1")


def test_deterministic_registration():
    run = planned("stratified")
    a = register_planned_run(run, ("F1", "F2"))
    b = register_planned_run(run, ("F1", "F2"))
    assert a == b
    assert a.scenario.population_regime == "stratified"

import pytest
from interfirm_abm.task_layer_registry import iter_strategies
from interfirm_abm.task_experiment_registry import (
    ExperimentScenario, FirmMembership, validate_memberships, reporting_keys,
)


def scenario(regime="separate", agents=("F1", "F2")):
    strategy = next(s for s in iter_strategies() if dict(s.choices)["L7"] == regime)
    return ExperimentScenario(
        "E1", "S1", "M1", strategy, 0, 42,
        ("F1", "F2"), agents, regime,
    )


def test_matched_population_provenance():
    s = scenario()
    members = (
        FirmMembership("S1", "F1", "F1", "labor", "baseline-v1", "ex_ante"),
        FirmMembership("S1", "F2", "F2", "capital", "baseline-v1", "ex_ante"),
    )
    validate_memberships(s, members)
    assert s.run_key == ("E1", "S1", "M1", 0)
    assert len(reporting_keys(s)) == 4
    assert len({k[1] for k in reporting_keys(s)}) == 1


def test_clone_market_preserves_base_identity():
    s = scenario("clones", ("F1::a", "F1::b", "F2::a"))
    members = (
        FirmMembership("S1", "F1::a", "F1"),
        FirmMembership("S1", "F1::b", "F1"),
        FirmMembership("S1", "F2::a", "F2"),
    )
    validate_memberships(s, members)
    assert len(s.market_agent_ids) == 3
    assert len(s.base_firm_ids) == 2


def test_reject_duplicate_nonclone_firm_and_missing_agent():
    s = scenario()
    with pytest.raises(ValueError):
        validate_memberships(s, (
            FirmMembership("S1", "F1", "F1"),
            FirmMembership("S1", "F2", "F1"),
        ))
    with pytest.raises(ValueError):
        validate_memberships(s, (FirmMembership("S1", "F1", "F1"),))


def test_reject_wrong_regime_and_invalid_cluster_provenance():
    with pytest.raises(ValueError):
        ExperimentScenario("E", "S", "M", scenario().strategy, 0, 0, ("F1",), ("F1",), "mixed")
    with pytest.raises(ValueError):
        FirmMembership("S", "F1", "F1", "labor", "v1", None)
    with pytest.raises(ValueError):
        FirmMembership("S", "F1", "F1", None, "v1", "ex_ante")

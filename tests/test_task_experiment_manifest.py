import json

import pytest

from interfirm_abm.task_experiment_manifest import (
    bind_researcher_initial_configurations,
    build_experiment_manifest,
    write_experiment_manifest,
)
from interfirm_abm.task_experiment_dimensions import strategy_player_ids


def test_full_manifest_has_400_runs_and_3072_players():
    manifest = build_experiment_manifest()
    assert manifest["status"] == "structure_only_no_economic_inputs"
    assert manifest["strategy_players"] == 3072
    assert len(manifest["strategy_player_ids"]) == 3072
    assert len(manifest["runs"]) == 400
    assert len({(r["market_design"], r["configuration_id"]) for r in manifest["runs"]}) == 400
    assert all(r["rounds"] == 200 for r in manifest["runs"])
    assert all(r["economic_inputs_status"] == "researcher_specification_required" for r in manifest["runs"])


def test_manifest_reproducible_and_exportable(tmp_path):
    path = tmp_path / "manifest.json"
    first = write_experiment_manifest(path)
    assert json.loads(path.read_text()) == first
    assert build_experiment_manifest() == first


def test_bind_researcher_rosters_requires_all_profiles_and_players():
    roster = dict.fromkeys(strategy_player_ids(), object())
    configs = {f"profile_{i:03d}": roster for i in range(1, 101)}
    assert bind_researcher_initial_configurations(configs) is configs
    with pytest.raises(ValueError, match="100 initial configurations"):
        bind_researcher_initial_configurations({"profile_001": roster})


def test_bind_researcher_rosters_rejects_wrong_profile_ids():
    roster = dict.fromkeys(strategy_player_ids(), None)
    configs = {f"profile_{i:03d}": roster for i in range(1, 100)}
    configs["unexpected"] = roster
    with pytest.raises(ValueError, match="deterministic manifest"):
        bind_researcher_initial_configurations(configs)


def test_manifest_does_not_invent_technology_or_firm_endowments():
    manifest = build_experiment_manifest()
    assert "researcher_inputs_required" in manifest
    assert "firm_endowments" not in manifest
    assert "inverse_demand" not in manifest
    assert "economic_results" not in manifest

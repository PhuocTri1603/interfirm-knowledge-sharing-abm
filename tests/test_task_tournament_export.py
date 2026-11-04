import csv
import json

import pytest

from interfirm_abm.task_tournament_export import export_tournament, TABLES


def fixture_result():
    return {
        "execution_status": "economic_models_injected_not_research_validated",
        "configuration_count": 1, "strategy_count": 1,
        "rounds_per_configuration": 1,
        "configuration_summaries": [dict(zip(TABLES["configuration_summaries"], ("C001", 1, 1, 2.0, "P1")))],
        "market_trajectory": [dict(zip(TABLES["market_trajectory"], ("C001", 1, 1, 1, 4, 2, 2, 4)))],
        "player_trajectory": [dict(zip(TABLES["player_trajectory"], ("C001", 1, "P1", "a", None, 1, 1, 4, 4, 1, 1, 2, 2, 2)))],
        "ranking_by_configuration": [dict(zip(TABLES["ranking_by_configuration"], ("C001", "P1", 2, 1)))],
    }


def test_export_writes_dashboard_tables_and_explicit_warning(tmp_path):
    paths = export_tournament(fixture_result(), tmp_path)
    assert set(paths) == {*TABLES, "manifest"}
    with paths["ranking_by_configuration"].open(newline="", encoding="utf-8") as handle:
        assert list(csv.DictReader(handle))[0]["player_id"] == "P1"
    manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    assert manifest["research_validated"] is False
    assert manifest["player_round_observations"] == 1
    assert manifest["tables"]["market_trajectory"]["rows"] == 1


def test_export_refuses_overwrite_unless_explicit(tmp_path):
    result = fixture_result()
    export_tournament(result, tmp_path)
    with pytest.raises(FileExistsError):
        export_tournament(result, tmp_path)
    export_tournament(result, tmp_path, overwrite=True)


def test_export_rejects_missing_or_extra_columns_without_writing(tmp_path):
    result = fixture_result()
    result["player_trajectory"][0]["invented"] = 1
    with pytest.raises(ValueError, match="schema"):
        export_tournament(result, tmp_path)
    assert not (tmp_path / "manifest.json").exists()


def test_export_rejects_unvalidated_status_and_missing_rows(tmp_path):
    result = fixture_result()
    result["execution_status"] = "scientific_results"
    with pytest.raises(ValueError, match="execution status"):
        export_tournament(result, tmp_path)
    result = fixture_result()
    result["ranking_by_configuration"] = []
    with pytest.raises(ValueError, match="ranking count"):
        export_tournament(result, tmp_path)

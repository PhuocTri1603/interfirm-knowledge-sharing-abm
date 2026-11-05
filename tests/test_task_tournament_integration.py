"""End-to-end Game 1 diagnostic pipeline: tournament -> dashboard JSON.

This test deliberately uses injected fixtures and MUST NOT be interpreted as
an approved economic experiment or a finding about optimal strategies.
"""
import json

from interfirm_abm.task_full_tournament import TournamentSpecification, run_full_tournament
from interfirm_abm.task_tournament_dashboard import write_tournament_dashboard
from test_task_full_tournament import configurations, market_factory, policy_factory


def test_tournament_to_dashboard_end_to_end(tmp_path):
    # One configuration and three rounds keep the CI integration check cheap.
    result = run_full_tournament(
        configurations(1),
        TournamentSpecification(market_factory, policy_factory, rounds=3,
                                expected_configurations=1),
    )
    target = tmp_path / "economic-results.json"
    write_tournament_dashboard(result, target)
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["players"] == 256
    assert payload["rounds"] == 3
    assert len(payload["configurations"]) == 1
    config = payload["configurations"][0]
    assert len(config["price_trajectory"]) == 3
    assert len(config["top_10"]) == 10
    assert len(config["player_trajectory"]) == 768
    assert payload["preview_only"] is False
    assert "ILLUSTRATIVE" in payload["warning"]
    assert all(row["cumulative_profit"] is not None for row in config["player_trajectory"])

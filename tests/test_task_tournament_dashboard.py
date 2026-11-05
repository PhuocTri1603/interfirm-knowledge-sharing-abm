import json

import pytest

from interfirm_abm.task_tournament_dashboard import (
    tournament_dashboard_payload, write_tournament_dashboard,
)


def example():
    return {
        "execution_status": "economic_models_injected_not_research_validated",
        "configuration_count": 1, "rounds_per_configuration": 2, "strategy_count": 2,
        "configuration_summaries": [{"config_id": "C01"}],
        "market_trajectory": [
            {"config_id": "C01", "round": t, "average_transaction_price": 4.0}
            for t in (1, 2)
        ],
        "ranking_by_configuration": [
            {"config_id": "C01", "player_id": p, "rank": rank, "total_benefit": 3.0}
            for rank, p in enumerate(("A", "B"), 1)
        ],
        "player_trajectory": [
            {"config_id": "C01", "round": t, "player_id": p,
             "cumulative_profit": float(t), "round_profit": 1.0,
             "produced_quantity": 2.0, "capital_used": 0.5, "labor_used": 1.0}
            for t in (1, 2) for p in ("A", "B")
        ],
    }


def test_dashboard_payload_matches_existing_site_contract(tmp_path):
    path = write_tournament_dashboard(example(), tmp_path / "economic-results.json")
    result = json.loads(path.read_text())
    assert result["players"] == 2 and result["rounds"] == 2
    assert result["status"] == "externally_injected_policies_not_research_validated"
    assert "ILLUSTRATIVE" in result["warning"]
    assert len(result["configurations"][0]["player_trajectory"]) == 4
    assert len(result["configurations"][0]["price_trajectory"]) == 2
    assert result["configurations"][0]["top_10"][0]["player_id"] == "A"
    assert result["preview_only"] is False


def test_dashboard_rejects_missing_rounds():
    data = example()
    data["market_trajectory"].pop()
    with pytest.raises(ValueError, match="market rounds"):
        tournament_dashboard_payload(data)


def test_dashboard_rejects_duplicate_player_round():
    data = example()
    data["player_trajectory"][1] = dict(data["player_trajectory"][0])
    with pytest.raises(ValueError, match="duplicate player-round"):
        tournament_dashboard_payload(data)


def test_dashboard_rejects_unpriced_round():
    data = example()
    data["market_trajectory"][0]["average_transaction_price"] = None
    with pytest.raises(ValueError, match="price chart"):
        tournament_dashboard_payload(data)


def test_dashboard_rejects_unapproved_status():
    data = example()
    data["execution_status"] = "validated"
    with pytest.raises(ValueError, match="provenance"):
        tournament_dashboard_payload(data)

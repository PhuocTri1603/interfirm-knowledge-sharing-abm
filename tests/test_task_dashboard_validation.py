import pytest

from interfirm_abm.task_dashboard_validation import validate_economic_dashboard


def sample(players=3072, rounds=200):
    return {
        "status": "externally_injected_policies_not_research_validated",
        "players": players, "rounds": rounds,
        "configurations": [{
            "id": "initial_001",
            "price_trajectory": [
                {"round": i, "price": 2.0, "market_quantity": 3.0,
                 "capital_used": 1.0, "labor_used": 2.0,
                 "total_production_cost": 1.0,
                 "output_concentration_hhi": 0.1}
                for i in range(1, rounds + 1)
            ],
            "top_10": [
                {"rank": i, "player_id": f"player_{i}", "total_benefit": float(11-i)}
                for i in range(1, min(10, players) + 1)
            ],
            "total_market_benefit": 100.0,
        }],
    }


def test_complete_3072_player_200_round_dashboard():
    validate_economic_dashboard(sample(), expected_configurations=1)


@pytest.mark.parametrize("field,value", [
    ("players", 3071), ("rounds", 199), ("status", "research_validated"),
])
def test_rejects_wrong_metadata(field, value):
    payload = sample()
    payload[field] = value
    with pytest.raises(ValueError):
        validate_economic_dashboard(payload)


def test_rejects_missing_round():
    payload = sample()
    payload["configurations"][0]["price_trajectory"].pop()
    with pytest.raises(ValueError, match="incomplete"):
        validate_economic_dashboard(payload)


def test_rejects_out_of_order_rounds():
    payload = sample()
    payload["configurations"][0]["price_trajectory"][0]["round"] = 2
    with pytest.raises(ValueError, match="consecutive"):
        validate_economic_dashboard(payload)


def test_rejects_nonfinite_price():
    payload = sample()
    payload["configurations"][0]["price_trajectory"][0]["price"] = float("nan")
    with pytest.raises(ValueError, match="invalid price"):
        validate_economic_dashboard(payload)


def test_rejects_inconsistent_ranking():
    payload = sample()
    payload["configurations"][0]["top_10"][1]["rank"] = 1
    with pytest.raises(ValueError, match="nonconsecutive"):
        validate_economic_dashboard(payload)


def test_rejects_wrong_configuration_count():
    with pytest.raises(ValueError, match="configuration count"):
        validate_economic_dashboard(sample(), expected_configurations=100)

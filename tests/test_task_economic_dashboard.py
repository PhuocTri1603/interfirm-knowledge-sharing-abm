import pytest

from interfirm_abm.task_economic_dashboard import economic_dashboard_payload, write_economic_dashboard
from interfirm_abm.task_economic_policy import EconomicSpecification, PlayerState, ProductionDecision
from interfirm_abm.task_economic_tournament import EconomicMarketConfiguration, run_economic_configuration


class ConstantPolicy:
    def decide(self, player, observation):
        return ProductionDecision(1, 0)


def example_result():
    config = EconomicMarketConfiguration(
        "scenario_a", {"one": PlayerState("one", 2, 2)},
        EconomicSpecification(
            output=lambda player, decision: decision.capital,
            cost=lambda player, decision: decision.capital,
            inverse_demand=lambda quantity: 5,
        ),
    )
    return run_economic_configuration(config, {"one": ConstantPolicy()}, 3)


def test_adapter_preserves_real_rounds_and_ranking():
    payload = economic_dashboard_payload([example_result()])
    assert payload["rounds"] == 3
    assert payload["players"] == 1
    assert len(payload["configurations"][0]["price_trajectory"]) == 3
    assert payload["configurations"][0]["top_10"][0]["total_benefit"] == 12


def test_adapter_writes_json(tmp_path):
    path = tmp_path / "data.json"
    payload = write_economic_dashboard(path, [example_result()])
    assert path.exists()
    assert '"scenario_a"' in path.read_text()
    assert payload["configurations"][0]["id"] == "scenario_a"


def test_adapter_rejects_incomplete_results():
    result = example_result()
    result["trajectory"].pop()
    with pytest.raises(ValueError, match="incomplete"):
        economic_dashboard_payload([result])


def test_dynamic_task_scenario_dashboard_export():
    result = {
        "config_id": "task_sample",
        "execution_status": "injected_task_policies_not_research_validated",
        "rounds": 1,
        "players": 1,
        "trajectory": [{
            "round": 1, "market_price": 5, "market_quantity": 2,
            "capital_used": 1, "labor_used": 1,
            "total_production_cost": 2, "output_concentration_hhi": 1,
        }],
        "ranking": [{"player_id": "p", "total_benefit": 8, "rank": 1}],
    }
    payload = economic_dashboard_payload([result])
    assert payload["configurations"][0]["price_trajectory"][0]["capital_used"] == 1
    assert "not_research_validated" in payload["status"]

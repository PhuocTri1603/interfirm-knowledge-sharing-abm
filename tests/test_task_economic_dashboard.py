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

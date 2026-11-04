import pytest

from interfirm_abm.task_economic_policy import (
    EconomicSpecification, PlayerState, ProductionDecision,
)
from interfirm_abm.task_economic_tournament import (
    EconomicMarketConfiguration, run_economic_configuration, run_economic_sequential,
)


class FixedPolicy:
    def __init__(self, capital):
        self.capital = capital

    def decide(self, player, observation):
        return ProductionDecision(self.capital, 0)


class AdaptivePolicy:
    def decide(self, player, observation):
        return ProductionDecision(1 if observation.last_market_price is None else 2, 0)


def configuration(name, intercept=10):
    return EconomicMarketConfiguration(
        name,
        {"a": PlayerState("a", 3, 3), "b": PlayerState("b", 3, 3)},
        EconomicSpecification(
            output=lambda player, decision: decision.capital + decision.labor,
            cost=lambda player, decision: decision.capital + decision.labor,
            inverse_demand=lambda quantity: max(0, intercept - quantity),
        ),
    )


def test_200_rounds_and_ranking():
    result = run_economic_configuration(
        configuration("one"), {"a": FixedPolicy(1), "b": FixedPolicy(2)}, 200
    )
    assert len(result["trajectory"]) == 200
    assert result["trajectory"][0]["market_quantity"] == 3
    assert result["trajectory"][0]["market_price"] == 7
    assert result["ranking"][0]["player_id"] == "b"
    assert result["ranking"][0]["total_benefit"] == 2400


def test_sequential_configuration_resets_and_changes_prices():
    policies = {"a": FixedPolicy(1), "b": FixedPolicy(2)}
    results = run_economic_sequential(
        (configuration("one"), configuration("two", 12)), policies, 2
    )
    assert results[0]["ranking"][0]["total_benefit"] == 24
    assert results[1]["ranking"][0]["total_benefit"] == 32
    assert results[0]["trajectory"][0]["market_price"] == 7
    assert results[1]["trajectory"][0]["market_price"] == 9


def test_observation_updates():
    result = run_economic_configuration(
        configuration("adaptive"), {"a": AdaptivePolicy(), "b": FixedPolicy(1)}, 3
    )
    assert [r["market_quantity"] for r in result["trajectory"]] == [2, 3, 3]


def test_missing_strategy_rejected():
    with pytest.raises(ValueError, match="strategy"):
        run_economic_configuration(configuration("bad"), {"a": FixedPolicy(1)})


def test_duplicate_configurations_rejected():
    policies = {"a": FixedPolicy(1), "b": FixedPolicy(1)}
    with pytest.raises(ValueError, match="unique"):
        run_economic_sequential(
            (configuration("same"), configuration("same")), policies
        )


def test_empty_configurations_rejected():
    with pytest.raises(ValueError, match="nonempty"):
        run_economic_sequential((), {})

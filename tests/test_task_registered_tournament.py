import pytest
from interfirm_abm.task_shared_market_game import player_ids
from interfirm_abm.task_economic_policy import EconomicSpecification, PlayerState, ProductionDecision
from interfirm_abm.task_economic_tournament import EconomicMarketConfiguration
from interfirm_abm.task_registered_tournament import run_registered_tournament

class Policy:
    def decide(self, player, observation):
        return ProductionDecision(1, 0)

def test_registered_tournament():
    identifier = player_ids()[0]
    scenario = EconomicMarketConfiguration(
        "sample", {identifier: PlayerState(identifier, 2, 2)},
        EconomicSpecification(
            output=lambda p, d: d.capital,
            cost=lambda p, d: d.capital,
            inverse_demand=lambda quantity: 5,
        ),
    )
    result = run_registered_tournament((scenario,), {identifier: Policy()}, 2)
    assert result[0]["ranking"][0]["total_benefit"] == 8

def test_registered_tournament_rejects_missing_policy():
    identifier = player_ids()[0]
    scenario = EconomicMarketConfiguration(
        "sample", {identifier: PlayerState(identifier, 2, 2)},
        EconomicSpecification(lambda p, d: 1, lambda p, d: 1, lambda q: 5),
    )
    with pytest.raises(ValueError):
        run_registered_tournament((scenario,), {}, 2)


def test_fresh_policies_do_not_leak_learning_memory():
    from interfirm_abm.task_registered_tournament import run_registered_tournament_with_fresh_policies

    class LearningPolicy:
        def __init__(self):
            self.experience = 0

        def decide(self, player, observation):
            self.experience += 1
            return ProductionDecision(1 if self.experience == 1 else 2, 0)

    identifier = player_ids()[0]
    spec = EconomicSpecification(
        lambda p, d: d.capital, lambda p, d: 0, lambda q: 10 - q
    )
    scenarios = (
        EconomicMarketConfiguration("first", {identifier: PlayerState(identifier, 2, 2)}, spec),
        EconomicMarketConfiguration("second", {identifier: PlayerState(identifier, 2, 2)}, spec),
    )
    result = run_registered_tournament_with_fresh_policies(
        scenarios, lambda config: {identifier: LearningPolicy()}, 2
    )
    assert [r["market_quantity"] for r in result[0]["trajectory"]] == [1, 2]
    assert [r["market_quantity"] for r in result[1]["trajectory"]] == [1, 2]

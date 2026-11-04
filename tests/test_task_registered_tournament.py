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

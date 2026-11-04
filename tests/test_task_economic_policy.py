import pytest

from interfirm_abm.task_economic_policy import (
    EconomicSpecification, MarketObservation, PlayerState,
    ProductionDecision, evaluate_joint_decisions,
)


def fixture():
    players = {
        "a": PlayerState("a", 5, 5),
        "b": PlayerState("b", 5, 5),
    }
    decisions = {
        "a": ProductionDecision(2, 1),
        "b": ProductionDecision(1, 2),
    }
    specification = EconomicSpecification(
        output=lambda p, d: d.capital + d.labor,
        cost=lambda p, d: 2 * d.capital + d.labor,
        inverse_demand=lambda q: 20 - q,
    )
    return players, decisions, specification


def test_shared_market_accounting_with_injected_functions():
    players, decisions, specification = fixture()
    result = evaluate_joint_decisions(players, decisions, specification)
    assert result["market_quantity"] == 6
    assert result["market_price"] == 14
    assert result["round_payoffs"] == {"a": 37, "b": 38}
    assert "not_validated_equilibrium" in result["execution_status"]


def test_rejects_missing_player_decision():
    players, decisions, specification = fixture()
    decisions.pop("b")
    with pytest.raises(ValueError, match="match"):
        evaluate_joint_decisions(players, decisions, specification)


def test_rejects_resource_infeasibility():
    players, decisions, specification = fixture()
    decisions["a"] = ProductionDecision(6, 0)
    with pytest.raises(ValueError, match="infeasible"):
        evaluate_joint_decisions(players, decisions, specification)


def test_rejects_invalid_price():
    players, decisions, specification = fixture()
    specification = EconomicSpecification(specification.output, specification.cost, lambda q: float("nan"))
    with pytest.raises(ValueError, match="market price"):
        evaluate_joint_decisions(players, decisions, specification)


def test_rejects_negative_inputs_and_invalid_round():
    with pytest.raises(ValueError):
        ProductionDecision(-1, 0)
    with pytest.raises(ValueError):
        MarketObservation(0, None, None)

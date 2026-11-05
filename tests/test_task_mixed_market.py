from random import Random

import pytest

from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm, TaskCapability
from interfirm_abm.task_mixed_market import MixedMarket, Sale, run_mixed_market
from interfirm_abm.task_strategy_engine import (
    Action, ComposedStrategyPolicy, DecisionParameters, strategy_roster,
)


def make_firm(player_id):
    tasks = tuple(TaskCapability(f"T{i:02d}", 1.0, 1.0, True) for i in range(1, 21))
    return TaskBasedFirm(player_id, 10.0, 10.0, tasks)


def candidates(strategy, firm, info):
    price = 3.0 if strategy.L5 == "price" else None
    return {"fixed": Action("fixed", tuple(TaskAllocation(f"T{i:02d}", .1, 0) for i in range(1, 21)),
                            offered_price=price)}


def valuation(strategy, firm, info, action):
    return 1.0


def policies(roster):
    return {
        identity.strategy_id: ComposedStrategyPolicy(
            identity, candidates, valuation, DecisionParameters(0.0, 1.0), Random(42),
            peer_provider=lambda firm, obs: ({firm.firm_id: "fixed"}, {firm.firm_id: 1.0}),
        )
        for identity in roster
    }


def market(roster, clearing, extra_cost=lambda key, action, round_number: 0.0):
    firms = {identity.strategy_id: make_firm(identity.strategy_id) for identity in roster}
    return MixedMarket(firms, lambda activity: sum(activity.values()), clearing, 1.0, 1.0, extra_cost)


def test_full_256_players_mixed_prices_and_quantities_200_rounds():
    roster = strategy_roster()
    assert len(roster) == 256
    def clear(round_number, offers):
        return {key: Sale(offer.available_quantity, offer.offered_price or 2.0)
                for key, offer in offers.items()}
    result = run_mixed_market(market(roster, clear), policies(roster), 200)
    assert result["players"] == 256
    assert len(result["ranking"]) == 256
    assert len(result["market_trajectory"]) == 200
    assert len(result["player_trajectory"]) == 256 * 200
    first = result["market_trajectory"][0]
    assert first["quantity_sold"] == pytest.approx(512)
    assert first["total_revenue"] == pytest.approx(1152)
    assert first["total_cost"] == pytest.approx(512)
    assert first["total_profit"] == pytest.approx(640)
    assert sum(r["round_profit"] for r in result["player_trajectory"]) == pytest.approx(640 * 200)


def test_reject_sale_above_production():
    roster = strategy_roster()[:1]
    def bad_clear(round_number, offers):
        return {key: Sale(offer.available_quantity + 1, 3) for key, offer in offers.items()}
    with pytest.raises(ValueError, match="more than produced"):
        run_mixed_market(market(roster, bad_clear), policies(roster), 1)


def test_reject_sale_below_price_offer():
    roster = [next(x for x in strategy_roster() if x.L5 == "price")]
    def bad_clear(round_number, offers):
        return {key: Sale(1, 2) for key in offers}
    with pytest.raises(ValueError, match="below"):
        run_mixed_market(market(roster, bad_clear), policies(roster), 1)


def test_reject_incomplete_clearing():
    roster = strategy_roster()[:2]
    with pytest.raises(ValueError, match="exactly one sale"):
        run_mixed_market(market(roster, lambda r, offers: {}), policies(roster), 1)


def test_extra_cost_is_charged_explicitly():
    roster = strategy_roster()[:1]
    def clear(r, offers):
        return {key: Sale(1, 4) for key in offers}
    result = run_mixed_market(market(roster, clear, lambda key, action, round_number: 1.5), policies(roster), 1)
    assert result["ranking"][0]["total_benefit"] == pytest.approx(.5)

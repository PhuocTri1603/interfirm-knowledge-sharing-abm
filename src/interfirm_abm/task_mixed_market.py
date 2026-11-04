"""Mixed price/quantity Game 1 market: explicit clearing and accounting contracts.

No implicit demand allocation, price formation, investment depreciation,
production aggregator or calibration. All 256 player identities may coexist.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import fsum, isclose, isfinite
from typing import Callable, Mapping, Protocol

from interfirm_abm.task_based_firm import TaskBasedFirm
from interfirm_abm.task_economic_policy import MarketObservation
from interfirm_abm.task_strategy_engine import Action, ComposedStrategyPolicy


@dataclass(frozen=True)
class SupplyOffer:
    player_id: str
    available_quantity: float
    offered_price: float | None

    def __post_init__(self):
        if not self.player_id or not isfinite(self.available_quantity) or self.available_quantity < 0:
            raise ValueError("invalid supply offer")
        if self.offered_price is not None and (not isfinite(self.offered_price) or self.offered_price < 0):
            raise ValueError("invalid offered price")


@dataclass(frozen=True)
class Sale:
    quantity: float
    unit_price: float

    def __post_init__(self):
        if not isfinite(self.quantity) or not isfinite(self.unit_price) or self.quantity < 0 or self.unit_price < 0:
            raise ValueError("invalid sale")


class ClearingRule(Protocol):
    def __call__(self, round_number: int, offers: Mapping[str, SupplyOffer]) -> Mapping[str, Sale]: ...


@dataclass(frozen=True)
class MixedMarket:
    firms: Mapping[str, TaskBasedFirm]
    aggregate_tasks: Callable[[Mapping[str, float]], float]
    clearing: ClearingRule
    capital_unit_cost: float
    labor_unit_cost: float
    # Explicit extra cost, e.g. investment/adoption cost: callback prevents
    # assuming these fields are always charged one-for-one.
    extra_cost: Callable[[str, Action, int], float]

    def __post_init__(self):
        if not self.firms or any(key != firm.firm_id for key, firm in self.firms.items()):
            raise ValueError("nonempty firm roster keyed by player ID required")
        if any(not isfinite(x) or x < 0 for x in (self.capital_unit_cost, self.labor_unit_cost)):
            raise ValueError("unit costs must be finite and nonnegative")


def run_mixed_market(market: MixedMarket,
                     policies: Mapping[str, ComposedStrategyPolicy],
                     rounds: int = 200) -> dict:
    if rounds < 1 or set(market.firms) != set(policies):
        raise ValueError("positive rounds and complete policy roster required")
    totals = {key: 0.0 for key in market.firms}
    market_rows, player_rows = [], []
    observation = MarketObservation(1, None, None)
    for round_number in range(1, rounds + 1):
        # Simultaneous decisions: no current-round sales information is revealed.
        actions, offers, inputs, costs = {}, {}, {}, {}
        for key, firm in market.firms.items():
            action = policies[key].decide_action(firm, observation)
            activity = firm.evaluate_allocation(list(action.allocation))
            output = float(market.aggregate_tasks(activity))
            if not isfinite(output) or output < 0:
                raise ValueError("invalid production output")
            capital = fsum(a.capital for a in action.allocation)
            labor = fsum(a.labor for a in action.allocation)
            added_cost = float(market.extra_cost(key, action, round_number))
            if not isfinite(added_cost) or added_cost < 0:
                raise ValueError("invalid extra cost")
            actions[key] = action
            offers[key] = SupplyOffer(key, output, action.offered_price)
            inputs[key] = (capital, labor)
            costs[key] = market.capital_unit_cost * capital + market.labor_unit_cost * labor + added_cost
        sales = dict(market.clearing(round_number, offers))
        if set(sales) != set(offers):
            raise ValueError("clearing must return exactly one sale per player")
        for key, sale in sales.items():
            if not isinstance(sale, Sale):
                raise TypeError("clearing must return Sale objects")
            if sale.quantity > offers[key].available_quantity + 1e-9:
                raise ValueError("cannot sell more than produced")
            if offers[key].offered_price is not None and sale.quantity > 0 and sale.unit_price + 1e-9 < offers[key].offered_price:
                raise ValueError("sale price below player's stated offer")
        realized = {}
        for key in market.firms:
            sale = sales[key]
            revenue = sale.quantity * sale.unit_price
            payoff = revenue - costs[key]
            if not isfinite(payoff):
                raise ValueError("nonfinite payoff")
            realized[key] = payoff
            totals[key] += payoff
            player_rows.append({
                "round": round_number, "player_id": key, "action_id": actions[key].action_id,
                "offered_price": actions[key].offered_price,
                "produced_quantity": offers[key].available_quantity,
                "sold_quantity": sale.quantity, "realized_unit_price": sale.unit_price,
                "revenue": revenue, "capital_used": inputs[key][0],
                "labor_used": inputs[key][1], "production_and_extra_cost": costs[key],
                "round_profit": payoff, "cumulative_profit": totals[key],
            })
        total_quantity = fsum(s.quantity for s in sales.values())
        total_revenue = fsum(s.quantity * s.unit_price for s in sales.values())
        total_cost = fsum(costs.values())
        total_profit = fsum(realized.values())
        if not isclose(total_profit, total_revenue - total_cost, rel_tol=1e-9, abs_tol=1e-8):
            raise ValueError("market accounting identity failed")
        market_rows.append({
            "round": round_number, "quantity_sold": total_quantity,
            "quantity_produced": fsum(o.available_quantity for o in offers.values()),
            "total_revenue": total_revenue, "total_cost": total_cost,
            "total_profit": total_profit,
            "average_transaction_price": total_revenue / total_quantity if total_quantity else None,
        })
        for key in policies:
            policies[key].observe_payoff(market.firms[key], round_number, realized[key])
        # Volume-weighted average is an observable statistic, NOT a common
        # market-clearing price or a requirement that firms charge the same price.
        observation = MarketObservation(
            round_number + 1,
            total_revenue / total_quantity if total_quantity else None,
            total_quantity,
        )
    ranking = sorted(
        ({"player_id": key, "total_benefit": value} for key, value in totals.items()),
        key=lambda item: (-item["total_benefit"], item["player_id"]),
    )
    for rank, row in enumerate(ranking, 1):
        row["rank"] = rank
    return {
        "rounds": rounds, "players": len(market.firms),
        "market_trajectory": market_rows, "player_trajectory": player_rows,
        "ranking": ranking,
        "execution_status": "externally_injected_clearing_and_cost_not_research_validated",
    }

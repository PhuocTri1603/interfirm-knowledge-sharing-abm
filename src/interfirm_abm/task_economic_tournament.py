"""Repeated shared-market accounting with externally supplied strategy policies.

Every initial configuration starts fresh. No economic technology, market
calibration, or strategy behavior is selected by this orchestration layer.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from interfirm_abm.task_economic_policy import (
    EconomicSpecification, EconomicStrategy, MarketObservation, PlayerState,
    evaluate_joint_decisions,
)


@dataclass(frozen=True)
class EconomicMarketConfiguration:
    config_id: str
    players: Mapping[str, PlayerState]
    specification: EconomicSpecification

    def __post_init__(self) -> None:
        if not self.config_id or not self.players:
            raise ValueError("configuration ID and player roster are required")


def run_economic_configuration(
    configuration: EconomicMarketConfiguration,
    strategies: Mapping[str, EconomicStrategy],
    rounds: int = 200,
) -> dict:
    if rounds <= 0:
        raise ValueError("rounds must be positive")
    if set(strategies) != set(configuration.players):
        raise ValueError("every player must have exactly one strategy")
    # Copy the initial states: never carry cumulative profits into another run.
    states = {
        key: PlayerState(p.player_id, p.capital_endowment, p.labor_endowment, 0.0)
        for key, p in configuration.players.items()
    }
    observations = MarketObservation(1, None, None)
    trajectories = []
    for t in range(1, rounds + 1):
        decisions = {
            key: strategies[key].decide(state, observations)
            for key, state in states.items()
        }
        result = evaluate_joint_decisions(states, decisions, configuration.specification)
        for key, state in tuple(states.items()):
            states[key] = PlayerState(
                state.player_id, state.capital_endowment, state.labor_endowment,
                state.cumulative_profit + result["round_payoffs"][key],
            )
        outputs = result["player_outputs"]
        market_quantity = result["market_quantity"]
        concentration_hhi = (
            sum((quantity / market_quantity) ** 2 for quantity in outputs.values())
            if market_quantity > 0 else None
        )
        trajectories.append({
            "round": t,
            "market_quantity": result["market_quantity"],
            "market_price": result["market_price"],
            "round_total_profit": sum(result["round_payoffs"].values()),
            "capital_used": sum(decision.capital for decision in decisions.values()),
            "labor_used": sum(decision.labor for decision in decisions.values()),
            "total_production_cost": sum(result["player_costs"].values()),
            "output_concentration_hhi": concentration_hhi,
        })
        observations = MarketObservation(
            t + 1, result["market_price"], result["market_quantity"]
        )
    ranking = sorted(
        ({"player_id": key, "total_benefit": state.cumulative_profit}
         for key, state in states.items()),
        key=lambda row: (-row["total_benefit"], row["player_id"]),
    )
    for i, row in enumerate(ranking, 1):
        row["rank"] = i
    return {
        "config_id": configuration.config_id,
        "rounds": rounds,
        "players": len(states),
        "trajectory": trajectories,
        "ranking": ranking,
        "execution_status": "injected_policies_not_research_validated",
    }


def run_economic_sequential(
    configurations: tuple[EconomicMarketConfiguration, ...],
    strategies: Mapping[str, EconomicStrategy],
    rounds: int = 200,
) -> list[dict]:
    if not configurations or len({c.config_id for c in configurations}) != len(configurations):
        raise ValueError("configurations must be nonempty with unique IDs")
    return [run_economic_configuration(c, strategies, rounds) for c in configurations]

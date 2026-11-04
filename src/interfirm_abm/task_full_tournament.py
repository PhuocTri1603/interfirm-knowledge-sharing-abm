"""Full-sample Game 1 orchestration; economic specifications are injected.

100 independent initial configurations x 256 strategy identities x 200 rounds.
No implicit task technology, market clearing, behavioral valuation, or L7 choice.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

from interfirm_abm.task_based_firm import TaskBasedFirm
from interfirm_abm.task_experiment_dimensions import (
    DEFAULT_INITIAL_CONFIGURATIONS, DEFAULT_ROUNDS, strategy_player_ids,
)
from interfirm_abm.task_mixed_market import MixedMarket, run_mixed_market
from interfirm_abm.task_strategy_engine import ComposedStrategyPolicy


MarketFactory = Callable[[str, Mapping[str, TaskBasedFirm]], MixedMarket]
PolicyFactory = Callable[[str, MixedMarket], Mapping[str, ComposedStrategyPolicy]]


@dataclass(frozen=True)
class TournamentSpecification:
    market_factory: MarketFactory
    policy_factory: PolicyFactory
    rounds: int = DEFAULT_ROUNDS
    expected_configurations: int = DEFAULT_INITIAL_CONFIGURATIONS

    def __post_init__(self):
        if self.rounds <= 0 or self.expected_configurations <= 0:
            raise ValueError("rounds and expected configurations must be positive")


def run_full_tournament(
    configurations: Mapping[str, Mapping[str, TaskBasedFirm]],
    specification: TournamentSpecification,
) -> dict:
    """Run each configuration independently, with fresh policies and market.

    Caller must supply all economic models. No synthetic research findings are
    created by this orchestrator.
    """
    if len(configurations) != specification.expected_configurations:
        raise ValueError(f"expected {specification.expected_configurations} configurations")
    expected_players = frozenset(strategy_player_ids())
    if len(expected_players) != 256:
        raise ValueError("canonical strategy roster must contain 256 identities")
    all_market_rows = []
    all_player_rows = []
    all_rankings = []
    summaries = []
    retained_policies = []
    seen_policy_ids = set()
    for config_id, roster in configurations.items():
        if not isinstance(config_id, str) or not config_id.strip():
            raise ValueError("configuration IDs must be nonempty")
        if len(roster) != 256 or frozenset(roster) != expected_players:
            raise ValueError(f"{config_id}: requires all 256 distinct strategy players")
        market = specification.market_factory(config_id, roster)
        if set(market.firms) != expected_players:
            raise ValueError("market factory must preserve complete strategy roster")
        policies = dict(specification.policy_factory(config_id, market))
        if set(policies) != expected_players:
            raise ValueError("policy factory must provide all 256 players")
        # Prevent learning-history leakage across independently run scenarios.
        if len({id(policy) for policy in policies.values()}) != len(policies):
            raise ValueError("policy objects cannot be shared within a configuration")
        if any(id(policy) in seen_policy_ids for policy in policies.values()):
            raise ValueError("policy objects cannot be reused between configurations")
        # Retain strong references: otherwise Python may recycle object IDs,
        # producing false positives for freshly constructed policies.
        retained_policies.extend(policies.values())
        seen_policy_ids.update(map(id, policies.values()))
        for player_id, policy in policies.items():
            if policy.identity.strategy_id != player_id:
                raise ValueError("policy identity mismatch")
        result = run_mixed_market(market, policies, rounds=specification.rounds)
        if len(result["player_trajectory"]) != 256 * specification.rounds:
            raise ValueError("missing player-round observations")
        all_market_rows.extend({"config_id": config_id, **row} for row in result["market_trajectory"])
        all_player_rows.extend({"config_id": config_id, **row} for row in result["player_trajectory"])
        all_rankings.extend({"config_id": config_id, **row} for row in result["ranking"])
        summaries.append({
            "config_id": config_id,
            "players": 256,
            "rounds": specification.rounds,
            "market_total_profit": sum(row["total_profit"] for row in result["market_trajectory"]),
            "highest_ranked_player": result["ranking"][0]["player_id"],
        })
    return {
        "configuration_count": len(configurations),
        "strategy_count": 256,
        "rounds_per_configuration": specification.rounds,
        "player_round_observations": len(all_player_rows),
        "configuration_summaries": summaries,
        "market_trajectory": all_market_rows,
        "player_trajectory": all_player_rows,
        "ranking_by_configuration": all_rankings,
        "execution_status": "economic_models_injected_not_research_validated",
    }

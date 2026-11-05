from random import Random

import pytest

from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm, TaskCapability
from interfirm_abm.task_experiment_dimensions import strategy_player_ids
from interfirm_abm.task_full_tournament import TournamentSpecification, run_full_tournament
from interfirm_abm.task_mixed_market import MixedMarket, Sale
from interfirm_abm.task_strategy_engine import (
    Action, ComposedStrategyPolicy, DecisionParameters, strategy_roster,
)


def configurations(n=100):
    tasks = tuple(TaskCapability(f"T{i:02d}", 1, 1, True) for i in range(1, 21))
    return {
        f"C{config:03d}": {
            player: TaskBasedFirm(player, 10, 10, tasks)
            for player in strategy_player_ids()
        }
        for config in range(n)
    }


def market_factory(config_id, roster):
    # Explicit test-only stub: not an approved scientific market specification.
    def clearing(round_number, offers):
        return {key: Sale(offer.available_quantity, offer.offered_price or 2)
                for key, offer in offers.items()}
    return MixedMarket(roster, lambda activity: sum(activity.values()),
                       clearing, 1, 1, lambda key, action, round_number: 0)


def action_factory(identity, firm, info):
    return {"fixed": Action(
        "fixed",
        tuple(TaskAllocation(f"T{i:02d}", .1, 0) for i in range(1, 21)),
        offered_price=3 if identity.L5 == "price" else None,
    )}


def policy_factory(config_id, market):
    return {
        identity.strategy_id: ComposedStrategyPolicy(
            identity, action_factory, lambda *args: 1.0,
            DecisionParameters(0, 1), Random(17),
            peer_provider=lambda firm, obs: ({firm.firm_id: "fixed"}, {firm.firm_id: 1}),
        )
        for identity in strategy_roster()
    }


def test_full_100_configurations_all_256_players():
    result = run_full_tournament(
        configurations(),
        TournamentSpecification(market_factory, policy_factory, rounds=2),
    )
    assert result["configuration_count"] == 100
    assert result["strategy_count"] == 256
    assert len(result["configuration_summaries"]) == 100
    assert len(result["ranking_by_configuration"]) == 25600
    assert result["player_round_observations"] == 51200
    assert len(result["market_trajectory"]) == 200
    assert all(row["market_total_profit"] == pytest.approx(1280)
               for row in result["configuration_summaries"])


def test_reject_missing_initial_configuration():
    with pytest.raises(ValueError, match="expected 100"):
        run_full_tournament(
            configurations(99),
            TournamentSpecification(market_factory, policy_factory),
        )


def test_reject_incomplete_player_roster():
    configs = configurations()
    configs["C000"].pop(next(iter(configs["C000"])))
    with pytest.raises(ValueError, match="256 distinct"):
        run_full_tournament(
            configs,
            TournamentSpecification(market_factory, policy_factory, rounds=1),
        )


def test_scientific_mode_blocks_unresolved_strategy_semantics():
    with pytest.raises(ValueError, match="16 unresolved strategy semantics"):
        run_full_tournament(
            configurations(1),
            TournamentSpecification(
                market_factory, policy_factory, rounds=1,
                expected_configurations=1, require_scientific_readiness=True,
            ),
        )


def test_diagnostic_mode_never_claims_scientific_readiness():
    result = run_full_tournament(
        configurations(1),
        TournamentSpecification(market_factory, policy_factory, rounds=1, expected_configurations=1),
    )
    assert result["scientific_readiness"] is False
    assert result["execution_status"] == "economic_models_injected_not_research_validated"

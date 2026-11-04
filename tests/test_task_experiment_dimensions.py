import pytest

from interfirm_abm.task_experiment_dimensions import (
    experiment_dimensions, market_designs, strategy_player_ids,
    validate_experiment_rosters,
)


def test_canonical_dimensions():
    dimensions = experiment_dimensions()
    assert dimensions.strategy_players == 256
    assert dimensions.market_designs == 4
    assert dimensions.catalog_combinations == 1024
    assert dimensions.initial_configurations == 100
    assert dimensions.rounds_per_configuration == 200
    assert dimensions.player_configuration_runs_per_design == 25600
    assert dimensions.player_round_decisions_per_design == 5120000
    assert dimensions.player_round_decisions_all_designs == 20480000
    assert market_designs() == ("separate", "mixed", "clones", "stratified")


def test_strategy_ids_unique_and_exclude_l7():
    players = strategy_player_ids()
    assert len(players) == len(set(players)) == 256
    assert all("L6=" in player and "L7=" not in player and "L1=" not in player and "L2=" not in player for player in players)


def test_validates_100_complete_configuration_rosters():
    roster = dict.fromkeys(strategy_player_ids(), None)
    configurations = {f"profile_{i:03d}": roster for i in range(1, 101)}
    validate_experiment_rosters(configurations)


def test_rejects_missing_initial_configuration():
    roster = dict.fromkeys(strategy_player_ids(), None)
    with pytest.raises(ValueError, match="100 initial configurations"):
        validate_experiment_rosters({"profile_001": roster})


def test_rejects_incomplete_strategy_roster():
    roster = dict.fromkeys(strategy_player_ids()[:-1], None)
    configurations = {f"profile_{i:03d}": roster for i in range(1, 101)}
    with pytest.raises(ValueError, match="all 256"):
        validate_experiment_rosters(configurations)


def test_rejects_nonpositive_dimensions():
    with pytest.raises(ValueError):
        experiment_dimensions(initial_configurations=0)

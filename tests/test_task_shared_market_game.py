import pytest
from interfirm_abm.task_shared_market_game import (
    InitialConfiguration, PROXY_STATUS, player_ids, run_configuration, run_sequential,
)


def test_l7_is_not_duplicated_as_player():
    ids = player_ids()
    assert len(ids) == 256
    assert len(set(ids)) == len(ids)
    assert all("L7=" not in name for name in ids)


def test_200_round_shared_market_and_rankings():
    panel, ranking = run_configuration(InitialConfiguration("A"), selected_players=player_ids()[:3])
    assert len(panel) == 600
    assert len(ranking) == 3
    assert {r["round"] for r in panel} == set(range(1, 201))
    assert len({r["market_price"] for r in panel}) == 1
    assert all(r["market_quantity"] == 3 for r in panel)
    assert sorted(r["rank"] for r in ranking) == [1, 2, 3]


def test_sequential_configurations_reset_and_keep_identity():
    players = player_ids()[:2]
    configs = (InitialConfiguration("A"), InitialConfiguration("B", demand_intercept=25))
    panel, ranking = run_sequential(configs, selected_players=players)
    assert len(panel) == 800
    assert len(ranking) == 4
    assert {r["config_id"] for r in ranking} == {"A", "B"}
    assert {r["round"] for r in panel if r["config_id"] == "B"} == set(range(1, 201))
    assert {r["player_id"] for r in ranking if r["config_id"] == "A"} == set(players)


def test_deterministic_and_explicit_proxy_status():
    cfg = InitialConfiguration("A")
    players = player_ids()[:3]
    assert run_configuration(cfg, selected_players=players) == run_configuration(cfg, selected_players=players)
    _, ranks = run_configuration(cfg, selected_players=players)
    assert all(r["execution_status"] == PROXY_STATUS for r in ranks)


def test_invalid_rosters_and_configurations():
    with pytest.raises(ValueError):
        run_configuration(InitialConfiguration("A"), selected_players=())
    with pytest.raises(ValueError):
        run_configuration(InitialConfiguration("A"), selected_players=("not-a-policy",))
    with pytest.raises(ValueError):
        run_configuration(InitialConfiguration("A"), rounds=0, selected_players=player_ids()[:1])
    with pytest.raises(ValueError):
        run_sequential((InitialConfiguration("A"), InitialConfiguration("A")), selected_players=player_ids()[:1])

import pytest
from interfirm_abm.task_shared_market_game import player_ids
from interfirm_abm.task_policy_binding import parse_player_identity, validate_policy_roster

def test_all_player_ids():
    ids = player_ids()
    assert len(ids) == 3072
    assert all(len(parse_player_identity(i)) == 6 for i in ids)

def test_missing_policy_rejected():
    with pytest.raises(ValueError):
        validate_policy_roster(player_ids()[:1], {})

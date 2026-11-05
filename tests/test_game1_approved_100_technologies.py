"""The 100 Game 1 configurations must exactly reuse the approved population."""
from pathlib import Path

from interfirm_abm.task_based_firm import load_approved_population
from interfirm_abm.task_multi_action_diagnostic import configurations


def test_all_100_configurations_match_approved_production_technologies():
    root = Path(__file__).resolve().parents[1] / "data" / "firms"
    approved = load_approved_population(
        root / "task_based_100_firms_profiles.csv",
        root / "task_based_100_firms_tasks.csv",
    )
    actual = configurations(100)
    assert list(actual) == [f"C{i:03d}" for i in range(100)]
    assert len({firm.tasks for firm in approved}) == 100
    for i, source in enumerate(approved):
        roster = actual[f"C{i:03d}"]
        assert len(roster) == 256
        for player_id, player in roster.items():
            assert player.firm_id == player_id
            assert player.capital_endowment == source.capital_endowment
            assert player.labor_endowment == source.labor_endowment
            assert player.tasks == source.tasks


def test_partial_configurations_use_approved_prefix():
    assert configurations(1)["C000"][next(iter(configurations(1)["C000"]))].capital_endowment == 66.22

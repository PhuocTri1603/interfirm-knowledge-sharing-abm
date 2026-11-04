from pathlib import Path

import pytest

from interfirm_abm.task_based_firm import TaskCapability
from interfirm_abm.task_initial_profile_bridge import load_initial_economic_profiles
from interfirm_abm.task_profile_strategy_roster import build_profile_strategy_roster


SOURCE = Path(__file__).resolve().parents[1] / "data/firms/firm_profiles_100.csv"


def test_same_original_endowments_for_all_strategy_players():
    profile = load_initial_economic_profiles(SOURCE)[0]
    def researcher_supplied_tasks(profile):
        return tuple(TaskCapability(f"T{i:02d}", 1.0, 1.0, True) for i in range(1, 21))
    roster = build_profile_strategy_roster(profile, task_capability_factory=researcher_supplied_tasks)
    assert len(roster) == 256
    assert len({id(firm) for firm in roster.values()}) == 3072
    assert {firm.capital_endowment for firm in roster.values()} == {profile.capital_endowment}
    assert {firm.labor_endowment for firm in roster.values()} == {profile.labor_endowment}
    assert all(len(firm.tasks) == 20 for firm in roster.values())


def test_missing_researcher_task_specification_fails():
    profile = load_initial_economic_profiles(SOURCE)[0]
    with pytest.raises(TypeError, match="researcher-supplied"):
        build_profile_strategy_roster(profile, task_capability_factory=None)

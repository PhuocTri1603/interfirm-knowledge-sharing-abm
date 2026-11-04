import json

import pytest

from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm, TaskCapability
from interfirm_abm.task_strategy_tournament import export_strategy_configuration_tournament


PLAYER = "L1=assignment|L2=linear|L3=flexible|L4=eligibility|L5=competitive|L6=optimization"


class FixedTaskPolicy:
    def decide_tasks(self, firm, observation):
        return tuple(TaskAllocation(f"T{i:02d}", 0, 0.05) for i in range(1, 21))


def make_firm():
    return TaskBasedFirm(
        PLAYER, 3, 3,
        tuple(TaskCapability(f"T{i:02d}", 1, 2, True) for i in range(1, 21)),
    )


def test_independent_configurations_export_200_rounds(tmp_path):
    created = []
    def factory(config, player, firm):
        created.append((config, player))
        return FixedTaskPolicy()

    path = tmp_path / "economic-results.json"
    payload = export_strategy_configuration_tournament(
        path,
        {"profile_a": {PLAYER: make_firm()}, "profile_b": {PLAYER: make_firm()}},
        aggregate_tasks=lambda activities: sum(activities.values()),
        inverse_demand=lambda quantity: 10 - quantity,
        capital_unit_cost=1,
        labor_unit_cost=1,
        policy_factory=factory,
        rounds=200,
    )
    assert len(created) == 2
    assert {config for config, _ in created} == {"profile_a", "profile_b"}
    assert payload["players"] == 1
    assert payload["rounds"] == 200
    assert len(payload["configurations"]) == 2
    assert len(payload["configurations"][0]["price_trajectory"]) == 200
    assert json.loads(path.read_text()) == payload
    assert "not_research_validated" in payload["status"]


def test_configuration_player_rosters_must_match(tmp_path):
    with pytest.raises(ValueError, match="same strategy players"):
        export_strategy_configuration_tournament(
            tmp_path / "out.json",
            {"a": {PLAYER: make_firm()}, "b": {PLAYER.replace("L6=optimization", "L6=softmax"): TaskBasedFirm(PLAYER.replace("L6=optimization", "L6=softmax"), 3, 3, make_firm().tasks)}},
            aggregate_tasks=sum,
            inverse_demand=lambda quantity: 10,
            capital_unit_cost=1,
            labor_unit_cost=1,
            policy_factory=lambda config, player, firm: FixedTaskPolicy(),
        )


def test_rejects_unregistered_player_label(tmp_path):
    with pytest.raises(ValueError):
        export_strategy_configuration_tournament(
            tmp_path / "out.json",
            {"a": {"arbitrary": make_firm()}},
            aggregate_tasks=sum,
            inverse_demand=lambda quantity: 10,
            capital_unit_cost=1,
            labor_unit_cost=1,
            policy_factory=lambda config, player, firm: FixedTaskPolicy(),
        )


def test_rejects_reused_policy_instance_across_configurations(tmp_path):
    shared_policy = FixedTaskPolicy()
    with pytest.raises(ValueError, match="fresh policy object"):
        export_strategy_configuration_tournament(
            tmp_path / "out.json",
            {"a": {PLAYER: make_firm()}, "b": {PLAYER: make_firm()}},
            aggregate_tasks=lambda activities: sum(activities.values()),
            inverse_demand=lambda quantity: 10 - quantity,
            capital_unit_cost=1,
            labor_unit_cost=1,
            policy_factory=lambda config, player, firm: shared_policy,
            rounds=2,
        )
    assert not (tmp_path / "out.json").exists()

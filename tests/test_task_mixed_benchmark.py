from pathlib import Path

import pytest

from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm, TaskCapability
from interfirm_abm.task_mixed_benchmark import MixedMarketSpecification, run_mixed_benchmark


P1 = "L3=flexible|L4=eligibility|L5=competitive|L6=optimization"
P2 = P1.replace("L6=optimization", "L6=softmax")


class FixedPolicy:
    def decide_tasks(self, firm, observation):
        return tuple(TaskAllocation(f"T{i:02d}", 0.0, 0.05) for i in range(1, 21))


def firm(player):
    return TaskBasedFirm(player, 2, 2, tuple(
        TaskCapability(f"T{i:02d}", 1.0, 1.0, True) for i in range(1, 21)
    ))


def spec():
    return MixedMarketSpecification(
        aggregate_tasks=lambda activities: sum(activities.values()),
        inverse_demand=lambda quantity: max(0.0, 10.0 - quantity),
        capital_unit_cost=1,
        labor_unit_cost=1,
        policy_factory=lambda config, player, economic_firm: FixedPolicy(),
    )


def test_two_players_compete_in_same_endogenous_price_market(tmp_path):
    output = tmp_path / "mixed.json"
    result = run_mixed_benchmark(
        output, {"profile_001": {P1: firm(P1), P2: firm(P2)}},
        spec(), rounds=2, require_full_experiment=False,
    )
    assert output.exists()
    assert result["players"] == 2
    assert result["rounds"] == 2
    assert len(result["configurations"]) == 1
    trajectory = result["configurations"][0]["price_trajectory"]
    assert len(trajectory) == 2
    assert trajectory[0]["price"] == pytest.approx(8.0)


def test_full_benchmark_rejects_partial_profiles(tmp_path):
    with pytest.raises(ValueError, match="100 original configuration IDs"):
        run_mixed_benchmark(tmp_path / "mixed.json", {"profile_001": {P1: firm(P1)}}, spec())

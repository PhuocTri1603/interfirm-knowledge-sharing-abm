import pytest

from interfirm_abm.task_based_firm import TaskBasedFirm, TaskCapability
from interfirm_abm.task_strategy_market import build_strategy_market, require_strategy_policies


def test_market_roster_is_not_automatically_multiplied_by_initial_profiles():
    firms = {
        name: TaskBasedFirm(
            name, 3, 3,
            tuple(TaskCapability(f"T{i:02d}", 1, 2, True) for i in range(1, 21)),
        )
        for name in ("strategy-a", "strategy-b")
    }
    market = build_strategy_market(
        firms,
        aggregate_tasks=lambda activities: sum(activities.values()),
        inverse_demand=lambda quantity: 10 - quantity,
        capital_unit_cost=1,
        labor_unit_cost=1,
    )
    assert len(market.firms) == 2
    with pytest.raises(TypeError):
        require_strategy_policies(market, lambda name, firm: None)


def test_rejects_mismatched_player_ids():
    firm = TaskBasedFirm(
        "real-id", 3, 3,
        tuple(TaskCapability(f"T{i:02d}", 1, 2, True) for i in range(1, 21)),
    )
    with pytest.raises(ValueError):
        build_strategy_market(
            {"wrong-id": firm},
            aggregate_tasks=sum,
            inverse_demand=lambda quantity: 1,
            capital_unit_cost=1,
            labor_unit_cost=1,
        )

import pytest
from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm, TaskCapability
from interfirm_abm.task_dynamic_market import DynamicTaskMarket, run_dynamic_task_market


class ChangingPolicy:
    def decide_tasks(self, firm, observation):
        capital = 0.05 * observation.round_number
        return tuple(TaskAllocation(f"T{i:02d}", 0, capital) for i in range(1, 21))


def test_dynamic_allocation_changes_market_quantity_and_price():
    firm = TaskBasedFirm(
        "p", 3, 3,
        tuple(TaskCapability(f"T{i:02d}", 1, 2, True) for i in range(1, 21)),
    )
    market = DynamicTaskMarket(
        {"p": firm}, lambda activities: sum(activities.values()),
        lambda quantity: 10 - quantity, 1, 1,
    )
    result = run_dynamic_task_market(market, {"p": ChangingPolicy()}, rounds=2)
    assert [row["capital_used"] for row in result["trajectory"]] == pytest.approx([1, 2])
    assert [row["market_quantity"] for row in result["trajectory"]] == pytest.approx([2, 4])
    assert [row["market_price"] for row in result["trajectory"]] == pytest.approx([8, 6])
    assert result["ranking"][0]["total_benefit"] == pytest.approx(37)


def test_rejects_missing_task_policy():
    firm = TaskBasedFirm(
        "p", 3, 3,
        tuple(TaskCapability(f"T{i:02d}", 1, 2, True) for i in range(1, 21)),
    )
    market = DynamicTaskMarket({"p": firm}, sum, lambda quantity: 1, 1, 1)
    with pytest.raises(ValueError):
        run_dynamic_task_market(market, {}, rounds=1)


def test_scenarios_reset_policy_memory():
    from interfirm_abm.task_dynamic_market import run_dynamic_task_scenarios

    firm = TaskBasedFirm(
        "p", 3, 3,
        tuple(TaskCapability(f"T{i:02d}", 1, 2, True) for i in range(1, 21)),
    )
    market = DynamicTaskMarket(
        {"p": firm}, lambda activities: sum(activities.values()),
        lambda quantity: 10 - quantity, 1, 1,
    )
    results = run_dynamic_task_scenarios(
        {"first": market, "second": market},
        lambda config_id, current: {"p": ChangingPolicy()},
        rounds=2,
    )
    assert [r["config_id"] for r in results] == ["first", "second"]
    assert results[0]["trajectory"] == results[1]["trajectory"]


def test_market_accounting_identity_each_round():
    firm = TaskBasedFirm(
        "p", 3, 3,
        tuple(TaskCapability(f"T{i:02d}", 1, 2, True) for i in range(1, 21)),
    )
    market = DynamicTaskMarket(
        {"p": firm}, lambda activities: sum(activities.values()),
        lambda quantity: 10 - quantity, 1, 1,
    )
    result = run_dynamic_task_market(market, {"p": ChangingPolicy()}, rounds=2)
    for row in result["trajectory"]:
        assert row["round_total_revenue"] - row["total_production_cost"] == pytest.approx(
            row["round_total_profit"]
        )
    assert sum(row["round_total_profit"] for row in result["trajectory"]) == pytest.approx(
        result["ranking"][0]["total_benefit"]
    )

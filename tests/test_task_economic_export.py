import json
import pytest

from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm, TaskCapability
from interfirm_abm.task_dynamic_market import DynamicTaskMarket
from interfirm_abm.task_economic_export import export_dynamic_task_results


class TestAllocationPolicy:
    def decide_tasks(self, firm, observation):
        amount = 0.05 * observation.round_number
        return tuple(TaskAllocation(f"T{i:02d}", 0, amount) for i in range(1, 21))


def test_end_to_end_task_export(tmp_path):
    firm = TaskBasedFirm(
        "sample", 3, 3,
        tuple(TaskCapability(f"T{i:02d}", 1, 2, True) for i in range(1, 21)),
    )
    market = DynamicTaskMarket(
        {"sample": firm}, lambda activities: sum(activities.values()), lambda q: 10 - q, 1, 1
    )
    path = tmp_path / "economic-results.json"
    result = export_dynamic_task_results(
        path,
        {"configuration_a": market, "configuration_b": market},
        lambda config_id, current: {"sample": TestAllocationPolicy()},
        rounds=2,
    )
    assert path.exists()
    disk = json.loads(path.read_text(encoding="utf-8"))
    assert disk == result
    assert result["rounds"] == 2
    assert result["players"] == 1
    assert len(result["configurations"]) == 2
    assert result["configurations"][0]["price_trajectory"][1]["market_quantity"] == pytest.approx(4)
    assert result["configurations"][0]["total_market_benefit"] == pytest.approx(37)
    assert "not_research_validated" in result["status"]

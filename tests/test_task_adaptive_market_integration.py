"""Integration checks only: illustrative parameters are not research results."""
from random import Random

import pytest

from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm, TaskCapability
from interfirm_abm.task_adaptive_policies import (
    AdaptivePolicySpecification, adaptive_optimization, adaptive_softmax,
)
from interfirm_abm.task_dynamic_market import DynamicTaskMarket, run_dynamic_task_market


def test_two_adaptive_players_compete_in_shared_market_for_200_rounds():
    firms = {
        name: TaskBasedFirm(
            name, 3, 3,
            tuple(TaskCapability(f"T{i:02d}", 1, 2, True) for i in range(1, 21)),
        )
        for name in ("optimization", "softmax")
    }
    plans = {
        "low": tuple(TaskAllocation(f"T{i:02d}", 0, 0.05) for i in range(1, 21)),
        "high": tuple(TaskAllocation(f"T{i:02d}", 0, 0.1) for i in range(1, 21)),
    }
    spec = AdaptivePolicySpecification(
        candidates=lambda firm, obs: plans,
        output=lambda firm, plan: 2 * sum(a.capital for a in plan),
        cost=lambda firm, plan: 1.5 * sum(a.capital for a in plan),
        initial_expected_price=3,
        adjustment_rate=1,
    )
    policies = {
        "optimization": adaptive_optimization(spec),
        "softmax": adaptive_softmax(spec, temperature=0.001, rng=Random(21)),
    }
    market = DynamicTaskMarket(
        firms,
        lambda activities: sum(activities.values()),
        lambda q: 8.5 - q,
        capital_unit_cost=1.5,
        labor_unit_cost=0,
    )
    result = run_dynamic_task_market(market, policies, rounds=200)
    assert result["rounds"] == 200
    assert result["players"] == 2
    assert len(result["trajectory"]) == 200
    assert result["trajectory"][0]["market_quantity"] == pytest.approx(8)
    assert result["trajectory"][1]["market_quantity"] == pytest.approx(4)
    assert result["trajectory"][2]["market_quantity"] == pytest.approx(8)
    assert sum(item["total_benefit"] for item in result["ranking"]) == pytest.approx(
        sum(row["round_total_profit"] for row in result["trajectory"])
    )
    assert result["execution_status"] == "injected_task_policies_not_research_validated"

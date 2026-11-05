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


def test_payoff_feedback_is_delivered_after_simultaneous_decisions():
    firm = TaskBasedFirm(
        "p", 3, 3,
        tuple(TaskCapability(f"T{i:02d}", 1, 2, True) for i in range(1, 21)),
    )
    class FeedbackPolicy(ChangingPolicy):
        def __init__(self):
            self.received = []
        def decide_tasks(self, firm, observation):
            assert len(self.received) == observation.round_number - 1
            return super().decide_tasks(firm, observation)
        def observe_payoff(self, firm, round_number, payoff):
            self.received.append((round_number, payoff))
    policy = FeedbackPolicy()
    market = DynamicTaskMarket(
        {"p": firm}, lambda a: sum(a.values()), lambda q: 10 - q, 1, 1
    )
    result = run_dynamic_task_market(market, {"p": policy}, rounds=2)
    assert [t for t, _ in policy.received] == [1, 2]
    assert sum(p for _, p in policy.received) == pytest.approx(
        result["ranking"][0]["total_benefit"]
    )


def test_player_trajectory_reconciles_each_round_and_final_ranking():
    firm = TaskBasedFirm('p', 3, 3, tuple(TaskCapability(f'T{i:02d}', 1, 2, True) for i in range(1, 21)))
    market = DynamicTaskMarket({'p': firm}, lambda a: sum(a.values()), lambda q: 10 - q, 1, 1)
    result = run_dynamic_task_market(market, {'p': ChangingPolicy()}, rounds=2)
    panel = result['player_trajectory']
    assert [p['round'] for p in panel] == [1, 2]
    assert [p['capital_used'] for p in panel] == pytest.approx([1, 2])
    assert [p['labor_used'] for p in panel] == pytest.approx([0, 0])
    assert [p['output'] for p in panel] == pytest.approx([2, 4])
    assert panel[0]['cumulative_profit'] == pytest.approx(panel[0]['round_profit'])
    assert panel[-1]['cumulative_profit'] == pytest.approx(result['ranking'][0]['total_benefit'])


def test_distinct_behavioral_mechanisms_shared_market_200_rounds():
    from interfirm_abm.task_behavioral_experiment import run_behavioral_experiment
    first = run_behavioral_experiment()
    second = run_behavioral_experiment()
    assert first == second
    assert first["rounds"] == 200
    assert first["players"] == 2
    assert len(first["trajectory"]) == 200
    assert len(first["player_trajectory"]) == 400
    assert set(first["learning_action_counts"]) == {"low", "medium", "high"}
    assert sum(first["learning_action_counts"].values()) == 200
    assert first["experiment_status"] == "controlled_unvalidated_behavioral_comparison"
    assert first["assumptions"]["information"] == "myopic uses lagged market price; learner uses only own payoff"
    assert {x["player_id"] for x in first["ranking"]} == {"myopic_forecast", "own_payoff_learning"}
    for round_number in range(1, 201):
        records = [p for p in first["player_trajectory"] if p["round"] == round_number]
        assert len(records) == 2
        assert records[0]["market_price"] == records[1]["market_price"]


def test_behavioral_experiment_rejects_invalid_exploration():
    from interfirm_abm.task_behavioral_experiment import run_behavioral_experiment
    import pytest
    with pytest.raises(ValueError, match="epsilon"):
        run_behavioral_experiment(rounds=2, epsilon=1.5)

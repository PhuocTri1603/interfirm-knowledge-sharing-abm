"""Controlled economic decision-mechanism comparison.

Two genuinely distinct information rules:
- myopic best response: maximize forecast profit using last observed market price;
- reinforcement: epsilon-greedy sample-mean learning from own realized profit only.

Common technology, feasible actions, demand and input prices. This is an
explicitly parameterized sensitivity experiment, not a calibrated finding.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from random import Random

from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm, TaskCapability
from interfirm_abm.task_dynamic_market import DynamicTaskMarket, run_dynamic_task_market


@dataclass
class MyopicBestResponse:
    market: DynamicTaskMarket
    plans: dict[str, tuple[TaskAllocation, ...]]
    initial_price: float

    def decide_tasks(self, firm, observation):
        price = self.initial_price if observation.market_price is None else observation.market_price
        scores = {}
        for name, plan in self.plans.items():
            output = self.market.aggregate_tasks(firm.evaluate_allocation(list(plan)))
            cost = sum(a.capital * self.market.capital_unit_cost + a.labor * self.market.labor_unit_cost for a in plan)
            scores[name] = price * output - cost
        return self.plans[sorted(scores, key=lambda k: (-scores[k], k))[0]]


@dataclass
class OwnPayoffReinforcement:
    plans: dict[str, tuple[TaskAllocation, ...]]
    epsilon: float
    rng: Random
    history: dict[str, list[float]] = field(default_factory=dict)
    pending: str | None = None

    def __post_init__(self):
        if not 0 <= self.epsilon <= 1:
            raise ValueError("epsilon must be between 0 and 1")

    def decide_tasks(self, firm, observation):
        untried = [k for k in sorted(self.plans) if not self.history.get(k)]
        if untried:
            choice = untried[0]
        elif self.rng.random() < self.epsilon:
            choice = self.rng.choice(sorted(self.plans))
        else:
            means = {k: sum(v) / len(v) for k, v in self.history.items()}
            choice = sorted(means, key=lambda k: (-means[k], k))[0]
        self.pending = choice
        return self.plans[choice]

    def observe_payoff(self, firm, round_number, payoff):
        if self.pending is None or not isfinite(payoff):
            raise ValueError("feedback must follow a decision and be finite")
        self.history.setdefault(self.pending, []).append(float(payoff))
        self.pending = None


def run_behavioral_experiment(rounds=200, seed=17, epsilon=0.1):
    tasks = tuple(TaskCapability(f"T{i:02d}", 1.0, 1.0, True) for i in range(1, 21))
    firms = {
        "myopic_forecast": TaskBasedFirm("myopic_forecast", 2, 2, tasks),
        "own_payoff_learning": TaskBasedFirm("own_payoff_learning", 2, 2, tasks),
    }
    market = DynamicTaskMarket(
        firms, lambda activity: sum(activity.values()),
        lambda quantity: max(0.0, 10.0 - quantity), 1.0, 1.0,
    )
    plans = {
        "low": tuple(TaskAllocation(f"T{i:02d}", 0, 0) for i in range(1, 21)),
        "medium": tuple(TaskAllocation(f"T{i:02d}", 0, 0.05) for i in range(1, 21)),
        "high": tuple(TaskAllocation(f"T{i:02d}", 0, 0.1) for i in range(1, 21)),
    }
    learner = OwnPayoffReinforcement(plans, epsilon, Random(seed))
    result = run_dynamic_task_market(market, {
        "myopic_forecast": MyopicBestResponse(market, plans, 10.0),
        "own_payoff_learning": learner,
    }, rounds)
    result["experiment_status"] = "controlled_unvalidated_behavioral_comparison"
    result["assumptions"] = {
        "seed": seed, "epsilon": epsilon, "initial_expected_price": 10.0,
        "demand": "P=max(0,10-Q)", "task_aggregator": "sum",
        "unit_input_costs": {"capital": 1.0, "labor": 1.0},
        "candidate_capital_per_task": [0.0, 0.05, 0.1],
        "technology": "identical 20 tasks, equal endowments and productivity",
        "information": "myopic uses lagged market price; learner uses only own payoff",
    }
    result["learning_action_counts"] = {k: len(v) for k, v in learner.history.items()}
    return result

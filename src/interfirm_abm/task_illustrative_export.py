"""Explicitly illustrative Game 1 scenario; not calibrated research evidence.

Run: python -m interfirm_abm.task_illustrative_export site/economic-results.json
All numerical choices below are transparent demonstration fixtures.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from random import Random

from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm, TaskCapability
from interfirm_abm.task_decision_rules import FiniteChoiceOptimization
from interfirm_abm.task_learning_choices import SoftmaxChoice
from interfirm_abm.task_dynamic_market import DynamicTaskMarket
from interfirm_abm.task_economic_export import export_dynamic_task_results


IDS = (
    "L3=flexible|L4=eligibility|L5=competitive|L6=optimization",
    "L3=flexible|L4=eligibility|L5=competitive|L6=softmax",
)


def illustrative_market():
    tasks = tuple(TaskCapability(f"T{i:02d}", 1.0, 1.0, True) for i in range(1, 21))
    firms = {name: TaskBasedFirm(name, 2.0, 2.0, tasks) for name in IDS}
    return DynamicTaskMarket(
        firms,
        aggregate_tasks=lambda activities: sum(activities.values()),
        inverse_demand=lambda quantity: max(0.0, 10.0 - quantity),
        capital_unit_cost=1.0,
        labor_unit_cost=1.0,
    )


def illustrative_policies(config_id, market):
    def candidates(firm, observation):
        return {
            "high": tuple(TaskAllocation(f"T{i:02d}", 0.0, 0.1) for i in range(1, 21)),
            "low": tuple(TaskAllocation(f"T{i:02d}", 0.0, 0.0) for i in range(1, 21)),
        }

    def scores(firm, observation, name, plan):
        return 2.0 if name == "high" else 0.0

    return {
        IDS[0]: FiniteChoiceOptimization(candidates, scores),
        IDS[1]: SoftmaxChoice(candidates, scores, 100.0, Random(17)),
    }


def export_illustrative_results(path: str | Path, rounds: int = 200) -> dict:
    if rounds <= 0:
        raise ValueError("rounds must be positive")
    payload = export_dynamic_task_results(
        path,
        {"illustrative_shared_technology": illustrative_market()},
        illustrative_policies,
        rounds=rounds,
    )
    payload["warning"] = (
        "ILLUSTRATIVE FIXTURE ONLY: arbitrary demand, task aggregation, input costs, "
        "choice scores and temperature. Not calibrated, approved, or research-validated."
    )
    # Persist the explicit caveat alongside the exported numerical records.
    import json
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="JSON output path (e.g. site/economic-results.json)")
    parser.add_argument("--rounds", type=int, default=200)
    args = parser.parse_args()
    payload = export_illustrative_results(args.output, args.rounds)
    print(f"Illustrative export: {payload['rounds']} rounds, {payload['players']} players, {args.output}")


if __name__ == "__main__":
    main()

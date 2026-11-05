"""Executable L3/L4/L5 decision mechanisms for Game 1 diagnostic runs.

These are explicit *illustrative behavioral specifications*, not calibrated
Acemoglu–Restrepo equilibrium, and not researcher-validated parameters.
L6 selection/learning is implemented by ComposedStrategyPolicy.
"""
from __future__ import annotations

from math import fsum
from interfirm_abm.task_based_firm import TaskAllocation
from interfirm_abm.task_strategy_engine import Action

# Shared action IDs allow lagged imitation across heterogeneous strategy players.
INTENSITIES = (0.30, 0.48, 0.66, 0.84)


def _weights(identity, firm, info):
    tasks = firm.tasks
    if identity.L3 == "flexible":
        return [1.0] * 20
    if identity.L3 == "capacity":
        return [max(t.labor_productivity, t.capital_productivity if t.automation_eligible else 0) for t in tasks]
    if identity.L3 == "adjustment":
        # Lagged own experience changes the task priority, not hidden rival information.
        shift = (len(info.own_history) % 20)
        return [1.0 + (i == shift) for i in range(20)]
    if identity.L3 == "investment":
        return [1.0 + float(t.automation_eligible) for t in tasks]
    raise ValueError("unknown L3")


def _capital_priority(identity, task):
    if not task.automation_eligible:
        return False
    if identity.L4 == "eligibility":
        return True
    if identity.L4 == "efficiency":
        return task.capital_productivity > task.labor_productivity
    if identity.L4 == "adoption_cost":
        # Capital must clear a higher productivity hurdle in this diagnostic.
        return task.capital_productivity > 1.25 * task.labor_productivity
    if identity.L4 == "combined":
        return task.capital_productivity > 1.10 * task.labor_productivity
    raise ValueError("unknown L4")


def build_actions(identity, firm, info):
    weights = _weights(identity, firm, info)
    total = fsum(weights)
    results = {}
    for index, intensity in enumerate(INTENSITIES):
        # L3 chooses task emphasis; L4 determines capital-eligible execution.
        # L3 investment prioritizes capital-capable tasks, without inventing
        # persistent capital accumulation or an unapproved investment cost.
        capital_tasks = [i for i, t in enumerate(firm.tasks) if _capital_priority(identity, t)]
        labor_tasks = [i for i in range(20) if i not in capital_tasks]
        if identity.L3 == "flexible":
            # Candidate-specific task-mode variation allows genuine mode switching.
            capital_tasks = [i for i in capital_tasks if (i + index) % 4 != 0]
            labor_tasks = [i for i in range(20) if i not in capital_tasks]
        elif identity.L3 == "adjustment":
            # Own lagged outcome changes the proposed mode at the margin.
            capital_tasks = [i for i in capital_tasks if (i + len(info.own_history)) % 5 != 0]
            labor_tasks = [i for i in range(20) if i not in capital_tasks]
        elif identity.L3 == "investment":
            # More capital-intensive candidates at higher effort.
            capital_tasks = [i for i in capital_tasks if index >= 1 or i % 2 == 0]
            labor_tasks = [i for i in range(20) if i not in capital_tasks]
        kw = fsum(weights[i] for i in capital_tasks)
        lw = fsum(weights[i] for i in labor_tasks)
        allocations = []
        for i, task in enumerate(firm.tasks):
            if i in capital_tasks:
                k = firm.capital_endowment * intensity * weights[i] / kw if kw else 0.
                allocations.append(TaskAllocation(task.task_id, 0., k))
            else:
                l = firm.labor_endowment * intensity * weights[i] / lw if lw else 0.
                allocations.append(TaskAllocation(task.task_id, l, 0.))
        plan = tuple(allocations)
        firm.evaluate_allocation(list(plan))
        action_id = f"effort_{index}"
        # L5 price explicitly sets a reserve; other L5 mechanisms affect valuation.
        price = (1.5, 2., 2.5, 3.)[index] if identity.L5 == "price" else None
        results[action_id] = Action(action_id, plan, offered_price=price)
    return results


def score_action(identity, firm, info, action, aggregate):
    activity = firm.evaluate_allocation(list(action.allocation))
    output = aggregate(activity)
    k = fsum(a.capital for a in action.allocation)
    l = fsum(a.labor for a in action.allocation)
    cost = k + l
    observed_price = info.market.last_market_price
    expected_price = 2. if observed_price is None else observed_price
    if identity.L5 == "competitive":
        # Price-taker: assumes last observed price is unchanged.
        price = expected_price
    elif identity.L5 == "cournot":
        # Illustrative residual-demand anticipation based on own output;
        # not a solved Cournot best response or a calibrated demand curve.
        price = max(0., expected_price - 0.01 * output)
    elif identity.L5 == "price":
        price = action.offered_price
    elif identity.L5 == "adaptive":
        price = expected_price
        # Own realized action payoffs are used by the L5 adaptive policy engine.
    else:
        raise ValueError("unknown L5")
    return price * output - cost

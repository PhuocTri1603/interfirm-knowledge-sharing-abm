"""Evaluate a 20-task execution proposal against one firm's shared resources.

No optimizing, endogenous adoption, market prices, or AI shock is assumed.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm
from interfirm_abm.task_execution import TaskModeQuote, TaskUnitCosts, quote_pure_task_mode


@dataclass(frozen=True)
class TaskChoice:
    task_id: str
    mode: str
    target_activity: float


@dataclass(frozen=True)
class BundleEvaluation:
    firm_id: str
    feasible: bool
    capital_used: float
    labor_used: float
    capital_available: float
    labor_available: float
    variable_cost: float
    task_quotes: tuple[TaskModeQuote, ...]
    violations: tuple[str, ...]


def evaluate_task_bundle(
    firm: TaskBasedFirm,
    choices: Sequence[TaskChoice],
    *,
    prices: TaskUnitCosts,
) -> BundleEvaluation:
    """Quote all 20 tasks and check common endowments.

    Reject malformed tasks or modes; report resource shortages as violations.
    Input costs are accounting quotes, not approved economic incentives.
    """
    task_ids = {task.task_id for task in firm.tasks}
    choice_ids = [choice.task_id for choice in choices]
    if len(choices) != 20 or set(choice_ids) != task_ids or len(set(choice_ids)) != 20:
        raise ValueError("Exactly one choice for each of the firm's 20 tasks is required")
    capabilities = {task.task_id: task for task in firm.tasks}
    quotes: list[TaskModeQuote] = []
    for choice in choices:
        quotes.append(quote_pure_task_mode(
            capabilities[choice.task_id],
            mode=choice.mode,
            target_activity=choice.target_activity,
            prices=prices,
        ))
    capital = math.fsum(quote.required_capital for quote in quotes)
    labor = math.fsum(quote.required_labor for quote in quotes)
    cost = math.fsum(quote.variable_cost for quote in quotes)
    violations = []
    if capital > firm.capital_endowment + 1e-9:
        violations.append("capital_endowment_exceeded")
    if labor > firm.labor_endowment + 1e-9:
        violations.append("labor_endowment_exceeded")
    if not all(math.isfinite(value) for value in (capital, labor, cost)):
        raise ValueError("Nonfinite aggregate resource or cost total")
    return BundleEvaluation(
        firm_id=firm.firm_id,
        feasible=not violations,
        capital_used=capital,
        labor_used=labor,
        capital_available=firm.capital_endowment,
        labor_available=firm.labor_endowment,
        variable_cost=cost,
        task_quotes=tuple(quotes),
        violations=tuple(violations),
    )


def feasible_allocations(evaluation: BundleEvaluation) -> list[TaskAllocation]:
    """Convert a feasible quoted bundle to the existing allocation interface."""
    if not evaluation.feasible:
        raise ValueError("Cannot convert infeasible task bundle")
    return [
        TaskAllocation(q.task_id, labor=q.required_labor, capital=q.required_capital)
        for q in evaluation.task_quotes
    ]

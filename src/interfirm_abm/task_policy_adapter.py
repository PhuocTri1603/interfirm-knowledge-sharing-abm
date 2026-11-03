"""Task-plan strategy adapter for the shared market.

Policies choose all 20 task modes and target activities. This adapter validates
resource feasibility and injects a caller-provided final-output aggregator.
No production function, price, strategy, or AI rule is endorsed here.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Sequence
import math

from interfirm_abm.task_bundle import TaskChoice, evaluate_task_bundle, feasible_allocations
from interfirm_abm.task_execution import TaskUnitCosts
from interfirm_abm.task_economics import EconomicPrices, evaluate_task_plan
from interfirm_abm.task_strategy_policy import AgentDecision, DecisionContext, StrategyPolicy
from interfirm_abm.task_based_firm import TaskAllocation


TaskPlanPolicy = Callable[[DecisionContext], Sequence[TaskChoice]]


@dataclass(frozen=True)
class TaskPlanAccounting:
    choices: tuple[TaskChoice, ...]
    capital_used: float
    labor_used: float
    output: float
    total_cost: float


def evaluate_policy_task_plan(
    context: DecisionContext,
    choices: Sequence[TaskChoice],
    *,
    unit_costs: TaskUnitCosts,
    aggregate_tasks: Callable[[Mapping[str, float]], float],
    fixed_cost: float = 0.0,
    adoption_cost: float = 0.0,
) -> TaskPlanAccounting:
    """Quote and validate a supplied task plan; do not optimize it."""
    firm = context.clone.firm
    selected = tuple(choices)
    quote = evaluate_task_bundle(firm, selected, prices=unit_costs)
    if not quote.feasible:
        raise ValueError(f"Infeasible task plan for {context.clone.agent_id}: {quote.violations}")
    allocations: list[TaskAllocation] = feasible_allocations(quote)
    accounting = evaluate_task_plan(
        firm,
        allocations,
        aggregate_tasks=aggregate_tasks,
        prices=EconomicPrices(
            output_price=0.0,
            capital_unit_cost=unit_costs.capital_rental_rate,
            labor_unit_cost=unit_costs.wage,
        ),
        fixed_cost=fixed_cost,
        adoption_cost=adoption_cost,
    )
    output = float(accounting["output"])
    total_cost = float(accounting["total_cost"])
    if not math.isfinite(output) or not math.isfinite(total_cost):
        raise ValueError("Nonfinite task-plan accounting")
    return TaskPlanAccounting(
        choices=selected,
        capital_used=float(accounting["used_capital"]),
        labor_used=float(accounting["used_labor"]),
        output=output,
        total_cost=total_cost,
    )


def adapt_task_plan_policy(
    policy: TaskPlanPolicy,
    *,
    unit_costs: TaskUnitCosts,
    aggregate_tasks: Callable[[Mapping[str, float]], float],
    fixed_cost: float = 0.0,
    adoption_cost: float = 0.0,
) -> StrategyPolicy:
    """Adapt researcher-supplied task choices to existing market decisions.

    Output price is deliberately not used to choose or evaluate a task plan;
    the shared market supplies the realized price after all decisions.
    """
    def decide(context: DecisionContext) -> AgentDecision:
        result = evaluate_policy_task_plan(
            context, policy(context), unit_costs=unit_costs,
            aggregate_tasks=aggregate_tasks, fixed_cost=fixed_cost,
            adoption_cost=adoption_cost,
        )
        return AgentDecision(output=result.output, total_cost=result.total_cost)
    return decide

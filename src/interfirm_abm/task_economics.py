"""Economic accounting interfaces for task-based Game 1.

No aggregator, prices, optimization policy, or market mechanism is selected here.
Caller supplies an explicitly approved aggregator and economic parameters.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping
import math

from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm


def _finite_nonnegative(name: str, value: float) -> None:
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and nonnegative")


@dataclass(frozen=True)
class EconomicPrices:
    output_price: float
    capital_unit_cost: float
    labor_unit_cost: float

    def __post_init__(self):
        for name in ("output_price", "capital_unit_cost", "labor_unit_cost"):
            _finite_nonnegative(name, getattr(self, name))


def evaluate_task_plan(
    firm: TaskBasedFirm,
    allocations: list[TaskAllocation],
    *,
    aggregate_tasks: Callable[[Mapping[str, float]], float],
    prices: EconomicPrices,
    fixed_cost: float = 0.0,
    adoption_cost: float = 0.0,
) -> dict[str, float | str]:
    """Evaluate a *given* feasible plan, not select a profit-maximizing plan.

    The aggregator is injected by the caller: this module neither endorses
    any specific aggregator nor interprets task activity as final output.
    Input costs are per-used-unit accounting; ownership/opportunity-cost
    treatment must be resolved in the economic design before scientific use.
    """
    _finite_nonnegative("fixed_cost", fixed_cost)
    _finite_nonnegative("adoption_cost", adoption_cost)
    activities = firm.evaluate_allocation(allocations)
    output = float(aggregate_tasks(activities))
    _finite_nonnegative("output", output)
    used_capital = sum(a.capital for a in allocations)
    used_labor = sum(a.labor for a in allocations)
    revenue = prices.output_price * output
    capital_cost = prices.capital_unit_cost * used_capital
    labor_cost = prices.labor_unit_cost * used_labor
    total_cost = capital_cost + labor_cost + fixed_cost + adoption_cost
    return {
        "firm_id": firm.firm_id,
        "output": output,
        "used_capital": used_capital,
        "used_labor": used_labor,
        "revenue": revenue,
        "capital_cost": capital_cost,
        "labor_cost": labor_cost,
        "fixed_cost": fixed_cost,
        "adoption_cost": adoption_cost,
        "total_cost": total_cost,
        "profit": revenue - total_cost,
    }

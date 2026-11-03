"""Task-level labor/capital execution candidates for Game 1.

No adoption, optimization, AI shock, or final production function is selected.
These helpers compare hypothetical pure-mode task execution at given prices.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

from interfirm_abm.task_based_firm import TaskCapability


def _valid_nonnegative(name: str, value: float) -> None:
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and nonnegative")


@dataclass(frozen=True)
class TaskUnitCosts:
    wage: float
    capital_rental_rate: float

    def __post_init__(self):
        _valid_nonnegative("wage", self.wage)
        _valid_nonnegative("capital_rental_rate", self.capital_rental_rate)


@dataclass(frozen=True)
class TaskModeQuote:
    task_id: str
    mode: str
    target_activity: float
    required_labor: float
    required_capital: float
    variable_cost: float


def quote_pure_task_mode(
    task: TaskCapability,
    *,
    mode: str,
    target_activity: float,
    prices: TaskUnitCosts,
) -> TaskModeQuote:
    """Quote inputs and variable costs to produce task activity in one mode.

    This is an illustrative linear within-mode accounting representation.
    It does not imply that a firm knows prices, has adopted automation, or
    can finance the quoted input bundle.
    """
    _valid_nonnegative("target_activity", target_activity)
    if mode not in ("labor", "capital"):
        raise ValueError("mode must be labor or capital")
    if mode == "capital" and not task.automation_eligible:
        raise ValueError(f"Capital mode is not eligible for {task.task_id}")
    labor = target_activity / task.labor_productivity if mode == "labor" else 0.0
    capital = target_activity / task.capital_productivity if mode == "capital" else 0.0
    return TaskModeQuote(
        task_id=task.task_id,
        mode=mode,
        target_activity=target_activity,
        required_labor=labor,
        required_capital=capital,
        variable_cost=prices.wage * labor + prices.capital_rental_rate * capital,
    )


def compare_pure_task_modes(
    task: TaskCapability,
    *,
    target_activity: float,
    prices: TaskUnitCosts,
) -> dict[str, TaskModeQuote | float | None]:
    """Return hypothetical costs, not an adoption recommendation.

    The difference is labor cost minus capital cost. It excludes fixed
    investment costs, adjustment costs, capacity constraints, and strategy.
    """
    labor = quote_pure_task_mode(
        task, mode="labor", target_activity=target_activity, prices=prices
    )
    if not task.automation_eligible:
        return {"labor": labor, "capital": None, "labor_minus_capital_cost": None}
    capital = quote_pure_task_mode(
        task, mode="capital", target_activity=target_activity, prices=prices
    )
    return {
        "labor": labor,
        "capital": capital,
        "labor_minus_capital_cost": labor.variable_cost - capital.variable_cost,
    }

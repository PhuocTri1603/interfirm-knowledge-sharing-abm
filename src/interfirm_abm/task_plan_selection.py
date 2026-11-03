"""Rank externally supplied feasible production plans by accounting profit.

This is a finite-candidate comparator, not a globally optimizing firm model.
The caller must explicitly provide an aggregator and economic prices.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Sequence
import math

from interfirm_abm.task_based_firm import TaskBasedFirm
from interfirm_abm.task_bundle import TaskChoice, evaluate_task_bundle, feasible_allocations
from interfirm_abm.task_execution import TaskUnitCosts
from interfirm_abm.task_economics import EconomicPrices, evaluate_task_plan


@dataclass(frozen=True)
class CandidatePlan:
    candidate_id: str
    choices: tuple[TaskChoice, ...]
    fixed_cost: float = 0.0
    adoption_cost: float = 0.0


@dataclass(frozen=True)
class CandidateResult:
    candidate_id: str
    feasible: bool
    profit: float | None
    output: float | None
    capital_used: float
    labor_used: float
    violations: tuple[str, ...]


@dataclass(frozen=True)
class CandidateComparison:
    firm_id: str
    results: tuple[CandidateResult, ...]
    best_candidate_id: str | None
    best_profit: float | None


def compare_candidate_plans(
    firm: TaskBasedFirm,
    candidates: Sequence[CandidatePlan],
    *,
    aggregate_tasks: Callable[[Mapping[str, float]], float],
    prices: EconomicPrices,
) -> CandidateComparison:
    """Compare a finite, externally defined choice set; never generate plans.

    Ties are resolved by first occurrence, making the result deterministic.
    Invalid plan structure or invalid economic inputs raise ValueError;
    resource-infeasible plans are reported without evaluating output.
    """
    if not candidates:
        raise ValueError("At least one candidate plan is required")
    ids = [c.candidate_id for c in candidates]
    if any(not x or not isinstance(x, str) for x in ids) or len(set(ids)) != len(ids):
        raise ValueError("Candidate IDs must be unique nonempty strings")
    unit_costs = TaskUnitCosts(
        wage=prices.labor_unit_cost,
        capital_rental_rate=prices.capital_unit_cost,
    )
    results: list[CandidateResult] = []
    best_id: str | None = None
    best_profit: float | None = None
    for candidate in candidates:
        for name, value in (("fixed_cost", candidate.fixed_cost),
                            ("adoption_cost", candidate.adoption_cost)):
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and nonnegative")
        bundle = evaluate_task_bundle(firm, candidate.choices, prices=unit_costs)
        if not bundle.feasible:
            results.append(CandidateResult(
                candidate.candidate_id, False, None, None,
                bundle.capital_used, bundle.labor_used, bundle.violations,
            ))
            continue
        accounting = evaluate_task_plan(
            firm,
            feasible_allocations(bundle),
            aggregate_tasks=aggregate_tasks,
            prices=prices,
            fixed_cost=candidate.fixed_cost,
            adoption_cost=candidate.adoption_cost,
        )
        profit = float(accounting["profit"])
        if not math.isfinite(profit):
            raise ValueError("Candidate profit must be finite")
        results.append(CandidateResult(
            candidate.candidate_id, True, profit, float(accounting["output"]),
            bundle.capital_used, bundle.labor_used, (),
        ))
        if best_profit is None or profit > best_profit:
            best_id, best_profit = candidate.candidate_id, profit
    return CandidateComparison(firm.firm_id, tuple(results), best_id, best_profit)

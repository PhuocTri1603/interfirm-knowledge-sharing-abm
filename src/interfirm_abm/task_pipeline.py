"""Compose candidate generation and finite-plan evaluation for Game 1.

No endogenous learning rule, aggregator, prices, or adoption policy is chosen.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

from interfirm_abm.task_based_firm import TaskBasedFirm
from interfirm_abm.task_candidate_generation import generate_local_candidates
from interfirm_abm.task_plan_selection import (
    CandidatePlan, CandidateComparison, compare_candidate_plans,
)
from interfirm_abm.task_economics import EconomicPrices


@dataclass(frozen=True)
class NeighborhoodEvaluation:
    firm_id: str
    baseline_candidate_id: str
    comparison: CandidateComparison
    generated_candidate_count: int
    feasible_candidate_count: int
    baseline_profit: float | None
    best_profit_gain_over_baseline: float | None


def evaluate_local_neighborhood(
    firm: TaskBasedFirm,
    baseline: CandidatePlan,
    *,
    activity_step: float,
    aggregate_tasks: Callable[[Mapping[str, float]], float],
    prices: EconomicPrices,
    include_mode_switches: bool = True,
) -> NeighborhoodEvaluation:
    """Generate and score one local neighborhood without changing the firm.

    The reported gain is a finite-set counterfactual accounting difference.
    It is NOT a realized gain, learning improvement, or predicted AI effect.
    """
    candidates = generate_local_candidates(
        firm, baseline, activity_step=activity_step,
        include_mode_switches=include_mode_switches,
    )
    comparison = compare_candidate_plans(
        firm, candidates, aggregate_tasks=aggregate_tasks, prices=prices,
    )
    baseline_result = comparison.results[0]
    baseline_profit = baseline_result.profit
    gain = (
        comparison.best_profit - baseline_profit
        if baseline_profit is not None and comparison.best_profit is not None
        else None
    )
    return NeighborhoodEvaluation(
        firm_id=firm.firm_id,
        baseline_candidate_id=baseline.candidate_id,
        comparison=comparison,
        generated_candidate_count=len(candidates),
        feasible_candidate_count=sum(r.feasible for r in comparison.results),
        baseline_profit=baseline_profit,
        best_profit_gain_over_baseline=gain,
    )

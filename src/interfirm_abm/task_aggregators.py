"""Candidate task-output aggregators for theoretical review.

NONE of these aggregators is selected as the official Game 1 technology.
They operate on task activity (not directly on capital and labor).
"""
from __future__ import annotations

import math
from typing import Mapping


def _validate(activities: Mapping[str, float], weights: Mapping[str, float]) -> tuple[list[float], list[float]]:
    if not activities or set(activities) != set(weights):
        raise ValueError("Activities and weights must have identical nonempty task sets")
    keys = sorted(activities)
    values = [float(activities[k]) for k in keys]
    shares = [float(weights[k]) for k in keys]
    if any(not math.isfinite(v) or v < 0 for v in values):
        raise ValueError("Task activity must be finite and nonnegative")
    if any(not math.isfinite(w) or w <= 0 for w in shares):
        raise ValueError("Weights must be finite and strictly positive")
    if not math.isclose(sum(shares), 1.0, rel_tol=0, abs_tol=1e-9):
        raise ValueError("Weights must sum to one")
    return values, shares


def weighted_linear(activities: Mapping[str, float], weights: Mapping[str, float]) -> float:
    """Weighted arithmetic aggregation; candidate only."""
    values, shares = _validate(activities, weights)
    return math.fsum(v * w for v, w in zip(values, shares))


def weighted_leontief(activities: Mapping[str, float], weights: Mapping[str, float]) -> float:
    """Normalized bottleneck candidate: min_j(activity_j / weight_j)."""
    values, shares = _validate(activities, weights)
    return min(v / w for v, w in zip(values, shares))


def task_ces(
    activities: Mapping[str, float],
    weights: Mapping[str, float],
    *,
    sigma: float,
) -> float:
    """Weighted CES over task activities, elasticity sigma > 0.

    Y = (sum_j omega_j * q_j ** ((sigma-1)/sigma)) ** (sigma/(sigma-1)).
    The sigma=1 limit is weighted geometric mean. sigma near zero is
    evaluated via its Leontief limit min(q_j) only if equal weights? No:
    the weighted power-mean limit is min(q_j) for positive weights.
    For sigma < 1, a zero task activity implies zero aggregate output.
    The aggregator is a *candidate*, not an approved research assumption.
    """
    values, shares = _validate(activities, weights)
    if not math.isfinite(sigma) or sigma <= 0:
        raise ValueError("sigma must be finite and strictly positive")
    if math.isclose(sigma, 1.0, rel_tol=0, abs_tol=1e-12):
        if any(v == 0 for v in values):
            return 0.0
        return math.exp(math.fsum(w * math.log(v) for v, w in zip(values, shares)))
    rho = (sigma - 1.0) / sigma
    if rho < 0 and any(v == 0 for v in values):
        return 0.0
    positive_terms = [(math.log(w) + rho * math.log(v)) for v, w in zip(values, shares) if v > 0]
    if not positive_terms:
        return 0.0
    maximum = max(positive_terms)
    logsum = maximum + math.log(math.fsum(math.exp(t - maximum) for t in positive_terms))
    return math.exp(logsum / rho)

"""Researcher-approved A5: normalized 20-activity CES technology.

Output is a dimensionless within-configuration index, NOT market quantity.
The sigma values are scenario assumptions, not empirical calibration.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import exp, fsum, isfinite, log

from interfirm_abm.task_based_firm import TaskBasedFirm, TaskAllocation

TASK_IDS = tuple(f"T{i:02d}" for i in range(1, 21))
SIGMA_SCENARIOS = (0.5, 1.0, 2.0)


@dataclass(frozen=True)
class A5Technology:
    reference: dict[str, float]
    sigma: float

    def __post_init__(self):
        if set(self.reference) != set(TASK_IDS):
            raise ValueError("Reference must have exactly T01..T20")
        if any(not isfinite(v) or v <= 0 for v in self.reference.values()):
            raise ValueError("Reference activities must be positive and finite")
        if not isfinite(self.sigma) or self.sigma <= 0:
            raise ValueError("sigma must be positive and finite")

    def output_index(self, activities: dict[str, float]) -> float:
        if set(activities) != set(TASK_IDS):
            raise ValueError("Activities must have exactly T01..T20")
        if any(not isfinite(v) or v < 0 for v in activities.values()):
            raise ValueError("Activities must be nonnegative and finite")
        x = [activities[k] / self.reference[k] for k in TASK_IDS]
        if any(not isfinite(v) for v in x):
            raise ValueError("Non-finite normalized task activity")
        if not any(x):
            return 0.0
        if self.sigma == 1.0:
            if any(v == 0 for v in x):
                return 0.0
            return exp(fsum(log(v) for v in x) / 20.0)
        rho = (self.sigma - 1.0) / self.sigma
        if rho < 0 and any(v == 0 for v in x):
            return 0.0
        terms = [rho * log(v) for v in x if v > 0]
        maximum = max(terms)
        log_mean = maximum + log(fsum(exp(t - maximum) for t in terms) / 20.0)
        return exp(log_mean / rho)

    def output_from_allocation(self, firm: TaskBasedFirm, allocations: list[TaskAllocation]) -> float:
        return self.output_index(firm.evaluate_allocation(allocations))


def reference_for_profile(firm: TaskBasedFirm) -> dict[str, float]:
    """Frozen feasible labor-only reference; never fit to strategies or payoffs."""
    if firm.labor_endowment <= 0:
        raise ValueError("A5 requires strictly positive reference labor endowment")
    if set(t.task_id for t in firm.tasks) != set(TASK_IDS):
        raise ValueError("Profile must have 20 canonical tasks")
    ref = {t.task_id: t.labor_productivity * firm.labor_endowment / 20.0 for t in firm.tasks}
    if any(not isfinite(v) or v <= 0 for v in ref.values()):
        raise ValueError("Reference must be strictly positive")
    return ref


def technology_for_profile(firm: TaskBasedFirm, sigma: float) -> A5Technology:
    return A5Technology(reference_for_profile(firm), sigma)


def paired_technologies(firm: TaskBasedFirm) -> dict[float, A5Technology]:
    """Same frozen reference for all three within-profile sigma treatments."""
    reference = reference_for_profile(firm)
    return {s: A5Technology(reference.copy(), s) for s in SIGMA_SCENARIOS}

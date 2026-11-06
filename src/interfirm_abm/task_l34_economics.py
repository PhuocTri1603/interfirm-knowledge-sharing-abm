"""Explicit, uncalibrated Game 1 L3/L4 economic mechanisms.

All four numeric parameters must be supplied by the experiment. No capital
stock accumulation, rival-specific information, or implicit AI adoption.
"""
from dataclasses import dataclass, replace
from math import isfinite, fsum
from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm

@dataclass(frozen=True)
class L34Parameters:
    capacity_ratio: float
    adjustment_unit_cost: float
    efficiency_gain: float
    adoption_fee: float

    def __post_init__(self):
        if not all(isfinite(x) for x in (self.capacity_ratio, self.adjustment_unit_cost,
                                         self.efficiency_gain, self.adoption_fee)):
            raise ValueError("L3/L4 parameters must be finite")
        if self.capacity_ratio <= 0 or self.adjustment_unit_cost < 0 or self.efficiency_gain < 0 or self.adoption_fee < 0:
            raise ValueError("L3/L4 parameters out of economic domain")


def effective_firm(firm: TaskBasedFirm, l4: str, parameters: L34Parameters) -> TaskBasedFirm:
    """L4 eligibility expands the feasible task set; efficiency raises aK."""
    if l4 not in ("eligibility", "efficiency", "adoption_cost", "combined"):
        raise ValueError("unknown L4")
    unlock = l4 in ("eligibility", "adoption_cost", "combined")
    improve = l4 in ("efficiency", "combined")
    tasks = tuple(replace(t,
        automation_eligible=(t.automation_eligible or unlock),
        capital_productivity=t.capital_productivity * (1 + parameters.efficiency_gain if improve else 1))
        for t in firm.tasks)
    return replace(firm, tasks=tasks)


def capacity_limited(plan, firm: TaskBasedFirm, original: TaskBasedFirm,
                     parameters: L34Parameters):
    """Limit each task's produced activity to capacity_ratio times its labor reference."""
    original_tasks = {t.task_id: t for t in original.tasks}
    effective_tasks = {t.task_id: t for t in firm.tasks}
    result = []
    for a in plan:
        t = effective_tasks[a.task_id]
        benchmark = original_tasks[a.task_id].labor_productivity * original.labor_endowment / 20
        actual = a.labor * t.labor_productivity + a.capital * t.capital_productivity
        factor = min(1., parameters.capacity_ratio * benchmark / actual) if actual else 1.
        result.append(TaskAllocation(a.task_id, a.labor * factor, a.capital * factor))
    firm.evaluate_allocation(result)
    return tuple(result)


def economic_extra_cost(identity, plan, previous_plan, original: TaskBasedFirm,
                        adopted_tasks: frozenset[str], parameters: L34Parameters):
    """Return (current-period adjustment cost, one-time AI adoption fee, new unlocks)."""
    adjustment = 0.
    if identity.L3 == "adjustment" and previous_plan is not None:
        old = {a.task_id: a for a in previous_plan}
        adjustment = parameters.adjustment_unit_cost * fsum(
            abs(a.labor - old[a.task_id].labor) + abs(a.capital - old[a.task_id].capital)
            for a in plan)
    originally_eligible = {t.task_id for t in original.tasks if t.automation_eligible}
    newly_used = frozenset(a.task_id for a in plan
        if a.capital > 0 and a.task_id not in originally_eligible
        and a.task_id not in adopted_tasks)
    fee = parameters.adoption_fee * len(newly_used) if identity.L4 in ("adoption_cost", "combined") else 0.
    return adjustment, fee, newly_used if identity.L4 in ("adoption_cost", "combined") else frozenset()

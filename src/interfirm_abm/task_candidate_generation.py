"""Deterministic one-change candidate generation for a 20-task firm.

This is a research instrument for constructing a local choice set, NOT a
behavioral learning rule or an assertion that firms know counterfactual payoffs.
"""
from __future__ import annotations

import math
from collections.abc import Sequence

from interfirm_abm.task_based_firm import TaskBasedFirm
from interfirm_abm.task_bundle import TaskChoice
from interfirm_abm.task_plan_selection import CandidatePlan


def generate_local_candidates(
    firm: TaskBasedFirm,
    baseline: CandidatePlan,
    *,
    activity_step: float,
    include_mode_switches: bool = True,
) -> tuple[CandidatePlan, ...]:
    """Return baseline plus unique one-task changes, without economic evaluation.

    Each target activity may be increased or decreased by an externally
    specified absolute step (nonnegative only). Eligible tasks can switch
    between pure labor and capital execution at unchanged activity.
    Ineligible tasks can never be assigned capital. Fixed and adoption
    costs are carried over unchanged: this generator does NOT infer new
    adoption costs or financing. Candidate IDs are deterministic.
    """
    if not math.isfinite(activity_step) or activity_step <= 0:
        raise ValueError("activity_step must be finite and strictly positive")
    if not baseline.candidate_id:
        raise ValueError("baseline candidate_id must be nonempty")
    tasks = {t.task_id: t for t in firm.tasks}
    choices = baseline.choices
    if len(choices) != 20 or len({c.task_id for c in choices}) != 20:
        raise ValueError("Baseline must contain 20 unique task choices")
    if {c.task_id for c in choices} != set(tasks):
        raise ValueError("Baseline tasks must match firm tasks")
    for c in choices:
        if c.mode not in ("labor", "capital"):
            raise ValueError("Unknown task mode")
        if not math.isfinite(c.target_activity) or c.target_activity < 0:
            raise ValueError("Task activity must be finite and nonnegative")
        if c.mode == "capital" and not tasks[c.task_id].automation_eligible:
            raise ValueError("Baseline uses ineligible capital mode")
    results = [baseline]
    seen = {tuple((c.task_id, c.mode, c.target_activity) for c in choices)}
    def add(index: int, mode: str, activity: float, suffix: str) -> None:
        if activity < 0 or not math.isfinite(activity):
            return
        changed = list(choices)
        original = choices[index]
        changed[index] = TaskChoice(original.task_id, mode, activity)
        key = tuple((c.task_id, c.mode, c.target_activity) for c in changed)
        if key not in seen:
            seen.add(key)
            results.append(CandidatePlan(
                f"{baseline.candidate_id}__{original.task_id}__{suffix}",
                tuple(changed), baseline.fixed_cost, baseline.adoption_cost,
            ))
    for index, c in enumerate(choices):
        add(index, c.mode, c.target_activity + activity_step, "up")
        if c.target_activity >= activity_step:
            add(index, c.mode, c.target_activity - activity_step, "down")
        if include_mode_switches and tasks[c.task_id].automation_eligible:
            alternative = "capital" if c.mode == "labor" else "labor"
            add(index, alternative, c.target_activity, "switch")
    return tuple(results)

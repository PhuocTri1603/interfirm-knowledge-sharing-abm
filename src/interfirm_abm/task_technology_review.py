"""L1/L2 production feasibility review; records questions, not solutions.

This module does not approve technology equations or evaluate output.
"""
from dataclasses import dataclass
from itertools import product
from interfirm_abm.task_layer_registry import LAYERS

TECHNOLOGIES = dict(LAYERS)["L1"]
AGGREGATORS = dict(LAYERS)["L2"]
REQUIRED = (
    "task_equations", "task_parameter_domains", "eligibility_semantics",
    "aggregation_equation", "aggregation_normalization",
    "input_feasibility", "comparison_baseline",
)

@dataclass(frozen=True)
class TechnologyReview:
    l1: str
    l2: str
    cell_id: str
    status: str
    unresolved: tuple[str, ...]
    flags: tuple[str, ...]


def review_technology(l1: str, l2: str, specified: tuple[str, ...] = ()) -> TechnologyReview:
    if l1 not in TECHNOLOGIES or l2 not in AGGREGATORS:
        raise ValueError("unknown L1/L2 option")
    if set(specified) - set(REQUIRED):
        raise ValueError("unknown specification field")
    flags = ["separate_task_activity_from_final_output"]
    if l1 == "assignment":
        flags.append("define_exclusive_mode_and_switching")
    if l1 == "ces":
        flags.append("define_within_task_ces_zero_and_limit_domains")
    if l1 == "leontief":
        flags.append("review_joint_input_requirement_vs_automation_eligibility")
    if l1 == "hybrid":
        flags.append("define_task_technology_assignment")
    if l2 == "leontief":
        flags.append("review_all_tasks_essential_and_positive_requirements")
    if l2 == "ces":
        flags.append("define_cross_task_ces_zero_and_limit_domains")
    if l1 == "ces" and l2 == "ces":
        flags.append("keep_within_task_and_cross_task_elasticities_distinct")
    return TechnologyReview(
        l1, l2, f"L1={l1}|L2={l2}", "requires_research_review",
        tuple(k for k in REQUIRED if k not in specified), tuple(flags),
    )


def iter_technology_reviews():
    for l1, l2 in product(TECHNOLOGIES, AGGREGATORS):
        yield review_technology(l1, l2)

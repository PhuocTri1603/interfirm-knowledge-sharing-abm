"""Conservative economic review flags; no economic assumptions are approved."""
from dataclasses import dataclass
from interfirm_abm.task_layer_registry import iter_strategies

REQUIRED = ("task_technology", "task_aggregation", "input_costs",
            "ai_shock", "market_solution", "learning_policy",
            "population_assignment", "initial_conditions", "welfare_measure")

@dataclass(frozen=True)
class Audit:
    strategy_id: str
    status: str
    missing: tuple[str, ...]
    review_flags: tuple[str, ...]

def audit_strategy(strategy, approved=()):
    choices = dict(strategy.choices)
    if set(choices) != {f"L{i}" for i in range(1, 8)}:
        raise ValueError("expected L1-L7")
    if set(approved) - set(REQUIRED):
        raise ValueError("unknown specification")
    flags = []
    if choices["L1"] == "hybrid":
        flags.append("define_hybrid_task_assignment")
    if choices["L1"] == "ces" or choices["L2"] == "ces":
        flags.append("distinguish_within_and_across_task_elasticities")
    if choices["L3"] in ("adjustment", "investment"):
        flags.append("specify_intertemporal_state_and_objective")
    if choices["L4"] in ("adoption_cost", "combined"):
        flags.append("specify_voluntary_adoption")
    if choices["L5"] == "price":
        flags.append("specify_price_game_and_rationing")
    if choices["L5"] == "cournot" and choices["L6"] != "optimization":
        flags.append("distinguish_learning_from_cournot_equilibrium")
    if choices["L7"] in ("mixed", "clones", "stratified"):
        flags.append("specify_population_assignment")
    if choices["L7"] == "clones":
        flags.append("specify_clone_count_and_market_size")
    missing = tuple(k for k in REQUIRED if k not in approved)
    return Audit(strategy.strategy_id, "requires_research_review", missing, tuple(flags))

def catalog_audit_summary():
    from collections import Counter
    counts = Counter()
    for strategy in iter_strategies():
        result = audit_strategy(strategy)
        counts["nominal_cells"] += 1
        for flag in result.review_flags:
            counts[flag] += 1
    return dict(counts)

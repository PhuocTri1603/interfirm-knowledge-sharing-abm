"""Connect approved layer catalog, deterministic plans and experiment provenance.

No firms, prices, payoffs, or economic outcomes are simulated here.
"""
from dataclasses import dataclass
from interfirm_abm.task_layer_registry import iter_strategies
from interfirm_abm.task_experiment_config import PlannedRun
from interfirm_abm.task_experiment_registry import (
    ExperimentScenario, FirmMembership, validate_memberships, reporting_keys,
)


@dataclass(frozen=True)
class RegisteredExperiment:
    scenario: ExperimentScenario
    memberships: tuple[FirmMembership, ...]
    analysis_keys: tuple[tuple, ...]


def register_planned_run(
    run: PlannedRun,
    base_firm_ids: tuple[str, ...],
    agent_to_base: tuple[tuple[str, str], ...] | None = None,
    ex_ante_clusters: dict[str, str] | None = None,
    cluster_definition_version: str | None = None,
) -> RegisteredExperiment:
    """Create validated metadata for one planned market.

    Non-clone markets use one agent per base firm. Clone markets require an
    explicit agent-to-base mapping; no clone counts or composition are assumed.
    Clusters are optional and must be explicitly supplied, never inferred.
    """
    strategy = next((s for s in iter_strategies() if s.strategy_id == run.strategy_id), None)
    if strategy is None:
        raise ValueError("strategy_id not in approved catalog")
    if run.population_regime != dict(strategy.choices)["L7"]:
        raise ValueError("population regime mismatch")
    if run.execution_status != "not_executed" or run.compatibility_status != "not_assessed":
        raise ValueError("registration only supports unexecuted, unassessed plans")
    if agent_to_base is None:
        if run.population_regime == "clones":
            raise ValueError("clone markets require explicit agent-to-base mapping")
        agent_to_base = tuple((firm_id, firm_id) for firm_id in base_firm_ids)
    else:
        agent_to_base = tuple(agent_to_base)
    if ex_ante_clusters is not None:
        if not cluster_definition_version:
            raise ValueError("cluster_definition_version required")
        if set(ex_ante_clusters) != set(base_firm_ids):
            raise ValueError("clusters must cover exactly the base firms")
        if any(not isinstance(c, str) or not c.strip() for c in ex_ante_clusters.values()):
            raise ValueError("cluster IDs must be nonempty")
    elif cluster_definition_version is not None:
        raise ValueError("cluster version without clusters")
    scenario = ExperimentScenario(
        experiment_id=run.experiment_id,
        scenario_id=run.scenario_id,
        market_id=run.market_id,
        strategy=strategy,
        replication_id=run.replication_id,
        seed=run.seed,
        base_firm_ids=tuple(base_firm_ids),
        market_agent_ids=tuple(agent for agent, _ in agent_to_base),
        population_regime=run.population_regime,
    )
    members = tuple(
        FirmMembership(
            scenario_id=scenario.scenario_id,
            market_agent_id=agent,
            base_firm_id=base,
            cluster_id=ex_ante_clusters[base] if ex_ante_clusters is not None and base in ex_ante_clusters else None,
            cluster_definition_version=cluster_definition_version if ex_ante_clusters is not None else None,
            cluster_timing="ex_ante" if ex_ante_clusters is not None else None,
        )
        for agent, base in agent_to_base
    )
    validate_memberships(scenario, members)
    return RegisteredExperiment(scenario, members, reporting_keys(scenario))

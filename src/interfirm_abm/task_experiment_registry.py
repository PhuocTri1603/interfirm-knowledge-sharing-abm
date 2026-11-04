"""Experiment provenance, separate from economic behavior and simulation.

A scenario is a market design; it is not a firm or a strategy clone.
"""
from dataclasses import dataclass
from interfirm_abm.task_layer_registry import StrategyRecord, ANALYSIS_LENSES


def _required(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a nonempty string")


@dataclass(frozen=True)
class ExperimentScenario:
    experiment_id: str
    scenario_id: str
    market_id: str
    strategy: StrategyRecord
    replication_id: int
    seed: int
    base_firm_ids: tuple[str, ...]
    market_agent_ids: tuple[str, ...]
    population_regime: str
    specification_status: str = "not_yet_specified"

    def __post_init__(self):
        for field in ("experiment_id", "scenario_id", "market_id"):
            _required(getattr(self, field), field)
        if not isinstance(self.replication_id, int) or self.replication_id < 0:
            raise ValueError("replication_id must be nonnegative")
        if not isinstance(self.seed, int) or self.seed < 0:
            raise ValueError("seed must be nonnegative")
        if not self.base_firm_ids or len(set(self.base_firm_ids)) != len(self.base_firm_ids):
            raise ValueError("base_firm_ids must be nonempty and unique")
        if not self.market_agent_ids or len(set(self.market_agent_ids)) != len(self.market_agent_ids):
            raise ValueError("market_agent_ids must be nonempty and unique")
        if any(not x or not x.strip() for x in self.base_firm_ids + self.market_agent_ids):
            raise ValueError("firm and agent IDs must be nonempty")
        choices = dict(self.strategy.choices)
        if self.population_regime != choices["L7"]:
            raise ValueError("population_regime must match strategy L7")
        if self.population_regime != "clones" and len(self.market_agent_ids) != len(self.base_firm_ids):
            raise ValueError("non-clone market requires one agent per base firm")
        if self.population_regime == "clones" and len(self.market_agent_ids) < len(self.base_firm_ids):
            raise ValueError("clone market cannot contain fewer agents than base firms")

    @property
    def run_key(self):
        return (self.experiment_id, self.scenario_id, self.market_id, self.replication_id)


@dataclass(frozen=True)
class FirmMembership:
    scenario_id: str
    market_agent_id: str
    base_firm_id: str
    cluster_id: str | None = None
    cluster_definition_version: str | None = None
    cluster_timing: str | None = None

    def __post_init__(self):
        for field in ("scenario_id", "market_agent_id", "base_firm_id"):
            _required(getattr(self, field), field)
        if self.cluster_id is None:
            if self.cluster_definition_version is not None or self.cluster_timing is not None:
                raise ValueError("cluster metadata requires cluster_id")
        else:
            _required(self.cluster_definition_version, "cluster_definition_version")
            if self.cluster_timing not in ("ex_ante", "ex_post"):
                raise ValueError("cluster_timing must be ex_ante or ex_post")


def validate_memberships(scenario: ExperimentScenario, memberships: tuple[FirmMembership, ...]):
    if len(memberships) != len(scenario.market_agent_ids):
        raise ValueError("one membership per market agent required")
    if {m.market_agent_id for m in memberships} != set(scenario.market_agent_ids):
        raise ValueError("market agent IDs do not match scenario")
    if any(m.scenario_id != scenario.scenario_id for m in memberships):
        raise ValueError("membership scenario mismatch")
    if any(m.base_firm_id not in scenario.base_firm_ids for m in memberships):
        raise ValueError("unknown base firm")
    if {m.base_firm_id for m in memberships} != set(scenario.base_firm_ids):
        raise ValueError("every base firm must be represented")
    if scenario.population_regime != "clones":
        if len({m.base_firm_id for m in memberships}) != len(memberships):
            raise ValueError("duplicate base firm outside clone market")


def reporting_keys(scenario: ExperimentScenario):
    return tuple((scenario.run_key, scenario.strategy.strategy_id, lens) for lens in ANALYSIS_LENSES)

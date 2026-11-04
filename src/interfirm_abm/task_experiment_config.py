"""Reproducible experiment manifest planning; does not execute markets."""
from dataclasses import dataclass
from hashlib import sha256
from itertools import islice
from interfirm_abm.task_layer_registry import LAYERS, iter_strategies

VALID_OPTIONS = {name: set(options) for name, options in LAYERS}


@dataclass(frozen=True)
class ExperimentPlan:
    experiment_id: str
    selected_layers: tuple[tuple[str, tuple[str, ...]], ...]
    replication_count: int
    master_seed: int

    def __post_init__(self):
        if not isinstance(self.experiment_id, str) or not self.experiment_id.strip():
            raise ValueError("experiment_id must be nonempty")
        if type(self.replication_count) is not int or self.replication_count < 1:
            raise ValueError("replication_count must be positive")
        if type(self.master_seed) is not int or self.master_seed < 0:
            raise ValueError("master_seed must be nonnegative")
        keys = [key for key, _ in self.selected_layers]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate layer filter")
        for key, values in self.selected_layers:
            if key not in VALID_OPTIONS or not values or len(values) != len(set(values)):
                raise ValueError("invalid layer filter")
            if any(v not in VALID_OPTIONS[key] for v in values):
                raise ValueError("unknown layer option")


@dataclass(frozen=True)
class PlannedRun:
    experiment_id: str
    strategy_id: str
    scenario_id: str
    market_id: str
    replication_id: int
    seed: int
    population_regime: str
    execution_status: str = "not_executed"
    compatibility_status: str = "not_assessed"


def deterministic_seed(master_seed: int, strategy_id: str, replication_id: int) -> int:
    payload = f"{master_seed}|{strategy_id}|{replication_id}".encode("utf-8")
    return int.from_bytes(sha256(payload).digest()[:8], "big")


def iter_plan_runs(plan: ExperimentPlan):
    filters = dict(plan.selected_layers)
    for strategy in iter_strategies():
        if any(dict(strategy.choices)[key] not in values for key, values in filters.items()):
            continue
        regime = dict(strategy.choices)["L7"]
        for replication in range(plan.replication_count):
            seed = deterministic_seed(plan.master_seed, strategy.strategy_id, replication)
            scenario_id = strategy.strategy_id
            market_id = f"{plan.experiment_id}|{strategy.strategy_id}|rep={replication}"
            yield PlannedRun(
                plan.experiment_id, strategy.strategy_id, scenario_id,
                market_id, replication, seed, regime,
            )


def preview_plan(plan: ExperimentPlan, limit: int = 5):
    if type(limit) is not int or limit < 0:
        raise ValueError("limit must be nonnegative")
    return tuple(islice(iter_plan_runs(plan), limit))

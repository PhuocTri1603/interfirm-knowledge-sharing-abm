"""Policy interface for repeated markets, with no built-in economic behavior.

Researcher-supplied strategy policies decide actions. The runner gives every
agent the same completed-market history and never exposes current-round choices
or outcomes to any policy. Policies are user code, not endorsed economics.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping
import math

from interfirm_abm.task_strategy_population import SharedMarketPopulation, StrategyClone
from interfirm_abm.task_repeated_market import RoundActions, RepeatedMarketOutcome, evaluate_repeated_market
from interfirm_abm.task_shared_market import MarketRoundOutcome


@dataclass(frozen=True)
class AgentDecision:
    output: float
    total_cost: float

    def __post_init__(self) -> None:
        for field in ("output", "total_cost"):
            value = getattr(self, field)
            if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                raise ValueError(f"{field} must be finite and nonnegative")


@dataclass(frozen=True)
class DecisionContext:
    round_index: int
    clone: StrategyClone
    completed_rounds: tuple[MarketRoundOutcome, ...]


StrategyPolicy = Callable[[DecisionContext], AgentDecision]


def generate_policy_actions(
    population: SharedMarketPopulation,
    *,
    round_index: int,
    completed_rounds: tuple[MarketRoundOutcome, ...],
    policies: Mapping[str, StrategyPolicy],
) -> RoundActions:
    """Request one action per agent using only completed-round market records.

    All policies receive the same immutable history tuple. Execution order is
    not a within-round information channel. Caller policies may be stateful;
    reproducibility then depends on caller-controlled policy state/seeds.
    """
    if round_index != len(completed_rounds) or round_index < 0:
        raise ValueError("round_index must match completed history length")
    if set(policies) != set(population.strategy_roster):
        raise ValueError("Policies must cover exactly the registered strategies")
    outputs: dict[str, float] = {}
    costs: dict[str, float] = {}
    for clone in population.clones:
        decision = policies[clone.strategy_id](
            DecisionContext(round_index, clone, completed_rounds)
        )
        if not isinstance(decision, AgentDecision):
            raise TypeError("Strategy policy must return AgentDecision")
        outputs[clone.agent_id] = float(decision.output)
        costs[clone.agent_id] = float(decision.total_cost)
    return RoundActions(outputs=outputs, total_costs=costs)


def run_policy_market(
    population: SharedMarketPopulation,
    *,
    number_of_rounds: int,
    policies: Mapping[str, StrategyPolicy],
    inverse_demand: Callable[[int, float], float],
) -> RepeatedMarketOutcome:
    """Generate actions from injected policies, then reuse market accounting.

    This runner is an integration harness, not an optimization/learning model.
    """
    if isinstance(number_of_rounds, bool) or not isinstance(number_of_rounds, int) or number_of_rounds < 1:
        raise ValueError("number_of_rounds must be a positive integer")
    actions: list[RoundActions] = []
    completed: tuple[MarketRoundOutcome, ...] = ()
    for t in range(number_of_rounds):
        current = generate_policy_actions(
            population, round_index=t, completed_rounds=completed, policies=policies
        )
        actions.append(current)
        # Reevaluate prior rounds with the supplied deterministic schedule.
        # No previous decisions are recomputed; no within-round outcome leaks.
        result = evaluate_repeated_market(
            population, actions, inverse_demand=inverse_demand
        )
        completed = result.rounds
    return result

"""Repeated shared-market accounting for externally supplied round actions.

No behavioral policy, demand specification, equilibrium or learning is assumed.
Each round is a simultaneous joint profile, evaluated at one shared price.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Mapping
import math

from interfirm_abm.task_strategy_population import SharedMarketPopulation
from interfirm_abm.task_shared_market import MarketRoundOutcome, evaluate_shared_market_round


@dataclass(frozen=True)
class RoundActions:
    outputs: Mapping[str, float]
    total_costs: Mapping[str, float]


@dataclass(frozen=True)
class AgentTrajectory:
    agent_id: str
    base_firm_id: str
    strategy_id: str
    profits: tuple[float, ...]
    cumulative_profits: tuple[float, ...]


@dataclass(frozen=True)
class RepeatedMarketOutcome:
    strategy_roster: tuple[str, ...]
    rounds: tuple[MarketRoundOutcome, ...]
    trajectories: tuple[AgentTrajectory, ...]

    def first_round_reaching(self, agent_id: str, threshold: float) -> int | None:
        """First zero-based round index reaching cumulative-profit threshold."""
        if not math.isfinite(threshold):
            raise ValueError("threshold must be finite")
        trajectory = next((t for t in self.trajectories if t.agent_id == agent_id), None)
        if trajectory is None:
            raise ValueError("Unknown agent_id")
        return next(
            (i for i, value in enumerate(trajectory.cumulative_profits) if value >= threshold),
            None,
        )


def evaluate_repeated_market(
    population: SharedMarketPopulation,
    actions_by_round: Iterable[RoundActions],
    *,
    inverse_demand: Callable[[int, float], float],
) -> RepeatedMarketOutcome:
    """Evaluate given round actions; inject a common inverse-demand schedule.

    Each round's joint outputs/costs must cover all agents exactly. Actions
    may come from future researcher-approved strategies, but this function
    does not generate them, carry over stocks or infer dynamic decisions.
    """
    actions = tuple(actions_by_round)
    if not actions:
        raise ValueError("At least one round required")
    rounds = tuple(
        evaluate_shared_market_round(
            population,
            round_index=t,
            outputs=action.outputs,
            total_costs=action.total_costs,
            inverse_demand=lambda q, t=t: inverse_demand(t, q),
        )
        for t, action in enumerate(actions)
    )
    trajectories = []
    for clone in population.clones:
        profits = tuple(
            next(a.profit for a in result.agents if a.agent_id == clone.agent_id)
            for result in rounds
        )
        cumulative = tuple(math.fsum(profits[:i + 1]) for i in range(len(profits)))
        if any(not math.isfinite(x) for x in cumulative):
            raise ValueError("Nonfinite cumulative profit")
        trajectories.append(AgentTrajectory(
            agent_id=clone.agent_id,
            base_firm_id=clone.base_firm_id,
            strategy_id=clone.strategy_id,
            profits=profits,
            cumulative_profits=cumulative,
        ))
    return RepeatedMarketOutcome(
        strategy_roster=population.strategy_roster,
        rounds=rounds,
        trajectories=tuple(trajectories),
    )

"""Injected learning/choice operators for Game 1.

All rewards, candidate sets, peer observations, and random generators are
explicit inputs. No researcher-unapproved behavioral calibration is assumed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import exp, isfinite
from random import Random
from typing import Callable, Mapping

from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm
from interfirm_abm.task_economic_policy import MarketObservation
from interfirm_abm.task_decision_rules import CandidateGenerator, TaskPlan


RewardProvider = Callable[[TaskBasedFirm, MarketObservation, str, TaskPlan], float]
PeerProvider = Callable[[TaskBasedFirm, MarketObservation], Mapping[str, float]]


def _options(generator: CandidateGenerator, firm: TaskBasedFirm, obs: MarketObservation):
    options = {name: tuple(plan) for name, plan in generator(firm, obs).items()}
    if not options or any(not name for name in options):
        raise ValueError("nonempty candidate plans with nonempty IDs required")
    for plan in options.values():
        firm.evaluate_allocation(list(plan))
    return options


@dataclass
class TrialAndErrorChoice:
    candidates: CandidateGenerator
    reward: RewardProvider
    exploration_probability: float
    rng: Random
    current_choice: dict[str, str] = field(default_factory=dict)
    realized_history: dict[str, list[tuple[int, str, float]]] = field(default_factory=dict)
    pending_round: dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        if not 0 <= self.exploration_probability <= 1:
            raise ValueError("exploration_probability must be in [0,1]")

    def decide_tasks(self, firm: TaskBasedFirm, observation: MarketObservation) -> TaskPlan:
        options = _options(self.candidates, firm, observation)
        incumbent = self.current_choice.get(firm.firm_id)
        if incumbent not in options or self.rng.random() < self.exploration_probability:
            chosen = self.rng.choice(sorted(options))
        else:
            chosen = incumbent
        self.current_choice[firm.firm_id] = chosen
        self.pending_round[firm.firm_id] = observation.round_number
        # Reward is externally supplied; this is an explicit diagnostic hook.
        score = float(self.reward(firm, observation, chosen, options[chosen]))
        if not isfinite(score):
            raise ValueError("trial reward must be finite")
        return options[chosen]

    def observe_payoff(self, firm: TaskBasedFirm, round_number: int, payoff: float) -> None:
        """Record own realized payoff; no update rule is imposed."""
        if not isfinite(payoff) or self.pending_round.get(firm.firm_id) != round_number:
            raise ValueError("payoff feedback must match a pending round and be finite")
        self.realized_history.setdefault(firm.firm_id, []).append(
            (round_number, self.current_choice[firm.firm_id], payoff)
        )
        del self.pending_round[firm.firm_id]


@dataclass
class SoftmaxChoice:
    candidates: CandidateGenerator
    expected_benefit: RewardProvider
    temperature: float
    rng: Random

    def __post_init__(self):
        if not isfinite(self.temperature) or self.temperature <= 0:
            raise ValueError("temperature must be positive and finite")

    def decide_tasks(self, firm: TaskBasedFirm, observation: MarketObservation) -> TaskPlan:
        options = _options(self.candidates, firm, observation)
        names = sorted(options)
        scores = [float(self.expected_benefit(firm, observation, name, options[name])) for name in names]
        if any(not isfinite(score) for score in scores):
            raise ValueError("expected benefits must be finite")
        baseline = max(scores)
        weights = [exp((score - baseline) / self.temperature) for score in scores]
        threshold = self.rng.random() * sum(weights)
        for name, weight in zip(names, weights):
            threshold -= weight
            if threshold < 0:
                return options[name]
        return options[names[-1]]


@dataclass
class ImitationChoice:
    candidates: CandidateGenerator
    peer_scores: PeerProvider

    def decide_tasks(self, firm: TaskBasedFirm, observation: MarketObservation) -> TaskPlan:
        options = _options(self.candidates, firm, observation)
        scores = self.peer_scores(firm, observation)
        available = [(float(score), name) for name, score in scores.items() if name in options]
        if not available or any(not isfinite(score) for score, _ in available):
            raise ValueError("peer scores must contain finite observations for a candidate")
        _, chosen = sorted(available, key=lambda pair: (-pair[0], pair[1]))[0]
        return options[chosen]

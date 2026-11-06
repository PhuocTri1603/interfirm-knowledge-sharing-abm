"""Composable 256-player Game 1 strategy and decision engine.

L3-L6 are crossed without exclusions. This module supplies an explicit
information/action contract, NOT researcher-unapproved economic equations.
Market mechanisms and action scoring must be injected by the experiment.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
from math import exp, isfinite
from random import Random
from typing import Mapping, Protocol

from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm
from interfirm_abm.task_economic_policy import MarketObservation
from interfirm_abm.task_experiment_dimensions import STRATEGY_LAYERS

LAYERS = {name: tuple(values) for name, values in STRATEGY_LAYERS}
Plan = tuple[TaskAllocation, ...]


@dataclass(frozen=True)
class StrategyIdentity:
    strategy_id: str
    L3: str
    L4: str
    L5: str
    L6: str

    def __post_init__(self):
        if any(getattr(self, key) not in LAYERS[key] for key in LAYERS):
            raise ValueError("unknown layer option")
        expected = "|".join(f"{key}={getattr(self, key)}" for key in LAYERS)
        if self.strategy_id != expected:
            raise ValueError("strategy ID does not match its four choices")


def strategy_roster() -> tuple[StrategyIdentity, ...]:
    return tuple(
        StrategyIdentity("|".join(f"{key}={value}" for key, value in zip(LAYERS, choices)), *choices)
        for choices in product(*(values for values in LAYERS.values()))
    )


@dataclass(frozen=True)
class Action:
    action_id: str
    allocation: Plan
    offered_price: float | None = None
    investment: float = 0.0
    adoption_cost: float = 0.0

    def __post_init__(self):
        if not self.action_id:
            raise ValueError("action_id required")
        if self.offered_price is not None and (not isfinite(self.offered_price) or self.offered_price < 0):
            raise ValueError("offered price must be nonnegative finite")
        if not isfinite(self.investment) or self.investment < 0:
            raise ValueError("investment must be nonnegative finite")
        if not isfinite(self.adoption_cost) or self.adoption_cost < 0:
            raise ValueError("adoption cost must be nonnegative finite")


@dataclass(frozen=True)
class OwnOutcome:
    round_number: int
    action_id: str
    profit: float


@dataclass(frozen=True)
class DecisionInformation:
    market: MarketObservation
    own_history: tuple[OwnOutcome, ...]


class ActionFactory(Protocol):
    def __call__(self, strategy: StrategyIdentity, firm: TaskBasedFirm, info: DecisionInformation) -> Mapping[str, Action]: ...


class ActionValuation(Protocol):
    def __call__(self, strategy: StrategyIdentity, firm: TaskBasedFirm, info: DecisionInformation, action: Action) -> float: ...


@dataclass(frozen=True)
class DecisionParameters:
    exploration_probability: float
    softmax_temperature: float

    def __post_init__(self):
        if not isfinite(self.exploration_probability) or not 0 <= self.exploration_probability <= 1:
            raise ValueError("exploration_probability must be in [0,1]")
        if not isfinite(self.softmax_temperature) or self.softmax_temperature <= 0:
            raise ValueError("softmax_temperature must be positive finite")


@dataclass
class ComposedStrategyPolicy:
    identity: StrategyIdentity
    action_factory: ActionFactory
    valuation: ActionValuation
    parameters: DecisionParameters
    rng: Random
    own_history: list[OwnOutcome] = field(default_factory=list)
    pending_action: str | None = None
    selected_action: Action | None = None

    def _information(self, observation: MarketObservation, firm: TaskBasedFirm) -> DecisionInformation:
        # Game 1: no rival-specific data, including for L6 self-imitation.
        return DecisionInformation(observation, tuple(self.own_history))

    def decide_action(self, firm: TaskBasedFirm, observation: MarketObservation) -> Action:
        if self.pending_action is not None:
            raise ValueError("pending payoff feedback for prior action")
        info = self._information(observation, firm)
        actions = dict(self.action_factory(self.identity, firm, info))
        if not actions or any(key != action.action_id for key, action in actions.items()):
            raise ValueError("nonempty action map keyed by action_id required")
        for action in actions.values():
            firm.evaluate_allocation(list(action.allocation))
        keys = sorted(actions)
        # L5=price permits explicit offers; no fabricated price clearing rule here.
        if self.identity.L5 == "price" and any(actions[k].offered_price is None for k in keys):
            raise ValueError("price strategy requires offered_price for every action")
        if self.identity.L5 == "adaptive":
            # Own realized payoffs only; valuation may not read rivals.
            realized: dict[str, list[float]] = {}
            for outcome in info.own_history:
                realized.setdefault(outcome.action_id, []).append(outcome.profit)
            scores = {k: sum(realized[k]) / len(realized[k]) if k in realized
                      else float(self.valuation(self.identity, firm, info, actions[k])) for k in keys}
        else:
            scores = {k: float(self.valuation(self.identity, firm, info, actions[k])) for k in keys}
        if any(not isfinite(value) for value in scores.values()):
            raise ValueError("action valuations must be finite")
        method = self.identity.L6
        if method == "optimization":
            chosen = min(keys, key=lambda k: (-scores[k], k))
        elif method == "trial_error":
            incumbent = max(keys, key=lambda k: (scores[k], -keys.index(k)))
            chosen = self.rng.choice(keys) if self.rng.random() < self.parameters.exploration_probability else incumbent
        elif method == "softmax":
            top = max(scores.values())
            weights = [exp((scores[k] - top) / self.parameters.softmax_temperature) for k in keys]
            draw = self.rng.random() * sum(weights)
            chosen = keys[-1]
            for key, weight in zip(keys, weights):
                draw -= weight
                if draw < 0:
                    chosen = key
                    break
        elif method == "imitation":
            # Self-imitation: repeat the available action with the highest
            # realized profit in this firm's own completed history.
            # Ties are deterministic; the first round uses own valuations.
            own_available = [outcome for outcome in info.own_history
                             if outcome.action_id in actions]
            if own_available:
                best = max(outcome.profit for outcome in own_available)
                chosen = min(outcome.action_id for outcome in own_available
                             if outcome.profit == best)
            else:
                chosen = min(keys, key=lambda k: (-scores[k], k))
        else:
            raise ValueError("unknown choice rule")
        self.pending_action = chosen
        self.selected_action = actions[chosen]
        return actions[chosen]

    def decide_tasks(self, firm: TaskBasedFirm, observation: MarketObservation) -> Plan:
        # Compatibility with allocation-only runner. Price bids/investment cannot be
        # settled by that runner; it must not be used to claim price/investment outcomes.
        action = self.decide_action(firm, observation)
        if action.offered_price is not None or action.investment or action.adoption_cost:
            self.pending_action = None
            self.selected_action = None
            raise ValueError("allocation-only market cannot settle price bids, investment or adoption costs")
        return action.allocation

    def observe_payoff(self, firm: TaskBasedFirm, round_number: int, payoff: float) -> None:
        if self.pending_action is None or not isfinite(payoff):
            raise ValueError("missing decision or nonfinite realized payoff")
        self.own_history.append(OwnOutcome(round_number, self.pending_action, float(payoff)))
        self.pending_action = None


def compose_all_policies(action_factory: ActionFactory, valuation: ActionValuation,
                         parameters: DecisionParameters, master_seed: int,
                         ) -> dict[str, ComposedStrategyPolicy]:
    if type(master_seed) is not int or master_seed < 0:
        raise ValueError("master_seed must be nonnegative integer")
    from hashlib import sha256
    policies = {}
    for identity in strategy_roster():
        seed = int.from_bytes(sha256(f"{master_seed}|{identity.strategy_id}".encode()).digest()[:8], "big")
        policies[identity.strategy_id] = ComposedStrategyPolicy(
            identity, action_factory, valuation, parameters, Random(seed))
    return policies

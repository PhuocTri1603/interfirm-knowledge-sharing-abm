"""Compose adaptive price beliefs with explicit candidate task-choice policies.

This is a wiring layer, not an approved model calibration. Callers supply
candidate plans, production/cost evaluators, and all belief parameters.
"""
from __future__ import annotations

from dataclasses import dataclass
from random import Random

from interfirm_abm.task_adaptive_beliefs import AdaptivePriceBeliefs
from interfirm_abm.task_decision_rules import CandidateGenerator, FiniteChoiceOptimization
from interfirm_abm.task_learning_choices import SoftmaxChoice
from interfirm_abm.task_market_beliefs import BeliefBasedProfit, OutputEvaluator, CostEvaluator


@dataclass(frozen=True)
class AdaptivePolicySpecification:
    candidates: CandidateGenerator
    output: OutputEvaluator
    cost: CostEvaluator
    initial_expected_price: float
    adjustment_rate: float

    def profit_evaluator(self):
        beliefs = AdaptivePriceBeliefs(
            initial_price=self.initial_expected_price,
            adjustment_rate=self.adjustment_rate,
        )
        return BeliefBasedProfit(beliefs, self.output, self.cost)


def adaptive_optimization(spec: AdaptivePolicySpecification) -> FiniteChoiceOptimization:
    """Create a fresh optimization policy with its own belief state."""
    return FiniteChoiceOptimization(spec.candidates, spec.profit_evaluator())


def adaptive_softmax(
    spec: AdaptivePolicySpecification, *, temperature: float, rng: Random
) -> SoftmaxChoice:
    """Create a fresh stochastic policy with its own belief state."""
    return SoftmaxChoice(
        spec.candidates, spec.profit_evaluator(), temperature, rng
    )

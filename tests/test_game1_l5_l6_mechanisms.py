"""Controlled A6 L5 and L6 mechanism checks, independent of pilot rankings."""
from unittest.mock import patch

import pytest

from interfirm_abm.task_a6_market import (
    A6Parameters, approved_profiles, l5_candidate_forecast,
    l5_candidate_score, rank_softmax, reference_allocation, run_a6_market,
)
from interfirm_abm.task_based_firm import TaskAllocation
from interfirm_abm.task_l34_economics import L34Parameters
from interfirm_abm.task_strategy_engine import OwnOutcome, choose_self_imitation, strategy_roster


def best_action(method, candidates, prior_price, last_quantity, slope):
    scores = {}
    for key, (quantity, cost) in candidates.items():
        price = l5_candidate_forecast(method, prior_price, last_quantity, quantity, slope)
        scores[key] = l5_candidate_score(method, price, quantity, cost)
    return max(sorted(scores), key=lambda k: scores[k])


def test_competitive_and_cournot_differ_when_own_output_moves_price():
    choices = {"small": (1., .2), "large": (4., 1.)}
    assert best_action("competitive", choices, 2., 1., .5) == "large"
    assert best_action("cournot", choices, 2., 1., .5) == "small"


def test_price_markup_target_differs_from_cournot_profit_maximization():
    choices = {"markup_close": (1., 1.8), "profit_high": (3., 1.)}
    assert best_action("price", choices, 2., 1., .1) == "markup_close"
    assert best_action("cournot", choices, 2., 1., .1) == "profit_high"


def test_adaptive_and_competitive_differ_only_when_beliefs_diverge():
    choices = {"small": (1., .1), "large": (3., 2.2)}
    assert best_action("competitive", choices, 1., 1., .1) == "small"
    assert best_action("adaptive", choices, 2., 1., .1) == "large"
    assert best_action("adaptive", choices, 1., 1., .1) == best_action("competitive", choices, 1., 1., .1)


def test_imitation_changes_when_own_realized_payoff_leader_changes():
    history = (OwnOutcome(1, "a", 4.), OwnOutcome(2, "b", 2.))
    assert choose_self_imitation(history, ("a", "b"), "b") == "a"
    updated = history + (OwnOutcome(3, "b", 8.),)
    assert choose_self_imitation(updated, ("a", "b"), "a") == "b"
    assert choose_self_imitation(updated, ("a",), "a") == "a"


def test_a6_softmax_never_samples_ineligible_action():
    firm = approved_profiles()[0]
    identity = next(x for x in strategy_roster() if x.L6 == "softmax")
    zero = tuple(TaskAllocation(t.task_id, 0., 0.) for t in firm.tasks)
    active = reference_allocation(firm)
    parameters = A6Parameters(10., .01, .15, 1., .5, 11, wage=1e-6, rental=1e-6)
    l34 = L34Parameters(2., .1, .2, .5)
    captured = []

    def spy(scores, temperature, rng):
        captured.append(tuple(scores))
        return rank_softmax(scores, temperature, rng)

    with patch("interfirm_abm.task_a6_market._candidate_plans",
               return_value={"zero": zero, "active": active}), patch(
               "interfirm_abm.task_a6_market.rank_softmax", side_effect=spy):
        result = run_a6_market(firm, 1., parameters, l34_parameters=l34,
                               rounds=2, identities=(identity,))
    assert captured and all(keys == ("active",) for keys in captured)
    assert all(row["action"] == "active" for row in result["players"])
    assert result["research_validated"] is False

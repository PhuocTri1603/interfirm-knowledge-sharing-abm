"""Tests for competitive learning rules."""

import pytest

from interfirm_abm.competitive_learning import (
    performance_triggered_exploration_probability,
)


def test_underperformer_explores_more():
    probability = (
        performance_triggered_exploration_probability(
            own_growth=1.0,
            peer_growth=3.0,
        )
    )

    assert probability == 0.40


def test_outperformer_keeps_baseline():
    probability = (
        performance_triggered_exploration_probability(
            own_growth=3.0,
            peer_growth=1.0,
        )
    )

    assert probability == 0.20


def test_equal_growth_keeps_baseline():
    probability = (
        performance_triggered_exploration_probability(
            own_growth=0.0,
            peer_growth=0.0,
        )
    )

    assert probability == 0.20


def test_invalid_probability_rejected():
    with pytest.raises(ValueError):
        performance_triggered_exploration_probability(
            own_growth=1.0,
            peer_growth=2.0,
            baseline_probability=0.50,
            triggered_probability=0.30,
        )


def test_nonfinite_growth_rejected():
    with pytest.raises(ValueError):
        performance_triggered_exploration_probability(
            own_growth=float("nan"),
            peer_growth=1.0,
        )

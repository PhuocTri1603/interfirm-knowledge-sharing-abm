"""Tests for firm learning policies."""

import numpy as np
import pytest

from interfirm_abm.learning import (
    random_exploration,
    experience_guided_exploration,
)


HISTORY = [
    {"candidate_share": 0.20, "candidate_output": 35.0},
    {"candidate_share": 0.60, "candidate_output": 52.0},
    {"candidate_share": 0.70, "candidate_output": 54.0},
]


def test_random_exploration_within_bounds():
    rng = np.random.default_rng(2026)

    samples = [
        random_exploration(rng)
        for _ in range(1000)
    ]

    assert all(0.05 <= q <= 0.95 for q in samples)


def test_random_exploration_reproducible():
    rng_a = np.random.default_rng(2026)
    rng_b = np.random.default_rng(2026)

    assert random_exploration(rng_a) == random_exploration(rng_b)


def test_empty_history_falls_back_to_random():
    rng = np.random.default_rng(2026)

    candidate = experience_guided_exploration(
        [],
        rng,
    )

    assert 0.05 <= candidate <= 0.95


def test_guided_search_uses_best_observation():
    rng = np.random.default_rng(2026)

    samples = [
        experience_guided_exploration(
            HISTORY,
            rng,
            exploration_probability=0.0,
            search_radius=0.02,
        )
        for _ in range(2000)
    ]

    assert abs(np.mean(samples) - 0.70) < 0.01


def test_full_exploration_ignores_history():
    rng_a = np.random.default_rng(2026)
    rng_b = np.random.default_rng(2026)

    guided = experience_guided_exploration(
        HISTORY,
        rng_a,
        exploration_probability=1.0,
    )

    # The policy first draws a random value to decide
    # whether to explore, then draws the candidate.
    rng_b.random()
    expected = random_exploration(rng_b)

    assert guided == expected


def test_guided_search_respects_bounds():
    rng = np.random.default_rng(2026)

    samples = [
        experience_guided_exploration(
            HISTORY,
            rng,
            exploration_probability=0.0,
            search_radius=0.50,
        )
        for _ in range(1000)
    ]

    assert all(0.05 <= q <= 0.95 for q in samples)


@pytest.mark.parametrize(
    "probability",
    [-0.1, 1.1],
)
def test_invalid_exploration_probability(probability):
    rng = np.random.default_rng(2026)

    with pytest.raises(ValueError):
        experience_guided_exploration(
            HISTORY,
            rng,
            exploration_probability=probability,
        )


def test_invalid_search_radius():
    rng = np.random.default_rng(2026)

    with pytest.raises(ValueError):
        experience_guided_exploration(
            HISTORY,
            rng,
            search_radius=0.0,
        )


def test_history_is_not_modified():
    rng = np.random.default_rng(2026)
    original = [record.copy() for record in HISTORY]

    experience_guided_exploration(
        HISTORY,
        rng,
    )

    assert HISTORY == original

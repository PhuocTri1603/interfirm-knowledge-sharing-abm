"""Tests for matched random number simulations."""

import numpy as np
import pandas as pd

from interfirm_abm.random_schedule import (
    generate_random_schedule,
)
from interfirm_abm.simulation import Simulation


def test_schedule_reproducibility():
    a = generate_random_schedule(20, 50, seed=2026)
    b = generate_random_schedule(20, 50, seed=2026)

    pd.testing.assert_frame_equal(a, b)


def test_schedule_unique_firm_round_pairs():
    schedule = generate_random_schedule(20, 50)

    assert len(schedule) == 1000
    assert not schedule.duplicated(
        ["firm_id", "round"]
    ).any()


def test_policies_share_same_schedule():
    random_sim = Simulation(
        learning_policy="random",
        matched_randomness=True,
        seed=2026,
    )
    guided_sim = Simulation(
        learning_policy="guided",
        matched_randomness=True,
        seed=2026,
    )

    pd.testing.assert_frame_equal(
        random_sim.random_schedule,
        guided_sim.random_schedule,
    )


def test_random_policy_uses_uniform_draw():
    sim = Simulation(
        n_firms=4,
        n_rounds=1,
        learning_policy="random",
        matched_randomness=True,
        seed=2026,
    )

    history = sim.run()

    expected = (
        0.05
        + 0.90 * sim.random_schedule["uniform_draw"]
    )

    assert np.allclose(
        history["candidate_share"],
        expected,
    )


def test_first_round_candidates_are_matched():
    random_sim = Simulation(
        n_firms=20,
        n_rounds=1,
        learning_policy="random",
        matched_randomness=True,
        seed=2026,
    )

    guided_sim = Simulation(
        n_firms=20,
        n_rounds=1,
        learning_policy="guided",
        matched_randomness=True,
        seed=2026,
    )

    random_history = random_sim.run()
    guided_history = guided_sim.run()

    assert np.allclose(
        random_history["candidate_share"],
        guided_history["candidate_share"],
    )


def test_matched_simulation_reproducible():
    a = Simulation(
        n_firms=20,
        n_rounds=10,
        learning_policy="guided",
        matched_randomness=True,
        seed=2026,
    )

    b = Simulation(
        n_firms=20,
        n_rounds=10,
        learning_policy="guided",
        matched_randomness=True,
        seed=2026,
    )

    pd.testing.assert_frame_equal(a.run(), b.run())


def test_both_policies_have_equal_trial_budgets():
    for policy in ("random", "guided"):
        sim = Simulation(
            n_firms=20,
            n_rounds=50,
            learning_policy=policy,
            matched_randomness=True,
        )

        history = sim.run()

        assert len(history) == 1000
        assert (
            history.groupby("firm_id").size() == 50
        ).all()

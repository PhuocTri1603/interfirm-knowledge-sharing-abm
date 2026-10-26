"""Tests for the Game 2 information-only control."""

import pandas as pd
import pytest

from interfirm_abm.simulation import Simulation
from interfirm_abm.competitive_simulation import (
    CompetitiveSimulation,
)


def test_competitive_control_matches_game_one():
    baseline = Simulation(
        seed=2026,
        learning_policy="guided_initial",
        matched_randomness=True,
    )
    competitive = CompetitiveSimulation(seed=2026)

    baseline_history = baseline.run()
    competitive_history = competitive.run()

    pd.testing.assert_frame_equal(
        baseline_history,
        competitive_history,
    )


def test_competitive_observation_is_lagged():
    simulation = CompetitiveSimulation(
        n_firms=4,
        n_rounds=3,
    )
    simulation.run()

    assert len(simulation.observation_log) == 12

    for record in simulation.observation_log:
        assert record["observed_round"] == record["round"] - 1


def test_competitive_observes_only_rivals():
    simulation = CompetitiveSimulation(
        n_firms=4,
        n_rounds=2,
    )
    simulation.run()

    assert all(
        record["n_competitors"] == 3
        for record in simulation.observation_log
    )


def test_competitive_final_snapshot_matches_firms():
    simulation = CompetitiveSimulation(
        n_firms=4,
        n_rounds=3,
    )
    simulation.run()

    snapshot = simulation.public_timeline.get_snapshot(3)

    for record in snapshot:
        firm = simulation.firms[record["firm_id"] - 1]
        assert record["output"] == firm.current_output


def test_competitive_cannot_run_twice():
    simulation = CompetitiveSimulation(
        n_firms=4,
        n_rounds=2,
    )
    simulation.run()

    with pytest.raises(RuntimeError):
        simulation.run()


def test_performance_triggered_policy_runs():
    simulation = CompetitiveSimulation(
        n_firms=20,
        n_rounds=10,
        competitive_policy="performance_triggered",
    )
    history = simulation.run()

    assert len(history) == 200


def test_information_only_keeps_baseline_probability():
    simulation = CompetitiveSimulation(
        n_firms=20,
        n_rounds=10,
        competitive_policy="information_only",
    )
    simulation.run()

    assert all(
        record["exploration_probability"] == 0.20
        for record in simulation.observation_log
    )


def test_performance_trigger_uses_lagged_signals():
    simulation = CompetitiveSimulation(
        n_firms=20,
        n_rounds=10,
        competitive_policy="performance_triggered",
    )
    simulation.run()

    early = [
        record for record in simulation.observation_log
        if record["round"] <= 2
    ]

    assert all(
        record["exploration_probability"] == 0.20
        for record in early
    )

    assert all(
        record["own_growth_pct"] is None
        for record in early
    )


def test_triggered_probability_matches_signal():
    simulation = CompetitiveSimulation(
        n_firms=20,
        n_rounds=10,
        competitive_policy="performance_triggered",
    )
    simulation.run()

    for record in simulation.observation_log:
        if record["own_growth_pct"] is None:
            continue

        expected = (
            0.40
            if record["own_growth_pct"]
            < record["peer_growth_pct"]
            else 0.20
        )

        assert record["exploration_probability"] == expected


def test_competitive_policy_reproducible():
    first = CompetitiveSimulation(
        seed=2026,
        competitive_policy="performance_triggered",
    )
    second = CompetitiveSimulation(
        seed=2026,
        competitive_policy="performance_triggered",
    )

    pd.testing.assert_frame_equal(
        first.run(),
        second.run(),
    )

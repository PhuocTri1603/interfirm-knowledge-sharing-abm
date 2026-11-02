"""Accounting and reproducibility tests for the matched Game 2 experiment."""
import numpy as np
import pandas as pd

from experiments.game2_heterogeneous import run_experiment, summarize


def test_game2_paired_experiment_small_horizon():
    final, observations = run_experiment(rounds=4, seeds=2, population_seed=2026)
    assert len(final) == 400
    assert len(observations) == 1600
    paired, by_seed_family, summary = summarize(final, observations)
    assert len(paired) == 200
    assert len(by_seed_family) == 8
    assert len(summary["by_technology"]) == 4
    assert np.isfinite(summary["overall_mean_efficiency_effect_pp"])
    assert summary["mean_growth_signal_available_share"] == 0.5
    assert 0 <= summary["mean_trigger_activation_share"] <= 1


def test_game2_paired_experiment_reproducible():
    first, observations_first = run_experiment(rounds=3, seeds=1)
    second, observations_second = run_experiment(rounds=3, seeds=1)
    pd.testing.assert_frame_equal(first, second, check_exact=True)
    pd.testing.assert_frame_equal(
        observations_first, observations_second, check_exact=True
    )

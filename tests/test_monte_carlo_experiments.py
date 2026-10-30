"""Tests for matched-seed Monte Carlo experiments."""

import pandas as pd
import pytest

from interfirm_abm.monte_carlo_experiments import run_monte_carlo


@pytest.fixture(scope="module")
def pilot_results():
    return run_monte_carlo(
        seeds=[2026, 2027],
        n_firms=8,
        n_rounds=10,
    )


def test_three_models_per_seed(pilot_results):
    assert len(pilot_results) == 6

    for seed in [2026, 2027]:
        models = set(
            pilot_results.loc[
                pilot_results["seed"] == seed, "model"
            ]
        )
        assert models == {"Game3A", "Game3B", "Game3C"}


def test_valid_experiment_counts(pilot_results):
    assert pilot_results["accepted"].between(0, 80).all()
    assert pilot_results["shared_learning"].between(0, 80).all()


def test_valid_output_metrics(pilot_results):
    assert pilot_results["mean_final_output"].notna().all()
    assert pilot_results["learning_auc"].notna().all()
    assert (pilot_results["mean_final_output"] > 0).all()
    assert (pilot_results["learning_auc"] > 0).all()


def test_share_rate_only_for_game3c(pilot_results):
    other_models = pilot_results[
        pilot_results["model"] != "Game3C"
    ]
    assert other_models["share_rate"].isna().all()

    game3c = pilot_results[
        pilot_results["model"] == "Game3C"
    ]
    assert game3c["share_rate"].between(0, 1).all()


def test_reproducible_results(pilot_results):
    repeated = run_monte_carlo(
        seeds=[2026, 2027],
        n_firms=8,
        n_rounds=10,
    )

    pd.testing.assert_frame_equal(
        pilot_results.reset_index(drop=True),
        repeated.reset_index(drop=True),
    )

"""Tests for Game 3C matched-seed ablation experiments."""

import pandas as pd
from pandas.testing import assert_frame_equal

from interfirm_abm.ablation_experiments import (
    ABLATION_SCENARIOS,
    run_ablation,
)


def test_ablation_runs_four_scenarios_per_seed():
    results = run_ablation(
        seeds=[2026, 2027],
        n_firms=8,
        n_rounds=10,
    )

    assert len(results) == 8
    assert set(results["scenario"]) == set(ABLATION_SCENARIOS)

    for seed in [2026, 2027]:
        subset = results[results["seed"] == seed]
        assert len(subset) == 4
        assert subset["scenario"].nunique() == 4


def test_ablation_mechanism_switches():
    results = run_ablation(
        seeds=[2026],
        n_firms=8,
        n_rounds=10,
    )

    for _, row in results.iterrows():
        expected = ABLATION_SCENARIOS[row["scenario"]]

        assert bool(row["selective_disclosure"]) == expected[0]
        assert bool(row["conditional_reciprocity"]) == expected[1]


def test_ablation_output_metrics():
    n_firms = 8
    n_rounds = 10

    results = run_ablation(
        seeds=[2026],
        n_firms=n_firms,
        n_rounds=n_rounds,
    )

    assert (results["mean_final_output"] > 0).all()
    assert (results["learning_auc"] > 0).all()

    assert results["accepted"].between(
        0, n_firms * n_rounds
    ).all()

    assert (
        results["published"] <= results["accepted"]
    ).all()

    assert results["share_rate"].between(0, 1).all()
    assert results["access_rate"].between(0, 1).all()
    assert results["shared_learning"].between(
        0, n_firms * n_rounds
    ).all()


def test_ablation_open_sharing_and_access():
    results = run_ablation(
        seeds=[2026],
        n_firms=8,
        n_rounds=15,
    )

    open_sharing = results[
        results["scenario"] == "OpenSharing"
    ].iloc[0]

    assert open_sharing["published"] == open_sharing["accepted"]
    assert open_sharing["access_rate"] == 1.0

    disclosure_only = results[
        results["scenario"] == "DisclosureOnly"
    ].iloc[0]

    assert disclosure_only["access_rate"] == 1.0

    reciprocity_only = results[
        results["scenario"] == "ReciprocityOnly"
    ].iloc[0]

    assert reciprocity_only["published"] == reciprocity_only["accepted"]


def test_ablation_reproducibility():
    kwargs = {
        "seeds": [2026, 2027],
        "n_firms": 8,
        "n_rounds": 10,
    }

    first = run_ablation(**kwargs)
    second = run_ablation(**kwargs)

    assert_frame_equal(first, second, check_exact=True)

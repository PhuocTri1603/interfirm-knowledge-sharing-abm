"""Check reproducibility and algebra of the factorial sensitivity experiment."""

import pytest

from experiments.game1_factorial_sensitivity import (
    EXPLORATION_PROBABILITIES, SEARCH_RADII, CHECKPOINTS,
    run_experiment, export_results,
)


def test_factorial_design():
    assert len(EXPLORATION_PROBABILITIES) == 5
    assert len(SEARCH_RADII) == 5
    assert len(CHECKPOINTS) == 5
    assert 0.20 in EXPLORATION_PROBABILITIES
    assert 0.10 in SEARCH_RADII


def test_one_seed_factorial_matches_expected_structure(tmp_path):
    paired = run_experiment(n_seeds=1)
    assert len(paired) == 25 * 20 * 5
    assert paired["advantage_pct"].notna().all()
    assert paired["seed"].nunique() == 1
    assert paired.groupby(["exploration_probability", "search_radius", "round"]).size().eq(20).all()
    # All configurations must share exactly the same random-policy benchmark.
    assert paired.groupby(["seed", "round", "firm_id"])["random_output"].nunique().eq(1).all()
    seed_means = export_results(paired, tmp_path)
    assert len(seed_means) == 25 * 5
    assert (tmp_path / "seed_interaction_contrast.csv").exists()


def test_reject_invalid_seed_count():
    with pytest.raises(ValueError):
        run_experiment(n_seeds=0)

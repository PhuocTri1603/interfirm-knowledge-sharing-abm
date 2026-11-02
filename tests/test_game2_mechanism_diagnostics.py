"""Game 2 mechanism diagnostics: accounting and invariants."""
import numpy as np
import pandas as pd

from experiments.diagnose_game2_mechanisms import diagnose


def test_mechanism_diagnostic_paired_paths_and_round_one():
    paths, paired = diagnose(rounds=4, seeds=1, population_seed=2026)
    assert len(paths) == 4 * 4 * 2
    assert len(paired) == 4 * 4
    assert paths.mean_efficiency_pct.between(0, 100 + 1e-7).all()
    assert paths.global_search_rate.between(0, 1).all()
    assert paths.acceptance_rate.between(0, 1).all()
    assert paths.trigger_rate.between(0, 1).all()
    assert (paths.loc[paths["round"] == 1, "global_search_rate"] == 1).all()
    assert (paths.loc[paths["round"] <= 2, "trigger_rate"] == 0).all()
    assert (paths.loc[paths.policy == "information_only", "trigger_rate"] == 0).all()
    assert (paths.loc[(paths.policy == "performance_triggered") &
                      (paths["round"] >= 3), "signal_availability_rate"] == 1).all()
    assert np.allclose(
        paired.loc[paired["round"] == 1, "triggered_minus_control_pp"], 0
    )


def test_mechanism_diagnostic_deterministic():
    a, b = diagnose(rounds=3, seeds=1)
    c, d = diagnose(rounds=3, seeds=1)
    pd.testing.assert_frame_equal(a, c, check_exact=True)
    pd.testing.assert_frame_equal(b, d, check_exact=True)

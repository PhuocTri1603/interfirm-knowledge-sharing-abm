import numpy as np
import pandas as pd

from interfirm_abm.cross_technology_simulation import (
    CrossTechnologySimulation,
)
from interfirm_abm.production_optimum import optimal_output


def test_normalized_transfer_gain_consistency():
    sim = CrossTechnologySimulation(
        seed=2026,
        sharing_probability=0.60,
        transfer_policy="cross_technology",
    )
    sim.run()

    df = pd.DataFrame(sim.transfer_log)

    expected_potential = df.apply(
        lambda row: max(
            0.0,
            optimal_output(row["recipient_technology"])
            - row["recipient_previous_output"],
        ),
        axis=1,
    )

    assert np.allclose(
        df["remaining_potential_before_transfer"],
        expected_potential,
    )

    valid = df[~df["near_optimum"]].copy()

    expected_normalized = (
        valid["recipient_output_gain"]
        / valid["remaining_potential_before_transfer"]
    )

    assert np.allclose(
        valid["normalized_transfer_gain"],
        expected_normalized,
    )

    assert (
        valid["normalized_transfer_gain"] >= -1e-10
    ).all()

    assert (
        valid["normalized_transfer_gain"] <= 1 + 1e-8
    ).all()


def test_normalization_does_not_change_learning():
    baseline = CrossTechnologySimulation(
        seed=2027,
        sharing_probability=0.30,
        transfer_policy="mixed",
    )

    history = baseline.run()

    assert len(history) == 1000
    assert len(baseline.learning_log) == 1000
    assert len(baseline.transfer_log) > 0
    assert all(
        "normalized_transfer_gain" in record
        for record in baseline.transfer_log
    )

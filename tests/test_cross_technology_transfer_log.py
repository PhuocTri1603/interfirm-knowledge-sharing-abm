import numpy as np
import pandas as pd
import pytest

from interfirm_abm.cross_technology_simulation import (
    CrossTechnologySimulation,
)


@pytest.mark.parametrize(
    "policy",
    ["same_technology", "cross_technology", "mixed"],
)
def test_transfer_log_consistency(policy):
    sim = CrossTechnologySimulation(
        seed=2026,
        sharing_probability=0.60,
        transfer_policy=policy,
    )
    sim.run()

    transfers = pd.DataFrame(sim.transfer_log)
    learning = pd.DataFrame(sim.learning_log)

    assert len(transfers) == learning["learning_source"].eq("shared").sum()
    assert len(transfers) > 0
    assert (transfers["source_round"] < transfers["round"]).all()
    assert (transfers["source_id"] != transfers["recipient_id"]).all()

    if policy == "same_technology":
        assert (
            transfers["source_technology"]
            == transfers["recipient_technology"]
        ).all()
    elif policy == "cross_technology":
        assert (
            transfers["source_technology"]
            != transfers["recipient_technology"]
        ).all()

    expected_gain = np.maximum(
        transfers["recipient_candidate_output"]
        - transfers["recipient_previous_output"],
        0.0,
    )
    assert np.allclose(
        transfers["recipient_output_gain"],
        expected_gain,
    )
    assert (
        transfers["recipient_accepted"]
        == (expected_gain > 0)
    ).all()


def test_transfer_log_preserves_one_experiment_per_round():
    sim = CrossTechnologySimulation(
        seed=2027,
        sharing_probability=0.60,
        transfer_policy="mixed",
    )
    history = sim.run()
    transfers = pd.DataFrame(sim.transfer_log)

    assert len(history) == 1000
    assert not history.duplicated(["firm_id", "round"]).any()
    assert not transfers.duplicated(["recipient_id", "round"]).any()

    merged = transfers.merge(
        history,
        left_on=["recipient_id", "round"],
        right_on=["firm_id", "round"],
        validate="one_to_one",
    )

    assert len(merged) == len(transfers)
    assert np.allclose(
        merged["recipient_candidate_share"],
        merged["candidate_share"],
    )
    assert np.allclose(
        merged["recipient_candidate_output"],
        merged["candidate_output"],
    )

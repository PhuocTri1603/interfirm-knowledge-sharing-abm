import numpy as np
import pandas as pd

from interfirm_abm.cross_technology_simulation import (
    CrossTechnologySimulation,
)
from interfirm_abm.production_optimum import optimal_capital_share


def test_allocation_distance_and_previous_state():
    sim = CrossTechnologySimulation(
        seed=2026,
        sharing_probability=0.60,
        transfer_policy="cross_technology",
    )
    history = sim.run()
    transfers = pd.DataFrame(sim.transfer_log)

    expected_distance = transfers.apply(
        lambda row: abs(
            row["recipient_candidate_share"]
            - optimal_capital_share(row["recipient_technology"])
        ),
        axis=1,
    )

    assert np.allclose(
        transfers["allocation_distance_to_optimum"],
        expected_distance,
    )

    assert transfers["recipient_previous_share"].between(
        0.05, 0.95
    ).all()

    assert np.allclose(
        transfers["recipient_previous_output"],
        transfers.apply(
            lambda row: sim.firms[
                int(row["recipient_id"]) - 1
            ].produce(row["recipient_previous_share"]),
            axis=1,
        ),
    )

    assert len(history) == 1000
    assert len(transfers) > 0

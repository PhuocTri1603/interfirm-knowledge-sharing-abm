"""
Competitive learning decision rules.

Public performance signals affect exploration intensity,
not direct imitation of competitors' private decisions.
"""

import numpy as np


def performance_triggered_exploration_probability(
    own_growth,
    peer_growth,
    baseline_probability=0.20,
    triggered_probability=0.40,
):
    """
    Increase exploration when the firm underperforms peers.

    Growth rates must use the same units.
    """

    values = (
        own_growth,
        peer_growth,
        baseline_probability,
        triggered_probability,
    )

    if not all(np.isfinite(value) for value in values):
        raise ValueError("All inputs must be finite.")

    if not (
        0 <= baseline_probability
        <= triggered_probability
        <= 1
    ):
        raise ValueError("Invalid exploration probabilities.")

    if own_growth < peer_growth:
        return float(triggered_probability)

    return float(baseline_probability)

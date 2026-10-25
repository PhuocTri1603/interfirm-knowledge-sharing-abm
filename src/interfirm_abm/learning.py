"""
Learning policies for firm experimentation.

Decisions use observed experimental histories,
not direct access to production functions.
"""

import numpy as np


def random_exploration(rng, lower=0.05, upper=0.95):
    """Draw an independent candidate allocation."""
    return float(rng.uniform(lower, upper))


def experience_guided_exploration(
    history,
    rng,
    exploration_probability=0.20,
    search_radius=0.10,
    lower=0.05,
    upper=0.95,
):
    """
    Choose a candidate using observed experiments.

    With probability exploration_probability,
    explore the entire allocation range.

    Otherwise, search around the best previously
    observed candidate allocation.

    If history is empty, explore randomly.
    """

    if not 0 <= exploration_probability <= 1:
        raise ValueError(
            "exploration_probability must be in [0, 1]."
        )

    if not search_radius > 0:
        raise ValueError(
            "search_radius must be positive."
        )

    if not 0 < lower < upper < 1:
        raise ValueError(
            "Invalid allocation bounds."
        )

    if not history or rng.random() < exploration_probability:
        return random_exploration(rng, lower, upper)

    best_observation = max(
        history,
        key=lambda record: record["candidate_output"],
    )

    center = best_observation["candidate_share"]

    candidate = rng.normal(
        loc=center,
        scale=search_radius,
    )

    return float(np.clip(candidate, lower, upper))

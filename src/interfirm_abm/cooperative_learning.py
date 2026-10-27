import numpy as np


def select_shared_experiment(
    shared_history,
    recipient_technology,
    rng,
):
    """
    Select one successful experiment shared by a firm
    using the same production technology.

    Each eligible experiment has equal probability.

    Returns a copy of the selected record, or None
    when no eligible experiment is available.
    """

    eligible = [
        record
        for record in shared_history
        if record["technology"] == recipient_technology
        and record["accepted"] is True
    ]

    if not eligible:
        return None

    index = int(rng.integers(0, len(eligible)))

    return eligible[index].copy()


def shared_knowledge_exploration(
    shared_history,
    recipient_technology,
    rng,
    search_radius=0.10,
    lower=0.05,
    upper=0.95,
):
    """
    Generate a candidate near a randomly selected
    successful experiment from a same-technology peer.

    Does not evaluate the recipient's production function
    before selecting the candidate.
    """

    if not np.isfinite(search_radius) or search_radius <= 0:
        raise ValueError("search_radius must be positive and finite.")

    if not 0 < lower < upper < 1:
        raise ValueError("Invalid allocation bounds.")

    selected = select_shared_experiment(
        shared_history=shared_history,
        recipient_technology=recipient_technology,
        rng=rng,
    )

    if selected is None:
        return None

    center = selected["candidate_share"]

    candidate = rng.normal(
        loc=center,
        scale=search_radius,
    )

    return float(np.clip(candidate, lower, upper))

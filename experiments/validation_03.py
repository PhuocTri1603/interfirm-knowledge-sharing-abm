"""
Validation 03: Knowledge-Guided Exploration.

Compare independent exploration with exploration guided
by another firm's experimental history.

This is a deterministic mechanism check, not a causal
estimate of knowledge-sharing benefits.
"""

import numpy as np
import pandas as pd

from interfirm_abm.production import (
    cobb_douglas,
    leontief,
    linear,
    ces,
)

TECHNOLOGIES = {
    "Cobb-Douglas": cobb_douglas,
    "Leontief": leontief,
    "Linear": linear,
    "CES": ces,
}

TOTAL_RESOURCES = 100.0
BASELINE_SHARE = 0.50
EXPERIMENT_BUDGET = 3

CANDIDATES = np.array([
    0.20, 0.35, 0.50, 0.60,
    0.65, 0.70, 0.75, 0.90,
])


def output_at_share(production, q):
    return float(
        production(
            TOTAL_RESOURCES * q,
            TOTAL_RESOURCES * (1 - q),
        )
    )


def independent_order():
    """Fixed exploration order without donor information."""
    return [0.20, 0.35, 0.60, 0.65, 0.70, 0.75, 0.90]


def donor_guided_order(donor_production):
    """Rank candidates using the donor's production outcomes."""
    candidates = [
        float(q) for q in CANDIDATES
        if not np.isclose(q, BASELINE_SHARE)
    ]

    return sorted(
        candidates,
        key=lambda q: (-output_at_share(donor_production, q), q),
    )


def explore(receiver_production, candidate_order):
    best_q = BASELINE_SHARE
    best_output = output_at_share(
        receiver_production, best_q
    )

    for q in candidate_order[:EXPERIMENT_BUDGET]:
        trial_output = output_at_share(
            receiver_production, q
        )

        if trial_output > best_output:
            best_q = q
            best_output = trial_output

    return best_q, best_output


def run_experiment():
    records = []

    for donor_name, donor_function in TECHNOLOGIES.items():
        for receiver_name, receiver_function in TECHNOLOGIES.items():
            if donor_name == receiver_name:
                continue

            baseline_output = output_at_share(
                receiver_function, BASELINE_SHARE
            )

            independent_q, independent_output = explore(
                receiver_function,
                independent_order(),
            )

            guided_q, guided_output = explore(
                receiver_function,
                donor_guided_order(donor_function),
            )

            records.append({
                "donor": donor_name,
                "receiver": receiver_name,
                "independent_q": independent_q,
                "guided_q": guided_q,
                "independent_gain_pct": (
                    independent_output / baseline_output - 1
                ) * 100,
                "guided_gain_pct": (
                    guided_output / baseline_output - 1
                ) * 100,
                "knowledge_advantage_pct_points": (
                    guided_output - independent_output
                ) / baseline_output * 100,
            })

    return pd.DataFrame(records)


if __name__ == "__main__":
    results = run_experiment()

    print("\n===== KNOWLEDGE-GUIDED EXPLORATION =====")
    print(results.round(4).to_string(index=False))

    advantage = results["knowledge_advantage_pct_points"]

    print("\n===== SUMMARY =====")
    print("Total pairs:", len(results))
    print("Guided better:", int((advantage > 1e-8).sum()))
    print("Guided worse:", int((advantage < -1e-8).sum()))
    print("Equal:", int((advantage.abs() <= 1e-8).sum()))
    print(
        "Mean advantage (percentage points):",
        round(float(advantage.mean()), 4),
    )

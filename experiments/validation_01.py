"""Validation 01: Production responses and technological distance."""

from itertools import combinations

import numpy as np
import pandas as pd

from interfirm_abm.production import (
    cobb_douglas,
    leontief,
    linear,
    ces,
)

TOTAL_RESOURCES = 100.0
CAPITAL_SHARES = [0.25, 0.50, 0.70, 0.75]
BASELINE_SHARE = 0.50

TECHNOLOGIES = {
    "Cobb-Douglas": cobb_douglas,
    "Leontief": leontief,
    "Linear": linear,
    "CES": ces,
}


def calculate_responses():
    records = []

    for name, production in TECHNOLOGIES.items():
        baseline = production(
            TOTAL_RESOURCES * BASELINE_SHARE,
            TOTAL_RESOURCES * (1 - BASELINE_SHARE),
        )

        for q in CAPITAL_SHARES:
            K = TOTAL_RESOURCES * q
            L = TOTAL_RESOURCES * (1 - q)

            output = production(K, L)
            response = output / baseline - 1

            records.append({
                "technology": name,
                "capital_share": q,
                "output": float(output),
                "response": float(response),
            })

    return pd.DataFrame(records)


def calculate_distances(responses):
    pivot = responses.pivot(
        index="capital_share",
        columns="technology",
        values="response",
    )

    records = []

    for tech_i, tech_j in combinations(TECHNOLOGIES, 2):
        difference = pivot[tech_i] - pivot[tech_j]
        distance = np.sqrt(np.mean(difference**2))

        records.append({
            "technology_i": tech_i,
            "technology_j": tech_j,
            "distance": float(distance),
        })

    return pd.DataFrame(records)


if __name__ == "__main__":
    responses = calculate_responses()
    distances = calculate_distances(responses)

    print("\n===== RELATIVE PRODUCTION RESPONSES =====")
    print(
        responses.pivot(
            index="capital_share",
            columns="technology",
            values="response",
        ).round(6).to_string()
    )

    print("\n===== BEHAVIORAL TECHNOLOGICAL DISTANCE =====")
    print(
        distances.sort_values("distance")
        .round(6)
        .to_string(index=False)
    )

    print("\n===== VALIDATION COMPLETE =====")

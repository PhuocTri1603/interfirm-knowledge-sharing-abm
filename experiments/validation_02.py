"""
Validation 02: Can imitation hurt?

Tests whether copying another firm's output-maximizing
capital allocation improves the recipient's production.
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
CAPITAL_SHARES = np.linspace(0.05, 0.95, 91)


def output_at_share(production, q):
    K = TOTAL_RESOURCES * q
    L = TOTAL_RESOURCES * (1 - q)
    return float(production(K, L))


def find_best_allocation(production):
    outputs = np.array([
        output_at_share(production, q)
        for q in CAPITAL_SHARES
    ])

    best_index = int(np.argmax(outputs))

    return float(CAPITAL_SHARES[best_index])


def run_experiment():
    records = []

    for donor_name, donor_function in TECHNOLOGIES.items():
        donor_best_share = find_best_allocation(donor_function)

        for receiver_name, receiver_function in TECHNOLOGIES.items():
            if donor_name == receiver_name:
                continue

            baseline_output = output_at_share(
                receiver_function, BASELINE_SHARE
            )

            imitation_output = output_at_share(
                receiver_function, donor_best_share
            )

            change = imitation_output / baseline_output - 1

            records.append({
                "donor": donor_name,
                "receiver": receiver_name,
                "donor_best_share": donor_best_share,
                "receiver_baseline_output": baseline_output,
                "receiver_imitation_output": imitation_output,
                "receiver_change_pct": change * 100,
            })

    return pd.DataFrame(records)


if __name__ == "__main__":
    results = run_experiment()

    print("\n===== DONOR OPTIMAL ALLOCATIONS =====")
    for name, production in TECHNOLOGIES.items():
        print(
            f"{name:15s}: "
            f"q* = {find_best_allocation(production):.2f}"
        )

    print("\n===== IMITATION RESULTS =====")
    print(
        results[
            ["donor", "receiver", "donor_best_share",
             "receiver_change_pct"]
        ].round(4).to_string(index=False)
    )

    print("\n===== SUMMARY =====")
    print("Total donor-receiver pairs:", len(results))
    print(
        "Imitation improves output:",
        int((results.receiver_change_pct > 1e-8).sum())
    )
    print(
        "Imitation reduces output:",
        int((results.receiver_change_pct < -1e-8).sum())
    )
    print(
        "No material change:",
        int((results.receiver_change_pct.abs() <= 1e-8).sum())
    )

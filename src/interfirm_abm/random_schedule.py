"""
Common random number schedule for matched simulations.

Each firm-round receives the same pre-generated
random variables across learning policies.
"""

import numpy as np
import pandas as pd


def generate_random_schedule(
    n_firms=20,
    n_rounds=50,
    seed=2026,
):
    if not isinstance(n_firms, int) or n_firms <= 0:
        raise ValueError("n_firms must be positive.")

    if not isinstance(n_rounds, int) or n_rounds <= 0:
        raise ValueError("n_rounds must be positive.")

    rng = np.random.default_rng(seed)

    records = []

    for round_number in range(1, n_rounds + 1):
        for firm_id in range(1, n_firms + 1):
            records.append({
                "round": round_number,
                "firm_id": firm_id,
                "exploration_draw": float(rng.random()),
                "uniform_draw": float(rng.random()),
                "normal_draw": float(rng.normal()),
            })

    return pd.DataFrame(records)


if __name__ == "__main__":
    schedule = generate_random_schedule()

    print("===== RANDOM SCHEDULE =====")
    print(schedule.head(8).round(4).to_string(index=False))

    print("\n===== VALIDATION =====")
    print("Total rows:", len(schedule))
    print(
        "Unique firm-round pairs:",
        len(schedule[["firm_id", "round"]].drop_duplicates())
    )

    repeated = generate_random_schedule(seed=2026)

    print(
        "Reproducible:",
        schedule.equals(repeated)
    )

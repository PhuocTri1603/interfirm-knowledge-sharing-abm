"""
Validation 04: Randomized Exploration Benchmark.

Compare donor-guided exploration with independent
random exploration under identical trial budgets.

The random benchmark is repeated with controlled seeds.
"""

import numpy as np
import pandas as pd

from experiments.validation_03 import (
    TECHNOLOGIES,
    CANDIDATES,
    BASELINE_SHARE,
    EXPERIMENT_BUDGET,
    donor_guided_order,
    explore,
    output_at_share,
)

N_REPLICATIONS = 1000
RANDOM_SEED = 2026


def run_experiment():
    rng = np.random.default_rng(RANDOM_SEED)

    candidates = [
        float(q) for q in CANDIDATES
        if not np.isclose(q, BASELINE_SHARE)
    ]

    records = []

    for donor_name, donor_function in TECHNOLOGIES.items():
        for receiver_name, receiver_function in TECHNOLOGIES.items():
            if donor_name == receiver_name:
                continue

            baseline = output_at_share(
                receiver_function, BASELINE_SHARE
            )

            guided_q, guided_output = explore(
                receiver_function,
                donor_guided_order(donor_function),
            )

            guided_gain = 100 * (
                guided_output / baseline - 1
            )

            random_gains = []

            for _ in range(N_REPLICATIONS):
                random_order = rng.permutation(candidates)

                _, random_output = explore(
                    receiver_function,
                    random_order,
                )

                random_gains.append(
                    100 * (random_output / baseline - 1)
                )

            random_gains = np.asarray(random_gains)

            records.append({
                "donor": donor_name,
                "receiver": receiver_name,
                "guided_q": guided_q,
                "guided_gain_pct": guided_gain,
                "random_mean_gain_pct": random_gains.mean(),
                "random_std_gain_pct": random_gains.std(),
                "knowledge_advantage_pp": (
                    guided_gain - random_gains.mean()
                ),
                "guided_beats_random_probability": (
                    np.mean(guided_gain > random_gains + 1e-8)
                ),
            })

    return pd.DataFrame(records)


if __name__ == "__main__":
    results = run_experiment()

    print("\n===== RANDOMIZED BENCHMARK =====")
    print(results.round(4).to_string(index=False))

    advantage = results["knowledge_advantage_pp"]

    print("\n===== SUMMARY =====")
    print("Total pairs:", len(results))
    print("Monte Carlo replications per pair:", N_REPLICATIONS)
    print("Guided better than random mean:",
          int((advantage > 1e-8).sum()))
    print("Guided worse than random mean:",
          int((advantage < -1e-8).sum()))
    print("Equal:",
          int((advantage.abs() <= 1e-8).sum()))
    print("Mean knowledge advantage (pp):",
          round(float(advantage.mean()), 4))

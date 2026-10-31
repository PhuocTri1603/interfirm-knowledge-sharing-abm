"""Reproducible, exactly balanced heterogeneous Game 1 population.

Sampling quotas are experimental assumptions, not empirically calibrated.
"""
import numpy as np
import pandas as pd

TECHNOLOGIES = ("Cobb-Douglas", "Leontief", "Linear", "CES")
STRATA = (
    ("strong_labor", 0.10, 0.40),
    ("moderate_labor", 0.40, 0.50),
    ("moderate_capital", 0.50, 0.60),
    ("strong_capital", 0.60, 0.90),
)
# Per-family counts sum to 25. Two families have 13 labor-oriented,
# and two have 13 capital-oriented: exactly 50 of each overall.
QUOTAS = (
    (7, 6, 6, 6),
    (6, 6, 6, 7),
    (7, 6, 6, 6),
    (6, 6, 6, 7),
)


def generate_population(seed=2026):
    """Return 100 immutable-in-design firm configurations.

    Draw alpha once using a population seed independent of learning seeds.
    A=1, budget=100 and CES rho=-0.5 are controlled baseline assumptions.
    """
    if not isinstance(seed, (int, np.integer)) or seed < 0:
        raise ValueError("seed must be a nonnegative integer")
    rng = np.random.default_rng(seed)
    records = []
    for technology, quotas in zip(TECHNOLOGIES, QUOTAS):
        members = []
        for (stratum, low, high), count in zip(STRATA, quotas):
            for alpha in rng.uniform(low, high, size=count):
                members.append({
                    "technology": technology,
                    "stratum": stratum,
                    "alpha": float(alpha),
                    "A": 1.0,
                    "rho": -0.5 if technology == "CES" else np.nan,
                    "budget": 100.0,
                    "initial_capital_share": 0.5,
                    "population_seed": int(seed),
                })
        rng.shuffle(members)
        records.extend(members)
    rng.shuffle(records)
    for index, record in enumerate(records, start=1):
        record["firm_id"] = index
    return pd.DataFrame.from_records(records)[
        ["firm_id", "technology", "stratum", "alpha", "A", "rho",
         "budget", "initial_capital_share", "population_seed"]
    ]

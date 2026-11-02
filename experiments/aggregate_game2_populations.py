"""Aggregate paired Game 2 effects across independently drawn populations."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def aggregate(root):
    files = sorted(Path(root).glob("**/paired_seed_family_effects.csv"))
    if len(files) < 2:
        raise ValueError("At least two independent population artifacts required")
    data = pd.concat([pd.read_csv(p) for p in files], ignore_index=True)
    if data.population_seed.nunique() != len(files):
        raise ValueError("Duplicate or missing population seeds")
    nseeds = data.groupby("population_seed").learning_seed.nunique()
    if nseeds.nunique() != 1:
        raise ValueError("Unbalanced learning seeds across populations")
    population_family = data.groupby(
        ["population_seed", "technology"], as_index=False
    ).triggered_minus_control_pp.mean()
    population_overall = population_family.groupby(
        "population_seed", as_index=False
    ).triggered_minus_control_pp.mean()
    summary = []
    for name, frame in [("overall", population_overall)] + list(
        population_family.groupby("technology")
    ):
        values = frame.triggered_minus_control_pp.to_numpy()
        mean = float(values.mean())
        se = float(values.std(ddof=1) / np.sqrt(len(values)))
        summary.append({
            "group": name, "independent_populations": len(values),
            "learning_seeds_per_population": int(nseeds.iloc[0]),
            "mean_effect_pp": mean,
            "population_level_se_pp": se,
            "normal_approx_95_ci_pp": [mean - 1.96 * se, mean + 1.96 * se],
            "population_effects_pp": [float(x) for x in values],
        })
    return data, population_family, population_overall, summary


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input-dir", type=Path, required=True)
    p.add_argument("--export-dir", type=Path, required=True)
    a = p.parse_args()
    data, family, overall, summary = aggregate(a.input_dir)
    a.export_dir.mkdir(parents=True, exist_ok=True)
    data.to_csv(a.export_dir / "all_seed_family_effects.csv", index=False)
    family.to_csv(a.export_dir / "population_family_effects.csv", index=False)
    overall.to_csv(a.export_dir / "population_overall_effects.csv", index=False)
    (a.export_dir / "cross_population_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    print("GAME 2 CROSS-POPULATION SUMMARY")
    print(json.dumps(summary, indent=2))

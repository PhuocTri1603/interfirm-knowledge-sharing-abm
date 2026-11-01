"""Descriptive diagnostic: alpha extremity versus Guided advantage, by production family.

Uses archived paired outcomes; does not alter learning, production, or random draws.
Alpha distance is a preference-extremity proxy, NOT measured search-space distance.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def analyze(root):
    records = []
    for folder in sorted(root.glob("population-*-rounds-*")):
        df = pd.read_csv(folder / "paired_firm_outcomes.csv")
        assert len(df) == 10000
        df["effect_pp"] = df["guided"] - df["random"]
        assert np.allclose(df["effect_pp"], df["guided_minus_random_efficiency_pp"], atol=1e-8)
        df["alpha_extremity"] = (df["alpha"] - 0.5).abs()
        df["alpha_band"] = pd.cut(df["alpha_extremity"], [0, .1, .2, .4],
                                  labels=["near", "intermediate", "extreme"],
                                  include_lowest=True)
        assert df["alpha_band"].notna().all()
        population = int(folder.name.split("-")[1])
        horizon = int(folder.name.split("-")[3])
        for (family, band), part in df.groupby(["technology", "alpha_band"], observed=True):
            per_seed = part.groupby("seed")["effect_pp"].mean()
            assert len(per_seed) == 100
            records.append({"population_seed": population, "rounds": horizon,
                            "technology": family, "alpha_band": str(band),
                            "n_firms_per_seed": len(part) // 100,
                            "mean_effect_pp": float(per_seed.mean()),
                            "seed_sd_pp": float(per_seed.std(ddof=1))})
    result = pd.DataFrame(records)
    assert result.groupby(["population_seed", "rounds", "technology"])["n_firms_per_seed"].sum().eq(25).all()
    summary = []
    for (horizon, family, band), part in result.groupby(["rounds", "technology", "alpha_band"], observed=True):
        summary.append({"rounds": int(horizon), "technology": family, "alpha_band": band,
                        "populations": int(len(part)),
                        "mean_pp": float(part.mean_effect_pp.mean()),
                        "min_pp": float(part.mean_effect_pp.min()),
                        "max_pp": float(part.mean_effect_pp.max()),
                        "firm_counts_per_population": part.n_firms_per_seed.tolist()})
    return {"diagnostic": "descriptive alpha-extremity stratification (not causal)",
            "limitations": ["Alpha extremity is not initial distance to optimum",
                            "No control for curvature or kink geometry",
                            "Shared learning seeds across populations",
                            "No multiplicity adjustment or mechanism identification"],
            "per_population": records, "across_population": summary}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.artifacts)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print("DESCRIPTIVE MECHANISM DIAGNOSTIC PASSED")
    for x in result["across_population"]:
        print(f'{x["rounds"]:3} {x["technology"]:14} {x["alpha_band"]:12} '
              f'{x["mean_pp"]:+.6f} [{x["min_pp"]:+.6f}, {x["max_pp"]:+.6f}] pp')

"""Post-process existing heterogeneous Game 1 final outcomes; no new simulation."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def analyze(paired: pd.DataFrame) -> dict:
    required = {"seed", "firm_id", "technology", "stratum", "alpha",
                "random", "guided", "guided_minus_random_efficiency_pp"}
    if missing := required - set(paired.columns):
        raise ValueError(f"Missing paired columns: {sorted(missing)}")
    if paired.duplicated(["seed", "firm_id"]).any():
        raise ValueError("Duplicate seed/firm_id pairs")
    if paired[list(required - {"technology", "stratum"})].isna().any().any():
        raise ValueError("Missing numeric fields")
    if not np.allclose(paired["guided"] - paired["random"],
                       paired["guided_minus_random_efficiency_pp"], atol=1e-9):
        raise ValueError("Inconsistent paired differences")
    if not paired[["guided", "random"]].ge(-1e-8).all().all() or not paired[["guided", "random"]].le(100 + 1e-7).all().all():
        raise ValueError("Efficiency out of bounds")
    expected = {"Cobb-Douglas", "Leontief", "Linear", "CES"}
    if set(paired.technology.unique()) != expected:
        raise ValueError("Unexpected technology families")
    counts = paired.groupby(["seed", "technology"]).size()
    if not counts.eq(25).all() or not paired.groupby("seed").size().eq(100).all():
        raise ValueError("Population composition is inconsistent")
    if not paired.groupby("seed").apply(lambda x: (x.alpha < .5).sum(), include_groups=False).eq(50).all():
        raise ValueError("Capital/labor orientation not balanced")
    out = {}
    for dimension in ("overall", "technology", "stratum", "orientation"):
        data = paired.copy()
        if dimension == "overall":
            data["group"] = "all"
        elif dimension == "orientation":
            data["group"] = np.where(data.alpha < .5, "labor", "capital")
        else:
            data["group"] = data[dimension]
        seed_groups = data.groupby(["group", "seed"], as_index=False).agg(
            effect=("guided_minus_random_efficiency_pp", "mean"),
            random_efficiency=("random", "mean"),
            guided_efficiency=("guided", "mean"),
            firms=("firm_id", "size"))
        rows = []
        for group, g in seed_groups.groupby("group"):
            effects = g.effect.to_numpy()
            n = len(effects)
            se = float(effects.std(ddof=1) / np.sqrt(n)) if n > 1 else None
            mean = float(effects.mean())
            rows.append({"group": str(group), "seeds": n,
                         "firms_per_seed": int(g.firms.iloc[0]),
                         "random_efficiency_pct": float(g.random_efficiency.mean()),
                         "guided_efficiency_pct": float(g.guided_efficiency.mean()),
                         "mean_effect_pp": mean, "seed_level_se_pp": se,
                         "normal_approx_95_ci_pp": [mean-1.96*se, mean+1.96*se] if se is not None else None})
        out[dimension] = sorted(rows, key=lambda x: x["group"])
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    results = analyze(pd.read_csv(args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2) + "\n")
    for dimension, rows in results.items():
        for row in rows:
            print(f"{dimension}: {row['group']}: {row['mean_effect_pp']:+.6f} pp")


if __name__ == "__main__":
    main()

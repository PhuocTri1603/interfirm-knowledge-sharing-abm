"""Independent standard-library audit of archived Game 1 population-sensitivity artifacts."""
import argparse
import csv
import json
import math
import re
import statistics
from pathlib import Path


def rows(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def stats(values):
    mean = statistics.mean(values)
    se = statistics.stdev(values) / math.sqrt(len(values))
    return mean, mean - 1.96 * se, mean + 1.96 * se


def close(a, b, tol=1e-8):
    if not math.isclose(a, b, rel_tol=0, abs_tol=tol):
        raise AssertionError(f"Mismatch: independently calculated {a} vs reported {b}")


def audit(directory):
    match = re.search(r"population-(\d+)-rounds-(\d+)-", directory.name)
    if not match:
        raise AssertionError(f"Unrecognized artifact directory: {directory}")
    pop, horizon = map(int, match.groups())
    raw = rows(directory / "paired_firm_outcomes.csv")
    final = rows(directory / "final_firm_outcomes.csv")
    summary = json.loads((directory / "summary.json").read_text())
    subgroups = json.loads((directory / "subgroup_summary.json").read_text())
    assert len(raw) == 10000 and len(final) == 20000
    assert int(summary["learning_seeds"]) == 100
    assert int(summary["population_seed"]) == pop
    assert int(summary["rounds"]) == horizon
    assert len({(r["seed"], r["firm_id"]) for r in raw}) == len(raw)
    assert len({(r["seed"], r["firm_id"], r["policy"]) for r in final}) == len(final)
    by_seed = {}
    by_family = {}
    by_strength = {}
    for r in raw:
        seed, family = int(r["seed"]), r["technology"]
        effect = float(r["guided"]) - float(r["random"])
        close(effect, float(r["guided_minus_random_efficiency_pp"]))
        assert -1e-7 <= float(r["guided"]) <= 100 + 1e-7
        assert -1e-7 <= float(r["random"]) <= 100 + 1e-7
        by_seed.setdefault(seed, []).append(effect)
        by_family.setdefault((family, seed), []).append(effect)
        strength = "strong" if r["stratum"].startswith("strong_") else "moderate"
        by_strength.setdefault((family, seed, strength), []).append(effect)
    assert len(by_seed) == 100 and all(len(v) == 100 for v in by_seed.values())
    assert len(by_family) == 400 and all(len(v) == 25 for v in by_family.values())
    overall = stats([statistics.mean(by_seed[s]) for s in sorted(by_seed)])
    close(overall[0], summary["mean_efficiency_effect_pp"])
    for i, value in enumerate(overall[1:]):
        close(value, summary["normal_approx_95_ci_pp"][i])
    family_effects = {}
    contrasts = {}
    for family in ("CES", "Cobb-Douglas", "Leontief", "Linear"):
        family_effects[family] = stats([statistics.mean(by_family[(family, s)]) for s in sorted(by_seed)])
        contrast = [
            statistics.mean(by_strength[(family, s, "strong")]) -
            statistics.mean(by_strength[(family, s, "moderate")])
            for s in sorted(by_seed)
        ]
        contrasts[family] = stats(contrast)
        reported = next(x for x in subgroups["technology"] if x["group"] == family)
        close(family_effects[family][0], reported["mean_effect_pp"])
        for i in (0, 1):
            close(family_effects[family][i + 1], reported["normal_approx_95_ci_pp"][i])
        reported_contrast = next(x for x in subgroups["within_technology_strength_contrast"] if x["technology"] == family)
        close(contrasts[family][0], reported_contrast["strong_minus_moderate_pp"])
        for i in (0, 1):
            close(contrasts[family][i + 1], reported_contrast["normal_approx_95_ci_pp"][i])
    return {"population_seed": pop, "rounds": horizon, "overall_pp": overall[0],
            "family_pp": {k: v[0] for k, v in family_effects.items()},
            "strong_minus_moderate_pp": {k: v[0] for k, v in contrasts.items()}}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--artifacts", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    folders = sorted(x for x in args.artifacts.iterdir() if x.is_dir() and x.name.startswith("population-"))
    assert len(folders) == 15, f"Expected 15 artifacts; found {len(folders)}"
    results = [audit(folder) for folder in folders]
    assert {(x["population_seed"], x["rounds"]) for x in results} == {
        (p, h) for p in range(2026, 2031) for h in (50, 100, 200)}
    summaries = []
    for horizon in (50, 100, 200):
        group = [x for x in results if x["rounds"] == horizon]
        record = {"rounds": horizon, "populations": 5, "overall": {
            "mean_pp": statistics.mean(x["overall_pp"] for x in group),
            "range_pp": [min(x["overall_pp"] for x in group), max(x["overall_pp"] for x in group)]},
            "families": {}, "contrasts": {}}
        for family in ("CES", "Cobb-Douglas", "Leontief", "Linear"):
            for key, output in (("family_pp", "families"), ("strong_minus_moderate_pp", "contrasts")):
                values = [x[key][family] for x in group]
                record[output][family] = {"mean_pp": statistics.mean(values),
                                          "min_pp": min(values), "max_pp": max(values),
                                          "positive_populations": sum(v > 0 for v in values)}
        summaries.append(record)
    output = {"audit": "independent CSV recomputation (standard library)",
              "population_horizon_cells": len(results), "paired_rows_total": 150000,
              "final_rows_total": 300000, "per_population_horizon": results,
              "across_population": summaries}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print("INDEPENDENT AUDIT PASSED: 15 artifacts, 150000 paired rows, 300000 final rows")
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()

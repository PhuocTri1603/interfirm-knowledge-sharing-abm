"""Post-hoc initial-optimality-gap diagnostics. No simulation changes.

Descriptive correlations are NOT causal effects. Initial gap is deterministically
derived from technology and alpha; regression controls can be collinear.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from interfirm_abm.firm import Firm
from interfirm_abm.production_optimum import optimal_capital_share, optimal_output


def run(root):
    results = []
    for folder in sorted(root.glob("population-*-rounds-*")):
        df = pd.read_csv(folder / "paired_firm_outcomes.csv")
        assert len(df) == 10000
        pop = int(folder.name.split("-")[1])
        rounds = int(folder.name.split("-")[3])
        firms = df.drop_duplicates("firm_id").sort_values("firm_id")
        assert len(firms) == 100
        geometry = []
        for r in firms.itertuples(index=False):
            firm = Firm(firm_id=int(r.firm_id), technology=r.technology, alpha=float(r.alpha),
                        budget=100.0, rho=-0.5)
            optimum = optimal_output(r.technology, 100.0, float(r.alpha), -0.5, 1.0)
            initial = firm.produce(0.5)
            geometry.append({"firm_id": int(r.firm_id),
                             "optimal_share": optimal_capital_share(r.technology, float(r.alpha), -0.5),
                             "initial_gap_pp": 100 * (1 - initial / optimum)})
        enriched = df.merge(pd.DataFrame(geometry), on="firm_id", validate="many_to_one")
        enriched["effect_pp"] = enriched["guided"] - enriched["random"]
        enriched["alpha_extremity"] = (enriched["alpha"] - .5).abs()
        enriched["share_distance"] = (enriched["optimal_share"] - .5).abs()
        enriched["gap_tertile"] = enriched.groupby("technology")["initial_gap_pp"].transform(
            lambda x: pd.qcut(x.rank(method="first"), 3, labels=["low", "medium", "high"]))
        for family, part in enriched.groupby("technology"):
            firm_data = part.groupby("firm_id", as_index=False).agg(
                effect_pp=("effect_pp", "mean"), initial_gap_pp=("initial_gap_pp", "first"),
                share_distance=("share_distance", "first"),
                alpha_extremity=("alpha_extremity", "first"))
            assert len(firm_data) == 25
            correlations = {}
            for name in ("initial_gap_pp", "share_distance", "alpha_extremity"):
                x = firm_data[name].to_numpy()
                y = firm_data["effect_pp"].to_numpy()
                correlations[name] = float(np.corrcoef(x, y)[0, 1]) if np.std(x) > 1e-12 else None
            by_tertile = {}
            for band, group in part.groupby("gap_tertile", observed=True):
                by_tertile[str(band)] = float(group.effect_pp.mean())
            results.append({"population_seed": pop, "rounds": rounds, "technology": family,
                            "correlation_firm_mean": correlations,
                            "mean_initial_gap_pp": float(firm_data.initial_gap_pp.mean()),
                            "gap_tertile_effect_pp": by_tertile,
                            "n_firms": 25, "n_learning_seeds": 100})
    assert len(results) == 60
    aggregate = []
    for (h, family), g in pd.DataFrame(results).groupby(["rounds", "technology"]):
        item = {"rounds": int(h), "technology": family, "populations": len(g),
                "gap_tertile_effect_pp": {
                    band: float(np.mean([d[band] for d in g.gap_tertile_effect_pp]))
                    for band in ("low", "medium", "high")},
                "correlation_firm_mean": {
                    key: float(np.mean([d[key] for d in g.correlation_firm_mean if d[key] is not None]))
                    if any(d[key] is not None for d in g.correlation_firm_mean) else None
                    for key in ("initial_gap_pp", "share_distance", "alpha_extremity")}}
        aggregate.append(item)
    return {"source_run": 41210955389, "n_population_horizon_family": 60,
            "caveats": ["Post-hoc descriptive association only",
                        "Initial gap is mathematically determined by alpha and technology",
                        "25 firms per technology per population; 5 populations",
                        "Tertiles rank within technology and population",
                        "No causal attribution, multiple-testing correction or independent replications"],
            "cells": results, "summary": aggregate}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--artifacts", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    result = run(a.artifacts)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2) + "\n")
    print("INITIAL GAP DIAGNOSTIC PASSED")
    for r in result["summary"]:
        print(json.dumps(r, sort_keys=True))

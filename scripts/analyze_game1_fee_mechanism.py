"""Aggregate paired adoption-fee mechanism audits across ten profiles and three seeds."""
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path("results/game1_mechanism")
files = sorted(ROOT.rglob("fee_profile_*.csv"))
expected = {(p, s, seed) for p in range(10) for s in (0.5, 1.0, 2.0) for seed in (11, 23, 47)}
found = set()
rows = []
for path in files:
    with path.open(newline="") as f:
        records = list(csv.DictReader(f))
    if len(records) != 9:
        raise AssertionError(f"Expected 9 strategies in {path}")
    for r in records:
        key = (int(r["profile_id"].removeprefix("F")) - 1, float(r["sigma"]), int(r["seed"]))
        found.add(key)
        rows.append(r)
if found != expected or len(rows) != 810:
    raise AssertionError(f"Expected 90 matched markets/810 strategy records, got {len(found)}/{len(rows)}")
round_files = sorted(ROOT.rglob("fee_rounds_profile_*.csv"))
if len(round_files) != 90:
    raise AssertionError(f"Expected 90 round panels, got {len(round_files)}")
groups = defaultdict(list)
for r in rows:
    if r["strategy_id"] == "L3=cost_adjusted|L4=profit_based":
        groups[float(r["sigma"])].append(r)
out = []
for sigma, sample in sorted(groups.items()):
    if len(sample) != 30:
        raise AssertionError("Expected 10 profiles x 3 seeds per sigma")
    metrics = ("delta_profit", "delta_revenue", "quantity_effect", "price_effect",
               "interaction_effect", "delta_variable_cost", "delta_adjustment_cost",
               "delta_adoption_cost", "delta_labor_used", "delta_capital_used",
               "delta_active_ai_task_rounds", "delta_output")
    summary = {"sigma": sigma, "paired_markets": len(sample)}
    for metric in metrics:
        summary["mean_" + metric] = sum(float(r[metric]) for r in sample) / len(sample)
    out.append(summary)
target = ROOT / "ten_profile_fee_mechanism_summary.csv"
with target.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)
print("PASS 10 profiles x 3 sigmas x 3 seeds; round panels and decomposition complete")
for row in out:
    print(row)

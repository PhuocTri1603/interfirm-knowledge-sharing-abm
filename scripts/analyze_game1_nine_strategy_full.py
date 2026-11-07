"""Aggregate full-sample scenario outputs; fail if any profile-sigma-strategy is absent."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path("results/game1_nine_strategy")
files = sorted(root.rglob("*_summary.csv"))
if len(files) != 30:
    raise SystemExit(f"INCOMPLETE: expected 30 summary partitions, got {len(files)}")
df = pd.concat([pd.read_csv(p) for p in files], ignore_index=True)
if len(df) != 2700 or df.groupby(["profile_id", "sigma"]).size().ne(9).any():
    raise SystemExit("INCOMPLETE: expected 100 profiles x 3 sigma x 9 strategies")
if df[["profile_id", "sigma", "strategy_id"]].duplicated().any():
    raise SystemExit("DUPLICATE strategy-profile-sigma")
root.mkdir(parents=True, exist_ok=True)
agg = df.groupby(["sigma", "strategy_id"], as_index=False).agg(
    mean_cumulative_profit=("cumulative_profit", "mean"),
    median_cumulative_profit=("cumulative_profit", "median"),
    win_count=("winner", "sum"),
    mean_active_ai_share=("active_ai_share", "mean"),
    mean_ever_adopted_share=("ai_ever_adopted_share", "mean"),
    mean_shutdown_share=("shutdown_share", "mean"))
agg["win_rate"] = agg["win_count"] / 100
agg.to_csv(root / "aggregate_by_sigma_strategy.csv", index=False)
df.to_csv(root / "all_profile_strategy_summary.csv", index=False)
for metric, ylabel, filename in [
    ("mean_cumulative_profit", "Mean cumulative profit", "cumulative_profit.png"),
    ("win_rate", "Fraction of configurations won", "win_rate.png"),
    ("mean_active_ai_share", "Mean active AI task share", "active_ai_share.png")]:
    pivot = agg.pivot(index="strategy_id", columns="sigma", values=metric).sort_index()
    ax = pivot.plot(kind="bar", figsize=(13, 6), rot=80)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Strategy")
    ax.figure.tight_layout()
    ax.figure.savefig(root / filename, dpi=150)
    plt.close(ax.figure)
print("FULL SAMPLE AGGREGATED: 100 profiles x 3 sigma x 9 strategies x 200 rounds")
print(agg.to_string(index=False))
print("research_validated: false; scenario parameters not calibrated")

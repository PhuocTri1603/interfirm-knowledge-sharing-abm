"""Aggregate complete paired robustness design; reject missing cells."""
from pathlib import Path
import pandas as pd

root = Path("results/game1_robustness")
files = sorted(root.glob("robust_sigma_*.csv"))
if len(files) != 18:
    raise SystemExit(f"INCOMPLETE robustness: expected 18 partitions, got {len(files)}")
df = pd.concat([pd.read_csv(p) for p in files], ignore_index=True)
keys = ["profile_id", "sigma", "scenario", "seed", "strategy_id"]
if len(df) != 2430 or df.duplicated(keys).any():
    raise SystemExit("INCOMPLETE or DUPLICATE robustness observations")
if df.groupby(["sigma", "scenario", "seed"]).size().ne(90).any():
    raise SystemExit("INCOMPLETE: 10 profiles x 9 strategies required per treatment")
if df.groupby(["profile_id", "sigma", "scenario"]).seed.nunique().ne(3).any():
    raise SystemExit("INCOMPLETE paired seeds")
summary = df.groupby(["sigma", "scenario", "strategy_id"], as_index=False).agg(
    mean_profit=("cumulative_profit", "mean"),
    profit_std=("cumulative_profit", "std"),
    win_rate=("winner", "mean"),
    active_ai_share=("active_ai_share", "mean"),
    shutdown_share=("shutdown_share", "mean"))
summary.to_csv(root / "robustness_summary.csv", index=False)
# Explicitly compare paired seeds on the SAME profile and scenario.
by_seed = df.groupby(["sigma", "scenario", "seed", "strategy_id"], as_index=False).agg(
    mean_profit=("cumulative_profit", "mean"),
    win_rate=("winner", "mean"))
by_seed.to_csv(root / "robustness_by_seed.csv", index=False)
# Economic treatment difference versus the baseline for identical profile, seed, sigma, strategy.
baseline = df[df.scenario == "baseline"][keys[:2] + keys[3:] + ["cumulative_profit"]].rename(
    columns={"cumulative_profit": "baseline_profit"})
paired = df.merge(baseline, on=["profile_id", "sigma", "seed", "strategy_id"], validate="many_to_one")
paired["profit_delta_vs_baseline"] = paired.cumulative_profit - paired.baseline_profit
paired.groupby(["sigma", "scenario", "strategy_id"], as_index=False).agg(
    mean_profit_delta=("profit_delta_vs_baseline", "mean"),
    median_profit_delta=("profit_delta_vs_baseline", "median")).to_csv(
    root / "paired_parameter_effects.csv", index=False)
print("ROBUSTNESS COMPLETE: 10 profiles x 3 sigma x 3 scenarios x 3 seeds x 9 strategies")
print(summary.to_string(index=False))
print("research_validated: false")

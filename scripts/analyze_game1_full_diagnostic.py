"""Analyze the archived Game 1 diagnostic CSV files without scientific claims."""
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, pstdev

root = Path("downloaded")
configs = sorted(p for p in root.iterdir() if p.is_dir() and p.name.startswith("C"))
if len(configs) != 100:
    raise ValueError(f"Expected 100 configurations, got {len(configs)}")
groups = defaultdict(list)
signatures = set()
market_totals = []
winners = defaultdict(int)
for folder in configs:
    with (folder / "ranking_by_configuration.csv").open(newline="") as f:
        rows = list(csv.DictReader(f))
    with (folder / "market_trajectory.csv").open(newline="") as f:
        markets = list(csv.DictReader(f))
    if len(rows) != 256 or len(markets) != 200:
        raise ValueError(f"Incomplete configuration {folder.name}")
    ranks = sorted(rows, key=lambda r: int(r["rank"]))
    winners[ranks[0]["player_id"]] += 1
    signatures.add(tuple(sorted((r["player_id"], round(float(r["total_benefit"]), 8))
                                for r in rows)))
    market_totals.append(sum(float(r["total_profit"]) for r in markets))
    for row in rows:
        fields = dict(part.split("=", 1) for part in row["player_id"].split("|"))
        value = float(row["total_benefit"])
        for layer in ("L3", "L4", "L5", "L6"):
            groups[(layer, fields[layer])].append(value)
report = {
    "source_run_id": 41965861687,
    "execution_status": "diagnostic_only_not_scientifically_validated",
    "configurations": len(configs),
    "distinct_ranking_payoff_signatures": len(signatures),
    "market_total_profit_per_config": {
        "min": min(market_totals), "max": max(market_totals),
        "mean": mean(market_totals), "std": pstdev(market_totals),
    },
    "group_comparisons": [
        {"layer": layer, "option": option, "observations": len(values),
         "mean_total_profit": mean(values), "std": pstdev(values),
         "min": min(values), "max": max(values)}
        for (layer, option), values in sorted(groups.items())
    ],
    "rank_one_strategy_frequency": dict(sorted(winners.items())),
    "warning": "This is a test fixture with identical initial conditions, one action per player, and administratively assigned prices. Do not interpret as economic strategy performance.",
}
Path("analysis").mkdir(exist_ok=True)
Path("analysis/diagnostic_comparison.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))

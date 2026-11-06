"""Single-configuration A6 pilot; all numeric values are TEST-ONLY, NOT approved."""
import csv
import json
from collections import Counter
from pathlib import Path
from statistics import mean, median

from interfirm_abm.task_a6_market import A6Parameters, approved_profiles, run_a6_market
from interfirm_abm.task_l34_economics import L34Parameters

OUTPUT = Path("artifacts/game1_a6_pilot")
OUTPUT.mkdir(parents=True, exist_ok=True)

# Illustrative scenario, not calibrated or approved for scientific inference.
a6 = A6Parameters(demand_intercept=10.0, demand_slope=0.01,
                  epsilon=0.15, temperature=1.0, imitation_probability=0.5,
                  seed=11, wage=0.001, rental=0.001)
l34 = L34Parameters(capacity_ratio=2.0, adjustment_unit_cost=0.001,
                    efficiency_gain=0.2, adoption_fee=0.001)
firm = approved_profiles()[0]
result = run_a6_market(firm, 1.0, a6, l34_parameters=l34, rounds=200)
players, market, ranking = result["players"], result["market"], result["ranking"]
assert len(players) == 256 * 200
assert len(market) == 200 and len(ranking) == 256
assert all(row["profit"] == row["price"] * row["quantity"] - row["cost"] or
           abs(row["profit"] - (row["price"] * row["quantity"] - row["cost"])) < 1e-8
           for row in players)
assert not result["research_validated"]

def write_csv(filename, rows):
    with (OUTPUT / filename).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

write_csv("players.csv", players)
write_csv("market.csv", market)
write_csv("ranking.csv", [{"rank": i, "strategy_id": sid, "cumulative_profit": profit}
                          for i, (sid, profit) in enumerate(ranking, 1)])
shutdown = sum(row["action"] == "shutdown" for row in players)
profits = [profit for _, profit in ranking]
summary = {
    "experiment": "Game1_A6_single_configuration_pilot",
    "research_validated": False,
    "calibration_status": "illustrative_parameters_only_not_researcher_approved",
    "profile_id": firm.firm_id, "sigma": 1.0,
    "strategies": 256, "rounds": 200, "observations": len(players),
    "parameters_a6": vars(a6), "parameters_l34": vars(l34),
    "shutdown_observations": shutdown,
    "shutdown_rate": shutdown / len(players),
    "final_market_price": market[-1]["price"],
    "final_market_quantity": market[-1]["quantity"],
    "mean_cumulative_profit": mean(profits),
    "median_cumulative_profit": median(profits),
    "min_cumulative_profit": min(profits),
    "max_cumulative_profit": max(profits),
    "unique_cumulative_profit_values": len(set(profits)),
    "top_10": [{"strategy_id": sid, "cumulative_profit": p} for sid, p in ranking[:10]],
    "action_counts": dict(Counter(row["action"] for row in players)),
}
(OUTPUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print("A6_PILOT_SUMMARY=" + json.dumps(summary, sort_keys=True))

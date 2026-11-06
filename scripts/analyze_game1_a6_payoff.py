"""Post-process a Game 1 A6 run without changing policies or parameters.

Payoff = realized firm profit. Market payoff = sum of all players' profits.
Cumulative market payoff is an accounting sum, NOT a welfare or efficiency measure.
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from math import fsum, isclose
from pathlib import Path
from statistics import mean

ROOT = Path("artifacts/game1_a6_pilot")
OUTPUT = ROOT / "payoff"
OUTPUT.mkdir(parents=True, exist_ok=True)


def load_csv(path):
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


players = load_csv(ROOT / "players.csv")
market = load_csv(ROOT / "market.csv")
assert players and len(market) == 200 and len(players) == 256 * len(market)
by_round = defaultdict(list)
by_strategy = defaultdict(list)
for row in players:
    by_round[int(row["round"])].append(row)
    by_strategy[row["strategy_id"]].append(row)
assert len(by_strategy) == 256
assert sorted(by_round) == list(range(1, 201))
assert all(len(group) == 256 for group in by_round.values())

def save_csv(name, data):
    with (OUTPUT / name).open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(data[0]))
        writer.writeheader()
        writer.writerows(data)

market_payoffs = []
running = 0.0
for entry in market:
    t = int(entry["round"])
    group = by_round[t]
    flow = fsum(float(x["profit"]) for x in group)
    reported_flow = float(entry["profit"])
    assert isclose(flow, reported_flow, rel_tol=1e-9, abs_tol=1e-7), (t, flow, reported_flow)
    revenue = fsum(float(x["price"]) * float(x["quantity"]) for x in group)
    costs = fsum(float(x["cost"]) for x in group)
    assert isclose(flow, revenue - costs, rel_tol=1e-9, abs_tol=1e-7)
    running += flow
    market_payoffs.append({
        "round": t, "market_payoff": flow, "cumulative_market_payoff": running,
        "total_revenue": revenue, "total_cost": costs,
        "price": float(entry["price"]), "quantity": float(entry["quantity"])
    })
save_csv("market_payoff_by_round.csv", market_payoffs)

winner_rows = []
for sid, group in by_strategy.items():
    group.sort(key=lambda x: int(x["round"]))
    cumulative = fsum(float(x["profit"]) for x in group)
    assert isclose(cumulative, float(group[-1]["cumulative_profit"]),
                   rel_tol=1e-9, abs_tol=1e-7)
    winner_rows.append({"strategy_id": sid, "cumulative_payoff": cumulative,
                        "mean_round_payoff": cumulative / 200,
                        "final_round_payoff": float(group[-1]["profit"])})
winner_rows.sort(key=lambda x: (-x["cumulative_payoff"], x["strategy_id"]))
best = winner_rows[0]["cumulative_payoff"]
winners = [x for x in winner_rows if isclose(x["cumulative_payoff"], best, rel_tol=1e-12, abs_tol=1e-8)]
for i, x in enumerate(winner_rows):
    x["competition_rank"] = 1 + sum(y["cumulative_payoff"] > x["cumulative_payoff"] + 1e-8 for y in winner_rows)
save_csv("strategy_ranking.csv", winner_rows)

# Optional per-round leaders, with explicit ties; same simultaneous market.
leaders = []
for t in range(1, 201):
    top = max(float(x["cumulative_profit"]) for x in by_round[t])
    ids = sorted(x["strategy_id"] for x in by_round[t] if isclose(
        float(x["cumulative_profit"]), top, abs_tol=1e-8, rel_tol=1e-12))
    leaders.append({"round": t, "leader_payoff": top, "n_co_leaders": len(ids),
                    "leaders": ";".join(ids)})
save_csv("leaders_by_round.csv", leaders)

def window_mean(first, last):
    return mean(x["market_payoff"] for x in market_payoffs[first - 1:last])

first20 = window_mean(1, 20)
last20 = window_mean(181, 200)
delta = last20 - first20
summary = {
    "experiment": "Game1_A6_pilot_payoff_analysis", "research_validated": False,
    "market_payoff_definition": "sum of realized firm profits in each round, not social welfare",
    "configurations": 1, "strategies": 256, "rounds": 200,
    "winner_count": len(winners), "winning_payoff": best,
    "winners": [x["strategy_id"] for x in winners],
    "market_payoff_first_round": market_payoffs[0]["market_payoff"],
    "market_payoff_last_round": market_payoffs[-1]["market_payoff"],
    "market_payoff_first_20_mean": first20,
    "market_payoff_last_20_mean": last20,
    "change_last_20_minus_first_20": delta,
    "market_payoff_increased_by_window_mean": delta > 0,
    "cumulative_market_payoff_200_rounds": running,
    "market_payoff_min_round": min(x["market_payoff"] for x in market_payoffs),
    "market_payoff_max_round": max(x["market_payoff"] for x in market_payoffs),
    "rounds_with_negative_market_payoff": sum(x["market_payoff"] < 0 for x in market_payoffs),
    "conclusions_limited_to": "F001, sigma=1, seed=11, explicitly illustrative parameters",
}
assert isclose(running, fsum(x["cumulative_payoff"] for x in winner_rows),
               rel_tol=1e-9, abs_tol=1e-6)
(OUTPUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

# Two standalone charts, created without plotting packages.
def svg_line(name, data, label, color="#2472a3"):
    w,h=900,360
    vals=[float(v) for v in data]
    lo,hi=min(vals),max(vals)
    span=max(hi-lo, 1e-9)
    points=" ".join(f"{58+i*810/(len(vals)-1):.2f},{308-270*(v-lo)/span:.2f}" for i,v in enumerate(vals))
    markup=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<rect width="{w}" height="{h}" fill="white"/>
<text x="58" y="24" font-family="Arial" font-size="18" fill="#222">{label}</text>
<line x1="58" y1="308" x2="868" y2="308" stroke="#777"/>
<line x1="58" y1="38" x2="58" y2="308" stroke="#777"/>
<text x="8" y="44" font-family="Arial" font-size="12" fill="#555">{hi:.2f}</text>
<text x="8" y="308" font-family="Arial" font-size="12" fill="#555">{lo:.2f}</text>
<text x="58" y="330" font-family="Arial" font-size="12">Round 1</text>
<text x="805" y="330" font-family="Arial" font-size="12">Round 200</text>
<polyline fill="none" stroke="{color}" stroke-width="2" points="{points}"/>
</svg>'''
    (OUTPUT/name).write_text(markup, encoding="utf-8")

svg_line("market_payoff_per_round.svg",
         [x["market_payoff"] for x in market_payoffs],
         "Total realized market payoff per round")
svg_line("market_payoff_cumulative.svg",
         [x["cumulative_market_payoff"] for x in market_payoffs],
         "Cumulative total realized market payoff")

print("A6_PAYOFF_SUMMARY=" + json.dumps(summary, sort_keys=True))

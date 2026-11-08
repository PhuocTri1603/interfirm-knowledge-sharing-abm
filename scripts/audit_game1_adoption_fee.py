"""Paired adoption-fee mechanism audit, holding profile/sigma/seed fixed.

Output: accounting-exact revenue decomposition, not a causal mediation estimate.
"""
import argparse
import csv
from collections import defaultdict
from pathlib import Path

from interfirm_abm.game1_nine_strategy import Game1Params, run_game1
from interfirm_abm.task_a6_market import approved_profiles


def parameters(seed, fee_multiplier):
    wage = .5 / 51.5
    return Game1Params(demand_intercept=2., demand_slope=1. / 9.,
                       wage=wage, rental=wage, adjustment_delta=.1,
                       adoption_fee=(.1 * .5 / 20.) * fee_multiplier,
                       eta=.1, epsilon=.15, seed=seed)


def totals(result):
    by_strategy = defaultdict(list)
    for row in result["players"]:
        by_strategy[row["strategy_id"]].append(row)
    return {s: {k: sum(r[k] for r in records) for k in (
        "revenue", "variable_cost", "adjustment_cost", "adoption_cost",
        "output", "newly_adopted_count", "active_ai_count")}
        for s, records in by_strategy.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile-index", type=int, default=0)
    ap.add_argument("--sigma", type=float, choices=(.5, 1., 2.), default=2.)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--out", default="results/game1_mechanism")
    a = ap.parse_args()
    profiles = approved_profiles()
    if not 0 <= a.profile_index < len(profiles):
        raise ValueError("profile index outside approved population")
    firm = profiles[a.profile_index]
    baseline = run_game1(firm, a.sigma, parameters(a.seed, 1.), audit=True)
    expensive = run_game1(firm, a.sigma, parameters(a.seed, 3.), audit=True)
    b, e = totals(baseline), totals(expensive)
    records = []
    for sid in sorted(b):
        base = b[sid]
        new = e[sid]
        # Exact decomposition at the round level, using baseline P and Q:
        # Δ(PQ) = P0 ΔQ + Q0 ΔP + ΔP ΔQ.
        br = [r for r in baseline["players"] if r["strategy_id"] == sid]
        er = [r for r in expensive["players"] if r["strategy_id"] == sid]
        quantity = sum(x["price"] * (y["output"] - x["output"]) for x, y in zip(br, er))
        price = sum(x["output"] * (y["price"] - x["price"]) for x, y in zip(br, er))
        interaction = sum((y["price"]-x["price"])*(y["output"]-x["output"]) for x,y in zip(br,er))
        delta_revenue = new["revenue"] - base["revenue"]
        delta_variable = new["variable_cost"] - base["variable_cost"]
        delta_adjustment = new["adjustment_cost"] - base["adjustment_cost"]
        delta_adoption = new["adoption_cost"] - base["adoption_cost"]
        delta_profit = delta_revenue - delta_variable - delta_adjustment - delta_adoption
        if abs(delta_revenue - quantity - price - interaction) > 1e-7:
            raise AssertionError("Revenue decomposition mismatch")
        if abs(delta_profit - (
            er[-1]["cumulative_profit"] - br[-1]["cumulative_profit"])) > 1e-7:
            raise AssertionError("Profit decomposition mismatch")
        records.append(dict(profile_id=firm.firm_id, sigma=a.sigma, seed=a.seed,
            strategy_id=sid, delta_profit=delta_profit, delta_revenue=delta_revenue,
            quantity_effect=quantity, price_effect=price, interaction_effect=interaction,
            delta_variable_cost=delta_variable, delta_adjustment_cost=delta_adjustment,
            delta_adoption_cost=delta_adoption,
            delta_new_adoptions=new["newly_adopted_count"]-base["newly_adopted_count"],
            delta_active_ai_task_rounds=new["active_ai_count"]-base["active_ai_count"],
            delta_output=new["output"]-base["output"]))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    target = out / f"fee_profile_{a.profile_index}_sigma_{a.sigma:g}_seed_{a.seed}.csv"
    with target.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    print(f"PASS accounting decomposition: {target}")
    print("WARNING: price and quantity effects are path-dependent accounting terms,")
    print("not identified causal effects. All nine firms respond simultaneously.")


if __name__ == "__main__":
    main()

"""Pre-specified robustness sample: paired profiles, seeds, and economic scenarios.

This is a sensitivity check, not a replacement for the 100-profile main result.
"""
import argparse
import csv
from collections import defaultdict
from pathlib import Path

from interfirm_abm.game1_nine_strategy import Game1Params, run_game1
from interfirm_abm.task_a6_market import approved_profiles

SEEDS = (11, 23, 47)
SCENARIOS = ("baseline", "capital_expensive", "adoption_expensive")


def parameters(scenario, seed):
    wage = 0.5 / 51.5
    rental = wage * (1.5 if scenario == "capital_expensive" else 1.0)
    fee = (0.1 * 0.5 / 20.0) * (3.0 if scenario == "adoption_expensive" else 1.0)
    return Game1Params(demand_intercept=2., demand_slope=1. / 9.,
                       wage=wage, rental=rental, adjustment_delta=.1,
                       adoption_fee=fee, eta=.1, epsilon=.15, seed=seed)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sigma", type=float, choices=(.5, 1., 2.), required=True)
    parser.add_argument("--batch", type=int, choices=(0, 1), required=True)
    parser.add_argument("--scenario", choices=SCENARIOS, required=True)
    parser.add_argument("--out", default="results/game1_robustness")
    args = parser.parse_args()
    profiles = approved_profiles()[:10][args.batch * 5:(args.batch + 1) * 5]
    if len(profiles) != 5:
        raise AssertionError("Expected five fixed profiles")
    rows = []
    for f in profiles:
        for seed in SEEDS:
            result = run_game1(f, args.sigma, parameters(args.scenario, seed), rounds=200)
            if len(result["players"]) != 1800:
                raise AssertionError("Incomplete firm-round output")
            groups = defaultdict(list)
            for record in result["players"]:
                groups[record["strategy_id"]].append(record)
            winner = result["ranking"][0][0]
            for strategy, records in groups.items():
                rows.append(dict(profile_id=f.firm_id, sigma=args.sigma,
                                 scenario=args.scenario, seed=seed,
                                 strategy_id=strategy,
                                 cumulative_profit=records[-1]["cumulative_profit"],
                                 winner=int(strategy == winner),
                                 active_ai_share=sum(x["active_ai_count"] for x in records)/4000,
                                 shutdown_share=sum(x["action"] == "shutdown" for x in records)/200))
    path = Path(args.out)
    path.mkdir(parents=True, exist_ok=True)
    target = path / f"robust_sigma_{args.sigma:g}_batch_{args.batch}_{args.scenario}.csv"
    with target.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"COMPLETE {target}: {len(rows)} strategy-profile-seed outcomes")


if __name__ == "__main__":
    main()

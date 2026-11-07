"""Run and summarize a partition of the nine-strategy Game 1 full sample.

Outputs are scenario simulations, NOT research validation.
"""
import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from interfirm_abm.game1_nine_strategy import Game1Params, run_game1
from interfirm_abm.task_a6_market import approved_profiles


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sigma", type=float, required=True, choices=(0.5, 1.0, 2.0))
    parser.add_argument("--batch", type=int, required=True, choices=range(10))
    parser.add_argument("--out", default="results/game1_nine_strategy")
    args = parser.parse_args()
    profiles = approved_profiles()
    subset = profiles[args.batch * 10:(args.batch + 1) * 10]
    if len(subset) != 10:
        raise ValueError("expected ten profiles in batch")
    # Explicit illustrative scenario: P0=1 at Q0=9, elasticity=1;
    # factor prices from the legacy A6 reference convention.
    wage = 0.5 / 51.5
    p = Game1Params(demand_intercept=2.0, demand_slope=1.0 / 9.0,
                    wage=wage, rental=wage, adjustment_delta=0.1,
                    adoption_fee=0.1 * 0.5 / 20.0,
                    eta=0.1, epsilon=0.15, seed=11)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    summary = []
    for firm in subset:
        result = run_game1(firm, args.sigma, p, rounds=200)
        if len(result["players"]) != 9 * 200:
            raise AssertionError("missing firm-round observations")
        by_strategy = defaultdict(list)
        for record in result["players"]:
            by_strategy[record["strategy_id"]].append(record)
            rows.append(dict(profile_id=firm.firm_id, sigma=args.sigma, **record))
        winner = result["ranking"][0][0]
        for strategy, records in by_strategy.items():
            summary.append(dict(profile_id=firm.firm_id, sigma=args.sigma,
                                strategy_id=strategy,
                                cumulative_profit=records[-1]["cumulative_profit"],
                                mean_profit=sum(r["profit"] for r in records) / 200,
                                ai_ever_adopted_share=records[-1]["adopted_count"] / 20,
                                # Current engine does not emit active AI modes.
                                active_ai_share=sum(r["active_ai_count"] for r in records) / (200 * 20),
                                shutdown_share=sum(r["action"] == "shutdown" for r in records) / 200,
                                winner=int(strategy == winner)))
    def save(path, data):
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(data[0]))
            writer.writeheader()
            writer.writerows(data)
    prefix = f"sigma_{args.sigma:g}_batch_{args.batch:02d}"
    save(out / f"{prefix}_rounds.csv", rows)
    save(out / f"{prefix}_summary.csv", summary)
    with open(out / f"{prefix}_metadata.json", "w") as fh:
        json.dump(dict(sigma=args.sigma, batch=args.batch,
                       profiles=len(subset), strategies=9, rounds=200,
                       scenario="exploratory, uncalibrated", research_validated=False,
                       params=p.__dict__), fh, indent=2)
    print(f"COMPLETE {prefix}: {len(rows)} observations, {len(summary)} strategy-profile summaries")


if __name__ == "__main__":
    main()

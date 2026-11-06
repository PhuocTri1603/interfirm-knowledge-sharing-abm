"""Full A5 paired-sigma diagnostic experiment; never implies A6 validation.

One result at a time, retaining only configuration-level summaries.
"""
from __future__ import annotations
import csv
import json
import math
from pathlib import Path
from statistics import mean

from interfirm_abm.task_a5_diagnostic_runner import run_a5_diagnostic
from interfirm_abm.task_a5_normalized import SIGMA_SCENARIOS
from interfirm_abm.task_multi_action_diagnostic import configurations


def run_full_a5(output_dir="a5-full-diagnostic", rounds=200):
    if rounds != 200:
        raise ValueError("Canonical A5 requires exactly 200 rounds")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    rosters = configurations(100)
    rows = []
    counts = 0
    for idx, (config_id, roster) in enumerate(rosters.items(), 1):
        for sigma in SIGMA_SCENARIOS:
            result = run_a5_diagnostic(config_id, sigma, rounds=rounds, roster=roster)
            players = result["player_trajectory"]
            markets = result["market_trajectory"]
            ranking = result["ranking"]
            assert len(players) == 256 * rounds
            assert len(markets) == rounds and len(ranking) == 256
            assert all(math.isfinite(p["produced_quantity"]) and p["produced_quantity"] >= 0
                       for p in players)
            assert all(p["sold_quantity"] <= p["produced_quantity"] + 1e-9 for p in players)
            assert all(math.isclose(m["total_profit"], m["total_revenue"]-m["total_cost"],
                                    abs_tol=1e-7, rel_tol=1e-9) for m in markets)
            counts += len(players)
            rows.append({
                "config_id": config_id, "sigma": sigma, "winner_strategy": ranking[0]["player_id"],
                "winner_diagnostic_payoff": ranking[0]["total_benefit"],
                "mean_diagnostic_payoff": mean(x["total_benefit"] for x in ranking),
                "sum_produced_index": sum(m["quantity_produced"] for m in markets),
                "sum_sold_index": sum(m["quantity_sold"] for m in markets),
                "sum_diagnostic_revenue": sum(m["total_revenue"] for m in markets),
                "sum_diagnostic_cost": sum(m["total_cost"] for m in markets),
                "sum_diagnostic_profit": sum(m["total_profit"] for m in markets),
                "player_rounds": len(players),
            })
        if idx % 10 == 0:
            print(f"A5 completed {idx}/100 profiles, {counts:,} player-rounds", flush=True)
    assert len(rows) == 300 and counts == 15_360_000
    with (output / "scenario_summaries.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    by_config = {}
    for row in rows:
        by_config.setdefault(row["config_id"], {})[row["sigma"]] = row
    paired = []
    for config_id, d in by_config.items():
        assert set(d) == set(SIGMA_SCENARIOS)
        for a, b in ((0.5, 1.), (1., 2.), (0.5, 2.)):
            paired.append({
                "config_id": config_id, "sigma_low": a, "sigma_high": b,
                "same_winner": d[a]["winner_strategy"] == d[b]["winner_strategy"],
                "delta_sum_produced_index": d[b]["sum_produced_index"]-d[a]["sum_produced_index"],
                "delta_diagnostic_payoff": d[b]["sum_diagnostic_profit"]-d[a]["sum_diagnostic_profit"],
            })
    with (output / "paired_contrasts.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(paired[0]))
        writer.writeheader()
        writer.writerows(paired)
    manifest = {
        "research_validated": False,
        "economic_validation": "NOT_VALIDATED_A6_DIAGNOSTIC_ONLY",
        "configuration_count": 100, "sigma_scenarios": list(SIGMA_SCENARIOS),
        "strategy_players": 256, "rounds": rounds,
        "player_round_observations": counts,
        "paired_contrasts": len(paired),
        "market_convention": "legacy diagnostic: dimensionless CES index provisionally offered as quantity",
        "not_validated": ["A6 output-to-physical-quantity mapping",
                          "demand/price unit consistency", "welfare interpretation",
                          "calibration of costs and learning parameters"],
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2), flush=True)
    return manifest


if __name__ == "__main__":
    run_full_a5()

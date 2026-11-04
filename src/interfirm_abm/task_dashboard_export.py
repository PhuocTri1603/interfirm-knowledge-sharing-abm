"""Build a compact web dashboard dataset from the Game 1 shared-market scaffold.

Proxy-only: strategy labels are not executed as distinct economic policies.
"""
import json
from pathlib import Path
from interfirm_abm.task_shared_market_game import InitialConfiguration, player_ids, run_configuration, PROXY_STATUS


def build_dashboard(path: Path, count: int = 3) -> dict:
    if count <= 0:
        raise ValueError("count must be positive")
    configs = [InitialConfiguration(f"config_{i:03d}", demand_intercept=20 + 0.1 * i)
               for i in range(1, count + 1)]
    players = player_ids()
    output = {"status": PROXY_STATUS, "rounds": 200, "players": len(players),
              "warning": "Illustrative proxy only. Rankings do not measure strategy superiority.",
              "configurations": []}
    for config in configs:
        panel, ranking = run_configuration(config, selected_players=players)
        by_round = []
        # The fixed-output illustrative market has a constant price across rounds.
        for t in (1, 25, 50, 75, 100, 125, 150, 175, 200):
            row = panel[t - 1]
            by_round.append({"round": t, "price": row["market_price"],
                             "market_quantity": row["market_quantity"]})
        output["configurations"].append({
            "id": config.config_id,
            "price_trajectory": by_round,
            "top_10": ranking[:10],
            "total_market_benefit": round(sum(x["total_benefit"] for x in ranking), 4),
            "note": "No adaptive behavior; prices are constant across rounds in this proxy."
        })
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return output


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("site/data.json"))
    parser.add_argument("--configurations", type=int, default=3)
    args = parser.parse_args()
    result = build_dashboard(args.output, args.configurations)
    print(f"Wrote {args.output}: {result['players']} players, {len(result['configurations'])} configurations")

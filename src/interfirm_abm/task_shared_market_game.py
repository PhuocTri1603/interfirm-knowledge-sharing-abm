"""Game 1 shared-market *scaffold*, not an economically validated strategy tournament.

L3-L6 combinations identify 256 players. L7 is a market-design label, not
an additional player decision. Unsupported strategy mechanisms are explicitly
marked proxy_only; do not interpret rankings as research findings.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from interfirm_abm.task_experiment_dimensions import strategy_player_ids

ROUNDS = 200
PROXY_STATUS = "proxy_only_not_economic_strategy_execution"


def player_ids() -> tuple[str, ...]:
    return strategy_player_ids()


def stable_fraction(label: str) -> float:
    return int.from_bytes(hashlib.sha256(label.encode()).digest()[:8], "big") / 2**64


@dataclass(frozen=True)
class InitialConfiguration:
    config_id: str
    demand_intercept: float = 20.0
    demand_slope: float = 0.001
    unit_cost_base: float = 5.0
    capacity: float = 1.0

    def validate(self) -> None:
        if not self.config_id or self.demand_intercept <= 0 or self.demand_slope <= 0:
            raise ValueError("invalid initial configuration")
        if self.unit_cost_base <= 0 or self.capacity <= 0:
            raise ValueError("cost and capacity must be positive")


def run_configuration(config: InitialConfiguration, rounds: int = ROUNDS,
                      selected_players: tuple[str, ...] | None = None) -> tuple[list[dict], list[dict]]:
    """Provisional shared inverse-demand accounting with *identical* player policy.

    Each player supplies fixed capacity every round; L3-L6 strategy choices are
    IDs only, NOT implemented decisions. Heterogeneous proxy unit costs are
    deterministic bookkeeping fixtures; they do not represent CES/Leontief/etc.
    """
    config.validate()
    if rounds <= 0:
        raise ValueError("rounds must be positive")
    players = player_ids() if selected_players is None else selected_players
    if not players or len(players) != len(set(players)):
        raise ValueError("player roster must be nonempty and unique")
    known = set(player_ids())
    if not set(players) <= known:
        raise ValueError("unknown strategy player")
    total_output = config.capacity * len(players)
    price = max(0.0, config.demand_intercept - config.demand_slope * total_output)
    panel, ranking = [], []
    for player in players:
        # This variation is explicitly a fixture, NOT a modeled strategy effect.
        cost = config.unit_cost_base * (0.9 + 0.2 * stable_fraction(player))
        payoff = (price - cost) * config.capacity
        ranking.append({"config_id": config.config_id, "player_id": player,
                        "total_benefit": round(payoff * rounds, 8),
                        "execution_status": PROXY_STATUS})
        for t in range(1, rounds + 1):
            panel.append({"config_id": config.config_id, "round": t,
                          "player_id": player, "quantity": config.capacity,
                          "market_quantity": total_output, "market_price": price,
                          "unit_cost": round(cost, 8), "round_payoff": round(payoff, 8),
                          "execution_status": PROXY_STATUS})
    ranking.sort(key=lambda r: (-r["total_benefit"], r["player_id"]))
    for rank, row in enumerate(ranking, 1):
        row["rank"] = rank
    return panel, ranking


def run_sequential(configurations: tuple[InitialConfiguration, ...],
                   rounds: int = ROUNDS,
                   selected_players: tuple[str, ...] | None = None) -> tuple[list[dict], list[dict]]:
    if not configurations or len({c.config_id for c in configurations}) != len(configurations):
        raise ValueError("configurations must be nonempty with unique IDs")
    all_panel, all_ranking = [], []
    for config in configurations:
        panel, ranking = run_configuration(config, rounds, selected_players)
        all_panel.extend(panel)
        all_ranking.extend(ranking)
    return all_panel, all_ranking


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run illustrative 200-round shared-market scaffold")
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/game1_shared_market"))
    parser.add_argument("--configurations", type=int, default=1)
    parser.add_argument("--rounds", type=int, default=ROUNDS)
    args = parser.parse_args()
    if args.configurations <= 0:
        parser.error("--configurations must be positive")
    configs = tuple(InitialConfiguration(f"config_{i:03d}", demand_intercept=20 + i * 0.1)
                    for i in range(1, args.configurations + 1))
    panel, ranking = run_sequential(configs, args.rounds)
    write_csv(args.output_dir / "rounds.csv", panel)
    write_csv(args.output_dir / "ranking.csv", ranking)
    print(json.dumps({"configurations":len(configs), "rounds_per_configuration":args.rounds,
                      "players_per_market":len(player_ids()), "round_records":len(panel),
                      "execution_status":PROXY_STATUS,
                      "winner_first_configuration":ranking[0]["player_id"],
                      "output_dir":str(args.output_dir)}, indent=2))


if __name__ == "__main__":
    main()

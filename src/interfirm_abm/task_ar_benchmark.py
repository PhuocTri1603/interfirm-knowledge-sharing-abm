"""Executable, explicitly illustrative Acemoglu–Restrepo-style task assignment game.

Benchmark: each task is performed by labor, or by the cheaper eligible
capital method. Capital K is not AI: automation expands eligible tasks.
All prices, capacities and productivity values are scenario assumptions,
not estimates or a full general-equilibrium implementation.
"""
from dataclasses import dataclass
from csv import DictWriter
from pathlib import Path
import argparse
import json
import random

@dataclass(frozen=True)
class Parameters:
    firms: int = 100
    tasks: int = 20
    wage: float = 1.0
    rental_rate: float = 0.7
    output_price: float = 1.5
    target_output: float = 20.0
    initial_eligible_share: float = 0.2
    post_eligible_share: float = 0.6
    seed: int = 2026


def validate(p: Parameters) -> None:
    if p.firms <= 0 or p.tasks <= 0 or p.target_output <= 0:
        raise ValueError("firms, tasks and target_output must be positive")
    if min(p.wage, p.rental_rate, p.output_price) <= 0:
        raise ValueError("factor and output prices must be positive")
    if not 0 <= p.initial_eligible_share <= p.post_eligible_share <= 1:
        raise ValueError("eligible shares must be ordered within [0, 1]")


def run_game(p: Parameters = Parameters()) -> list[dict]:
    """Matched firms and task productivities across pre/post states.

    A fixed-recipe 20-task final-output requirement is used ONLY as a
    transparent benchmark closure, not as a claim that AR requires it.
    No endogenous output, demand, capacity, adjustment or adoption costs.
    """
    validate(p)
    rng = random.Random(p.seed)
    records = []
    before = round(p.tasks * p.initial_eligible_share)
    after = round(p.tasks * p.post_eligible_share)
    task_requirement = p.target_output / p.tasks
    for firm in range(p.firms):
        labor_eff = [rng.uniform(0.8, 1.2) for _ in range(p.tasks)]
        capital_eff = [rng.uniform(0.8, 1.6) for _ in range(p.tasks)]
        # Same firm-specific eligibility ordering in both periods.
        order = list(range(p.tasks))
        rng.shuffle(order)
        for phase, count in (("pre", before), ("post", after)):
            eligible = set(order[:count])
            labor, capital, automated = 0.0, 0.0, 0
            for j in range(p.tasks):
                labor_units = task_requirement / labor_eff[j]
                capital_units = task_requirement / capital_eff[j]
                use_capital = j in eligible and p.rental_rate * capital_units < p.wage * labor_units
                if use_capital:
                    capital += capital_units
                    automated += 1
                else:
                    labor += labor_units
            cost = p.wage * labor + p.rental_rate * capital
            records.append({
                "firm_id": f"F{firm + 1:03d}",
                "phase": phase,
                "eligible_tasks": count,
                "automated_tasks": automated,
                "labor": round(labor, 8),
                "capital": round(capital, 8),
                "output": p.target_output,
                "cost": round(cost, 8),
                "revenue": round(p.output_price * p.target_output, 8),
                "profit": round(p.output_price * p.target_output - cost, 8),
            })
    return records


def summarize(records: list[dict]) -> dict:
    return {
        phase: {
            key: round(sum(row[key] for row in records if row["phase"] == phase), 6)
            for key in ("output", "labor", "capital", "cost", "revenue", "profit", "automated_tasks")
        }
        for phase in ("pre", "post")
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run illustrative 100-firm task-based automation game")
    parser.add_argument("--output", type=Path, default=Path("artifacts/game1_task_benchmark.csv"))
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()
    params = Parameters(seed=args.seed)
    rows = run_game(params)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as file:
        writer = DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"assumptions":vars(params), "totals":summarize(rows),
                      "csv":str(args.output)}, indent=2))


if __name__ == "__main__":
    main()

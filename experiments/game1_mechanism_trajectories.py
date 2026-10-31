"""Game 1 follow-up: inspect full matched learning trajectories."""

import argparse
import json
from pathlib import Path

import pandas as pd

from interfirm_abm.simulation import Simulation


def run_experiment():
    frames = []
    for seed in range(2026, 2126):
        for policy in ("random", "guided"):
            sim = Simulation(
                n_firms=20,
                n_rounds=50,
                seed=seed,
                learning_policy=policy,
                matched_randomness=True,
            )
            frame = sim.run()
            frame["seed"] = seed
            frame["policy"] = policy
            frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def export_results(history, output_dir):
    folder = Path(output_dir)
    folder.mkdir(parents=True, exist_ok=True)
    history.to_csv(folder / "firm_round_trajectories.csv", index=False)
    summary = history.groupby(
        ["policy", "technology", "round"], as_index=False
    ).agg(
        mean_output=("current_output", "mean"),
        mean_capital_share=("capital_share", "mean"),
        acceptance_rate=("accepted", "mean"),
    )
    summary.to_csv(folder / "mechanism_by_technology_round.csv", index=False)

    paired = history.pivot(
        index=["seed", "round", "firm_id", "technology"],
        columns="policy",
        values=["current_output", "capital_share"],
    )
    paired.columns = [
        f"{metric}_{policy}" for metric, policy in paired.columns
    ]
    paired = paired.reset_index()
    paired["advantage_pct"] = (
        100 * (paired["current_output_guided"] - paired["current_output_random"])
        / paired["current_output_random"]
    )
    paired.to_csv(folder / "paired_firm_round.csv", index=False)

    metadata = {
        "experiment": "game1_mechanism_trajectories",
        "source": "follow-up to Validation 05",
        "seed_start": 2026,
        "seed_end_inclusive": 2125,
        "n_firms": 20,
        "n_rounds": 50,
        "policies": ["random", "guided"],
        "matched_randomness": True,
        "expected_history_rows": 200000,
        "observed_history_rows": len(history),
        "expected_paired_rows": 100000,
        "observed_paired_rows": len(paired),
    }
    (folder / "metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    return paired


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--export-dir", type=Path, required=True)
    args = parser.parse_args()
    history = run_experiment()
    paired = export_results(history, args.export_dir)
    assert len(history) == 200000
    assert len(paired) == 100000
    print("History rows:", len(history), "Paired rows:", len(paired))

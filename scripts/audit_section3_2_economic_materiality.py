"""Economic materiality audit of existing seed-11 archive/replay data.

Descriptive only: no new simulation, no tolerance relaxation, no automatic
economic-equivalence PASS. Historical strict failure remains authoritative.
"""
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--replays", required=True)
p.add_argument("--archive", required=True)
p.add_argument("--out", required=True)
a = p.parse_args()
out = Path(a.out)
out.mkdir(parents=True, exist_ok=True)

def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))

replay_files = sorted(Path(a.replays).rglob("seed11_original_solver_rounds.csv"))
assert len(replay_files) == 10, f"Expected 10 seed11 trace files, got {len(replay_files)}"
archive_files = [Path(a.archive) / f"sigma_{s}_batch_{b:02d}_rounds.csv"
                 for s in (1, 2) for b in range(10)]
assert all(f.is_file() for f in archive_files)

def index(files):
    data = {}
    for f in files:
        for row in read_csv(f):
            key = (row["profile_id"], float(row["sigma"]), int(row["round"]), row["strategy_id"])
            assert key not in data, f"Duplicate key {key}"
            data[key] = row
    return data

archive = index(archive_files)
replay = index(replay_files)
assert len(archive) == len(replay) == 360000
assert set(archive) == set(replay)
final = defaultdict(lambda: {"archive": {}, "replay": {}})
actions = defaultdict(int)
for key, old in archive.items():
    new = replay[key]
    group = key[:2]
    if old["action"] != new["action"]:
        actions[group] += 1
    if key[2] == 200:
        for name, record in (("archive", old), ("replay", new)):
            final[group][name][key[3]] = float(record["cumulative_profit"])

assert len(final) == 200
rows = []
for group, values in sorted(final.items()):
    original, current = values["archive"], values["replay"]
    assert set(original) == set(current) and len(original) == 9
    ids = sorted(original)
    order_old = sorted(ids, key=lambda s: (-original[s], s))
    order_new = sorted(ids, key=lambda s: (-current[s], s))
    winner_old, winner_new = order_old[0], order_new[0]
    gap_old = original[order_old[0]] - original[order_old[1]]
    gap_new = current[order_new[0]] - current[order_new[1]]
    max_delta = max(abs(original[s] - current[s]) for s in ids)
    pair_flips = sum(
        (original[x] - original[y]) * (current[x] - current[y]) < 0
        for i, x in enumerate(ids) for y in ids[i+1:]
    )
    rows.append(dict(
        profile=group[0], sigma=group[1], winner_archive=winner_old,
        winner_replay=winner_new, winner_changed=int(winner_old != winner_new),
        full_ranking_changed=int(order_old != order_new),
        pairwise_ranking_reversals=pair_flips,
        winner_margin_archive=gap_old, winner_margin_replay=gap_new,
        max_abs_terminal_cumulative_profit_delta=max_delta,
        terminal_delta_over_archive_winner_margin=(
            max_delta / gap_old if gap_old > 0 else None),
        action_mismatches=actions[group],
    ))

with (out / "economic_equivalence_profile_sigma.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

report = {
    "status": "ECONOMIC_MATERIALITY_DESCRIPTIVE_ONLY",
    "historical_strict_equivalence": "STRICT_FAIL",
    "economic_equivalence_established": False,
    "research_validated": False,
    "engine_modified": False,
    "new_simulations": 0,
    "archive_rows_compared": len(archive),
    "profile_sigma_groups": len(rows),
    "winner_changes": sum(r["winner_changed"] for r in rows),
    "full_ranking_changes": sum(r["full_ranking_changed"] for r in rows),
    "pairwise_ranking_reversals": sum(r["pairwise_ranking_reversals"] for r in rows),
    "groups_with_pairwise_reversals": sum(r["pairwise_ranking_reversals"] > 0 for r in rows),
    "groups_with_action_mismatches": sum(r["action_mismatches"] > 0 for r in rows),
    "total_action_mismatches": sum(r["action_mismatches"] for r in rows),
    "max_terminal_profit_delta": max(r["max_abs_terminal_cumulative_profit_delta"] for r in rows),
    "max_delta_over_winner_margin": max(
        (r["terminal_delta_over_archive_winner_margin"] for r in rows
         if r["terminal_delta_over_archive_winner_margin"] is not None), default=None),
    "interpretation": (
        "Unchanged winner alone is insufficient to establish economic equivalence. "
        "Review full-ranking reversals, action changes, and cumulative-profit "
        "differences relative to winner margins. No thresholds were introduced."
    ),
}
(out / "economic_equivalence_materiality.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))

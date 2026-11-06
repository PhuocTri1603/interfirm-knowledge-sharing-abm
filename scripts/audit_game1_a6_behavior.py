"""Behavioral differentiation audit of the illustrative A6 pilot (no calibration)."""
import csv
import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from statistics import mean

ROOT = Path("artifacts/game1_a6_pilot")
with (ROOT / "players.csv").open(newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
assert len(rows) == 51200
by_id = defaultdict(list)
for row in rows:
    by_id[row["strategy_id"]].append(row)
assert len(by_id) == 256
for data in by_id.values():
    data.sort(key=lambda r: int(r["round"]))
    assert len(data) == 200

def layers(sid):
    return dict(piece.split("=", 1) for piece in sid.split("|"))

def action_path(data):
    return tuple(r["action"] for r in data)

def numeric_path(data, field):
    return tuple(float(r[field]) for r in data)

def path_equal(a, b, fields=("action", "quantity", "cost", "profit"), tol=1e-10):
    for x, y in zip(a, b):
        for field in fields:
            if field == "action":
                if x[field] != y[field]:
                    return False
            elif abs(float(x[field]) - float(y[field])) > tol:
                return False
    return True

ids = sorted(by_id)
paths = {sid: action_path(by_id[sid]) for sid in ids}
action_classes = defaultdict(list)
for sid in ids:
    action_classes[paths[sid]].append(sid)
transition_counts = {sid: sum(a != b for a, b in zip(paths[sid], paths[sid][1:])) for sid in ids}
action_distinct = {sid: len(set(paths[sid])) for sid in ids}

# Matched comparisons hold the other three layers fixed. This is descriptive
# within a jointly interacting market, not an independent treatment effect.
matched = {}
for layer in ("L3", "L4", "L5", "L6"):
    groups = defaultdict(list)
    for sid in ids:
        key = tuple((k, v) for k, v in layers(sid).items() if k != layer)
        groups[key].append(sid)
    pairs = [pair for members in groups.values() for pair in combinations(sorted(members), 2)]
    assert len(pairs) == 6 * 64
    action_same = sum(paths[a] == paths[b] for a, b in pairs)
    outcomes_same = sum(path_equal(by_id[a], by_id[b]) for a, b in pairs)
    mean_difference = mean(abs(float(by_id[a][-1]["cumulative_profit"]) -
                               float(by_id[b][-1]["cumulative_profit"])) for a, b in pairs)
    matched[layer] = {
        "pairs": len(pairs),
        "identical_action_paths": action_same,
        "identical_action_path_fraction": action_same / len(pairs),
        "identical_full_outcome_paths": outcomes_same,
        "identical_full_outcome_fraction": outcomes_same / len(pairs),
        "mean_absolute_cumulative_profit_difference": mean_difference,
    }

by_l6 = {}
for l6 in sorted({layers(s)["L6"] for s in ids}):
    members = [sid for sid in ids if layers(sid)["L6"] == l6]
    by_l6[l6] = {
        "players": len(members),
        "mean_action_transitions": mean(transition_counts[s] for s in members),
        "mean_distinct_actions": mean(action_distinct[s] for s in members),
        "action_counts": dict(Counter(a for s in members for a in paths[s])),
    }

# Each strategy's action path is observable, but the CSV does not contain
# task-level allocations or internal L5 beliefs. Do not claim these are tested.
report = {
    "experiment": "Game1_A6_behavioral_differentiation_audit",
    "research_validated": False,
    "observation_count": len(rows),
    "strategies": len(ids),
    "distinct_action_paths": len(action_classes),
    "largest_identical_action_path_group": max(map(len, action_classes.values())),
    "players_using_one_action_all_200_rounds": sum(x == 1 for x in action_distinct.values()),
    "players_with_at_least_one_action_transition": sum(x > 0 for x in transition_counts.values()),
    "mean_action_transitions_per_player": mean(transition_counts.values()),
    "matched_layer_comparisons": matched,
    "learning_layer_L6": by_l6,
    "examples_of_identical_paths": [v[:8] for v in sorted(action_classes.values(), key=len, reverse=True)[:3]],
    "audit_limitations": [
        "Identical action IDs can conceal different task-level K/L allocations.",
        "Identical action paths do not imply identical quantity, cost or profit.",
        "No internal beliefs, task allocations or counterfactual market trajectories in current pilot CSV.",
        "Single configuration and seed with illustrative parameters; no scientific ranking inference.",
    ],
}
(ROOT / "behavior_audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print("A6_BEHAVIOR_AUDIT=" + json.dumps(report, sort_keys=True))

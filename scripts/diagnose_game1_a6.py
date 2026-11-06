"""Small, explicitly illustrative A6 robustness diagnostic. No model changes."""
import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from statistics import mean
from interfirm_abm.task_a6_market import A6Parameters, approved_profiles, run_a6_market
from interfirm_abm.task_l34_economics import L34Parameters

out = Path("artifacts/game1_a6_diagnostics")
out.mkdir(parents=True, exist_ok=True)
profiles = approved_profiles()
l34 = L34Parameters(2.0, .001, .2, .001)
runs = []
for profile in profiles[:3]:
    for seed in (11, 29):
        a6 = A6Parameters(10., .01, .15, 1., .5, seed, .001, .001)
        r = run_a6_market(profile, 1.0, a6, l34_parameters=l34, rounds=200)
        grouped = defaultdict(list)
        for row in r["players"]:
            grouped[row["strategy_id"]].append(row)
        paths = {s: tuple(x["action"] for x in rows) for s, rows in grouped.items()}
        def layer(s, k):
            return dict(p.split("=", 1) for p in s.split("|"))[k]
        im = [s for s in paths if layer(s, "L6") == "imitation"]
        fixed_im = sum(len(set(paths[s])) == 1 for s in im)
        groups = defaultdict(list)
        for s in paths:
            key = tuple(p for p in s.split("|") if not p.startswith("L5="))
            groups[key].append(s)
        l5pairs = [p for v in groups.values() for p in combinations(sorted(v), 2)]
        same_l5 = sum(paths[a] == paths[b] for a,b in l5pairs)
        full_same_l5 = sum(all(
            x["action"] == y["action"] and
            all(abs(float(x[k])-float(y[k])) < 1e-9 for k in ("quantity","cost","profit"))
            for x,y in zip(grouped[a],grouped[b])) for a,b in l5pairs)
        ranking = dict(r["ranking"])
        runs.append({
            "profile_id":profile.firm_id,"seed":seed,"strategies":len(paths),
            "distinct_action_paths":len(set(paths.values())),
            "imitation_fixed_players":fixed_im,"imitation_players":len(im),
            "l5_identical_action_pairs":same_l5,"l5_identical_outcome_pairs":full_same_l5,
            "l5_matched_pairs":len(l5pairs),
            "profit_range":[min(ranking.values()),max(ranking.values())],
            "top_strategy":r["ranking"][0][0],
            "shutdown_rate":sum(x["action"]=="shutdown" for x in r["players"])/len(r["players"]),
        })
        print("A6_DIAGNOSTIC_RUN="+json.dumps(runs[-1],sort_keys=True),flush=True)
by_profile=defaultdict(dict)
for r in runs:
    by_profile[r["profile_id"]][r["seed"]]=r
report={
    "research_validated":False,
    "purpose":"diagnostic only; illustrative parameters, not researcher-approved calibration",
    "runs":runs,
    "imitation_fixation_all_runs":all(r["imitation_fixed_players"]==64 for r in runs),
    "distinct_action_path_range":[min(r["distinct_action_paths"] for r in runs),max(r["distinct_action_paths"] for r in runs)],
    "l5_identical_outcome_pair_range":[min(r["l5_identical_outcome_pairs"] for r in runs),max(r["l5_identical_outcome_pairs"] for r in runs)],
    "limitations":["L5 forecast score order is not logged; inspect formula in task_a6_market.py for mechanism.","Shared-market paired comparisons are descriptive, not causal.","Only 3 configurations and 2 seeds; not full robustness validation."]
}
(out/"diagnostics.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print("A6_DIAGNOSTICS_SUMMARY="+json.dumps(report,sort_keys=True),flush=True)

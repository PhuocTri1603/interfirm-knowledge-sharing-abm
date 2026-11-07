"""A6 pre-registered diagnostic robustness: 12 spaced profiles x 3 sigmas x 3 seeds.

All 256 strategies share the same market in each run. This is a diagnostic
robustness screen, NOT a full 100-profile scientific validation.
"""
import csv
import json
from collections import defaultdict
from math import isclose
from pathlib import Path
from statistics import mean

from interfirm_abm.task_a6_market import (
    approved_d1_d2_parameters, approved_profiles, run_a6_market,
)
from interfirm_abm.task_l34_economics import L34Parameters

OUT=Path("artifacts/game1_a6_robustness")
OUT.mkdir(parents=True,exist_ok=True)
profiles=approved_profiles()
assert len(profiles)==100
# Spread across the full preapproved configuration registry.
indices=(0,9,18,27,36,45,54,63,72,81,90,99)
sigmas=(0.5,1.0,2.0)
seeds=(11,23,47)
l34=L34Parameters(capacity_ratio=2.0,adjustment_unit_cost=.001,
                  efficiency_gain=.2,adoption_fee=.001)
rows=[]
run_summaries=[]
for index in indices:
    firm=profiles[index]
    for sigma in sigmas:
        for seed in seeds:
            params=approved_d1_d2_parameters(theta=1,kappa=.5,elasticity=1,
                                              adaptive_lambda=.5,seed=seed)
            result=run_a6_market(firm,sigma,params,l34_parameters=l34,rounds=200)
            assert result["research_validated"] is False
            assert len(result["players"])==51200
            paths=defaultdict(list)
            for record in result["players"]:
                paths[record["strategy_id"]].append(record)
            assert len(paths)==256 and all(len(v)==200 for v in paths.values())
            group={}
            for sid,path in paths.items():
                attrs=dict(part.split("=",1) for part in sid.split("|"))
                group[sid]=(attrs,path)
            for layer,method_a,method_b in (
                ("L6","imitation","optimization"),
                ("L6","imitation","softmax"),
                ("L5","competitive","cournot"),
                ("L5","adaptive","competitive"),
            ):
                fixed=defaultdict(dict)
                for sid,(attrs,path) in group.items():
                    key=tuple(sorted((k,v) for k,v in attrs.items() if k!=layer))
                    fixed[key][attrs[layer]]=path
                assert len(fixed)==64
                for key,options in fixed.items():
                    a,b=options[method_a],options[method_b]
                    action_same=all(x["action"]==y["action"] for x,y in zip(a,b))
                    quantity_same=all(isclose(x["quantity"],y["quantity"],rel_tol=1e-10,abs_tol=1e-10) for x,y in zip(a,b))
                    rows.append(dict(profile_id=firm.firm_id,sigma=sigma,seed=seed,
                        layer=layer,method_a=method_a,method_b=method_b,
                        fixed_layers="|".join(f"{k}={v}" for k,v in key),
                        identical_actions=int(action_same),
                        identical_quantities=int(quantity_same),
                        payoff_a=a[-1]["cumulative_profit"],
                        payoff_b=b[-1]["cumulative_profit"],
                        payoff_difference=a[-1]["cumulative_profit"]-b[-1]["cumulative_profit"],
                        transitions_a=sum(x["action"]!=y["action"] for x,y in zip(a,a[1:])),
                        transitions_b=sum(x["action"]!=y["action"] for x,y in zip(b,b[1:]))))
            run_summaries.append(dict(profile_id=firm.firm_id,sigma=sigma,seed=seed,
                total_market_profit=sum(m["profit"] for m in result["market"])))
            print("A6_ROBUSTNESS_PROGRESS="+json.dumps(dict(completed=len(run_summaries),
                total=len(indices)*len(sigmas)*len(seeds),profile=firm.firm_id,
                sigma=sigma,seed=seed)),flush=True)
assert len(run_summaries)==108 and len(rows)==108*64*4
fields=list(rows[0])
with (OUT/"paired_comparisons.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
with (OUT/"market_runs.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(run_summaries[0]));w.writeheader();w.writerows(run_summaries)
summary=[]
for (sigma,seed,layer,a,b),subset in sorted(
    ((key,[r for r in rows if (r["sigma"],r["seed"],r["layer"],r["method_a"],r["method_b"])==key])
     for key in set((r["sigma"],r["seed"],r["layer"],r["method_a"],r["method_b"]) for r in rows)),
    key=lambda pair:pair[0]):
    summary.append(dict(sigma=sigma,seed=seed,layer=layer,method_a=a,method_b=b,
        pairs=len(subset),identical_action_fraction=mean(r["identical_actions"] for r in subset),
        mean_payoff_difference=mean(r["payoff_difference"] for r in subset),
        mean_absolute_payoff_difference=mean(abs(r["payoff_difference"]) for r in subset)))
with (OUT/"summary_by_sigma_seed.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
report=dict(research_validated=False,experiment="A6_12profile_3sigma_3seed",
    configurations=12,scenarios=108,observations=108*51200,
    fixed_approved_d1_d2_d3=True,l34_l6_illustrative=True,
    warning="Descriptive paired differences in one jointly endogenous market; not causal estimates",
    summary=summary)
(OUT/"summary.json").write_text(json.dumps(report,indent=2))
print("A6_ROBUSTNESS_DONE="+json.dumps(dict(scenarios=108,comparisons=len(rows),
    summary_rows=len(summary),research_validated=False)),flush=True)

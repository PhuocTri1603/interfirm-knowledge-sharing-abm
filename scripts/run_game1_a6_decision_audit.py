"""Observational A6 decision-level audit; no changes to decisions or random draws."""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

from interfirm_abm.task_a6_market import (
    approved_profiles, approved_d1_d2_parameters, run_a6_market,
    l5_candidate_forecast, l5_candidate_score,
)
from interfirm_abm.task_l34_economics import L34Parameters

OUT=Path("artifacts/game1_a6_decision_audit")
OUT.mkdir(parents=True,exist_ok=True)
profiles=approved_profiles()
selected=tuple(profiles)
assert len(selected)==100 and len({f.firm_id for f in selected})==100
l34=L34Parameters(capacity_ratio=2.,adjustment_unit_cost=.001,
                  efficiency_gain=.2,adoption_fee=.001)
params=approved_d1_d2_parameters(theta=1.,kappa=.5,elasticity=1.,
                                  adaptive_lambda=.5,seed=11)
counts=defaultdict(Counter)
rows=[]
for firm in selected:
    def audit(d):
        key=(firm.firm_id,d["L5"],d["L6"])
        c=counts[key]
        c["decisions"]+=1
        if d["chosen"]=="shutdown":
            c["shutdown"]+=1
            return
        c["production"]+=1
        if d["L6"]=="imitation":
            if d["history_best"] is None:
                c["imitation_fallback"]+=1
            else:
                c["imitation_has_history"]+=1
                if d["history_best"]==d["preferred"]:
                    c["imitation_history_agrees_optimization"]+=1
                else:
                    c["imitation_history_disagrees_optimization"]+=1
            if d["chosen"]==d["preferred"]:
                c["imitation_chosen_equals_optimization"]+=1
        if d["L6"]=="softmax":
            if d["chosen"]!=d["preferred"]:
                c["softmax_explored_nonpreferred"]+=1
        if d["L5"] in ("competitive","cournot"):
            prices={}
            scores={}
            for method in ("competitive","cournot"):
                scores[method]={}
                for a in d["candidates"]:
                    if not a["eligible"]:
                        continue
                    q=a["quantity"]
                    cost=a["forecast_price"]*q-a["predicted_profit"]
                    forecast=l5_candidate_forecast(method,d["prior_price"],
                        d["last_quantity"],q,d["demand_slope"])
                    scores[method][a["action"]]=l5_candidate_score(method,forecast,q,cost)
            if scores["competitive"] and scores["cournot"]:
                def winner(sc):
                    return sorted(sc,key=lambda x:(sc[x],tuple(-ord(z) for z in x)),reverse=True)[0]
                # Same deterministic tie-break as the A6 engine: action-id ascending.
                def preferred(sc):
                    ordered=sorted(sc)
                    ordered.sort(key=lambda k:sc[k],reverse=True)
                    return ordered[0]
                pc=preferred(scores["competitive"])
                pq=preferred(scores["cournot"])
                c["competitive_cournot_same_rank1"]+=int(pc==pq)
                c["competitive_cournot_different_rank1"]+=int(pc!=pq)
                c["multiple_eligible"]+=int(len(scores["competitive"])>1)
                c["single_eligible"]+=int(len(scores["competitive"])==1)
                c["forecast_price_shift_nonzero"]+=int(any(
                    abs(l5_candidate_forecast("cournot",d["prior_price"],
                        d["last_quantity"],a["quantity"],d["demand_slope"])-d["prior_price"])>1e-12
                    for a in d["candidates"] if a["eligible"]))
    result=run_a6_market(firm,1.,params,l34_parameters=l34,rounds=200,decision_audit=audit)
    assert not result["research_validated"] and len(result["players"])==51200
    print("A6_DECISION_AUDIT_PROGRESS="+json.dumps({"completed":len({k[0] for k in counts}),"total":len(selected),"profile":firm.firm_id}),flush=True)
for (profile,l5,l6),c in sorted(counts.items()):
    rows.append({"profile_id":profile,"L5":l5,"L6":l6,**c})
fields=["profile_id","L5","L6"]+sorted(set(k for c in counts.values() for k in c))
with (OUT/"decision_mechanism_counts.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
summary={}
for l5,l6 in sorted({(r["L5"],r["L6"]) for r in rows}):
    subset=[r for r in rows if r["L5"]==l5 and r["L6"]==l6]
    total=Counter()
    for r in subset:
        for k in fields[3:]:
            total[k]+=r.get(k,0)
    summary[f"{l5}|{l6}"]=dict(total)
report=dict(research_validated=False,profiles=[x.firm_id for x in selected],
            sigma=1.,seed=11,decisions=len(selected)*256*200,
            interpretation="within-decision alternative ranking, observational not causal",
            by_mechanism=summary)
(OUT/"summary.json").write_text(json.dumps(report,indent=2))
print("A6_DECISION_AUDIT_SUMMARY="+json.dumps(report,sort_keys=True),flush=True)

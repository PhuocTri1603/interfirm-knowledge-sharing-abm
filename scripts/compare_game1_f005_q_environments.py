"""Compare F005 seed47 Q-values across independent numerical-thread environments.

This is a cross-environment sensitivity experiment, not recovery of unrecorded
historical Q-values. The original historical CSVs do not contain Q-values.
"""
import csv, glob, os
from pathlib import Path

root=Path("results/game1_f005_environment_compare")
a,b=(root/"threads1"/"F005_sigma2_seed47_fee1_q_margins.csv",
     root/"threads4"/"F005_sigma2_seed47_fee1_q_margins.csv")
def read(path):
    with path.open(newline="") as f:
        return {(int(r["round"]),r["strategy_id"]):r for r in csv.DictReader(f)}
x,y=read(a),read(b)
assert len(x)==len(y)==1800 and x.keys()==y.keys()
rows=[]
for key in sorted(x):
    l,r=x[key],y[key]
    gaps={name:float(r[name])-float(l[name]) for name in
          ("q_b2","q_b3","q_b4","b2_b3_gap","b3_b4_gap","greedy_margin")}
    rows.append(dict(round=key[0],strategy_id=key[1],
        action_threads1=l["action"],action_threads4=r["action"],
        greedy_threads1=l["greedy_action"],greedy_threads4=r["greedy_action"],
        exploratory_threads1=l["exploratory"],exploratory_threads4=r["exploratory"],
        action_changed=int(l["action"]!=r["action"]),
        exploration_changed=int(l["exploratory"]!=r["exploratory"]),
        **{"delta_"+name:value for name,value in gaps.items()},
        q_b3_b4_threads1=l["b3_b4_gap"],q_b3_b4_threads4=r["b3_b4_gap"]))
out=root/"environment_q_comparison.csv"
with out.open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
focal=[r for r in rows if r["strategy_id"]=="L3=productivity|L4=cost_based"]
print("all_strategy_action_differences",sum(r["action_changed"] for r in rows))
print("all_strategy_exploration_flag_differences",sum(r["exploration_changed"] for r in rows))
print("focal_action_differences",[(r["round"],r["action_threads1"],r["action_threads4"]) for r in focal if r["action_changed"]])
print("focal_max_abs_delta_q",max(abs(r["delta_"+k]) for r in focal for k in ("q_b2","q_b3","q_b4")))
print("focal_rounds_90_110")
for r in focal:
    if 90<=r["round"]<=110:
        print(r["round"],r["action_threads1"],r["action_threads4"],
              "epsilon",r["exploratory_threads1"],r["exploratory_threads4"],
              "gap1",r["q_b3_b4_threads1"],"gap4",r["q_b3_b4_threads4"])
print("REPORT",out)

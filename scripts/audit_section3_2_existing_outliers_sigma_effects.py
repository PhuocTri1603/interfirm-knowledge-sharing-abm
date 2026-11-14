"""Artifact-only audit: action differences, pointwise outliers and sigma 2 minus sigma 1 effects."""
import argparse,csv,json,heapq
from pathlib import Path
from collections import defaultdict
p=argparse.ArgumentParser()
p.add_argument("--replays",required=True);p.add_argument("--archive",required=True);p.add_argument("--out",required=True)
a=p.parse_args()
def read(path):
    with open(path,newline="") as f: yield from csv.DictReader(f)
new={}
files=sorted(Path(a.replays).rglob("seed11_original_solver_rounds.csv"))
assert len(files)==10,len(files)
for file in files:
    for r in read(file):
        k=(r["profile_id"],float(r["sigma"]),int(r["round"]),r["strategy_id"])
        assert k not in new,k
        new[k]=r
assert len(new)==360000
fields=("output","price","profit","cumulative_profit")
outliers={f:[] for f in fields}
over_threshold={f:{str(t):0 for t in (0.1,1,5,10,50,100)} for f in fields}
actions=[]
terminal=defaultdict(dict)
seen=set()
for sigma in ("1","2"):
    for batch in range(10):
        for old in read(Path(a.archive)/f"sigma_{sigma}_batch_{batch:02d}_rounds.csv"):
            k=(old["profile_id"],float(old["sigma"]),int(old["round"]),old["strategy_id"])
            assert k in new and k not in seen,k
            seen.add(k);r=new[k]
            if old["action"]!=r["action"]:
                actions.append(dict(profile=k[0],sigma=k[1],round=k[2],strategy=k[3],archive_action=old["action"],replay_action=r["action"],archive_output=old["output"],replay_output=r["output"],archive_profit=old["profit"],replay_profit=r["profit"],archive_cumulative_profit=old["cumulative_profit"],replay_cumulative_profit=r["cumulative_profit"]))
            for f in fields:
                x=float(old[f]);y=float(r[f]);den=max(abs(x),abs(y))
                if den<=1e-6:continue
                pct=100*abs(x-y)/den
                for t in (0.1,1,5,10,50,100):
                    if pct>t:over_threshold[f][str(t)]+=1
                item=dict(profile=k[0],sigma=k[1],round=k[2],strategy=k[3],archive=x,replay=y,absolute_difference=abs(x-y),relative_pct=pct)
                h=outliers[f]
                entry=(pct,len(seen),item)
                if len(h)<25:heapq.heappush(h,entry)
                elif pct>h[0][0]:heapq.heapreplace(h,entry)
            if k[2]==200:
                terminal[(k[0],k[3])][k[1]]=(float(old["cumulative_profit"]),float(r["cumulative_profit"]))
assert len(seen)==360000 and len(terminal)==900
effect_rows=[];flips=[];max_error=0.
for (profile,strategy),v in sorted(terminal.items()):
    assert set(v)=={1.,2.}
    old=v[2.][0]-v[1.][0];replay=v[2.][1]-v[1.][1]
    change=replay-old
    max_error=max(max_error,abs(change))
    sign=lambda z:(z>0)-(z<0)
    row=dict(profile=profile,strategy=strategy,archive_sigma_effect=old,replay_sigma_effect=replay,effect_difference=change,absolute_effect_error=abs(change),effect_sign_changed=sign(old)!=sign(replay),relative_effect_error_pct=(100*abs(change)/max(abs(old),abs(replay)) if max(abs(old),abs(replay))>1e-6 else None))
    effect_rows.append(row)
    if row["effect_sign_changed"]:flips.append(row)
# Compare relative advantage of the two pre-specified policies A and B.
A="L3=cost_adjusted|L4=profit_based";B="L3=productivity|L4=profit_based"
by={(r["profile"],r["strategy"]):r for r in effect_rows}
ab=[]
for profile in sorted({r["profile"] for r in effect_rows}):
    x=by[(profile,A)];y=by[(profile,B)]
    d0=x["archive_sigma_effect"]-y["archive_sigma_effect"]
    d1=x["replay_sigma_effect"]-y["replay_sigma_effect"]
    ab.append(dict(profile=profile,archive_AB_sigma_effect=d0,replay_AB_sigma_effect=d1,absolute_difference=abs(d1-d0),sign_changed=((d0>0)-(d0<0))!=((d1>0)-(d1<0))))
def write(name,data):
    if not data:return
    with (out/name).open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
write("action_differences_detailed.csv",actions)
write("sigma_effect_by_profile_strategy.csv",effect_rows)
write("sigma_effect_sign_flips.csv",flips)
write("sigma_effect_AB_contrast.csv",ab)
for f,h in outliers.items():write("top25_relative_outliers_"+f+".csv",[z[2] for z in sorted(h,reverse=True)])
summary=dict(status="DESCRIPTIVE_ONLY",source_run=43526795473,archive_run=42463803820,rows=len(seen),action_mismatches=len(actions),action_cases=sorted({(r["profile"],r["sigma"]) for r in actions}),outlier_counts_above_pct=over_threshold,technology_effects_compared=len(effect_rows),technology_effect_sign_changes=len(flips),max_abs_sigma_effect_difference=max_error,AB_profiles=len(ab),AB_sigma_effect_sign_changes=sum(r["sign_changed"] for r in ab),max_abs_AB_sigma_effect_difference=max(r["absolute_difference"] for r in ab),economic_equivalence_established=False,research_validated=False,new_simulations=0)
(out/"materiality_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps(summary,indent=2))

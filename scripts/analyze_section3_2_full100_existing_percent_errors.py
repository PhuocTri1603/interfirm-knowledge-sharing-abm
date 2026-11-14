"""Existing-artifact economic error percentages and terminal ranking audit; no simulation."""
import argparse,csv,json
from pathlib import Path
from collections import defaultdict
from itertools import combinations
p=argparse.ArgumentParser()
p.add_argument("--replays",required=True);p.add_argument("--archive",required=True);p.add_argument("--out",required=True)
a=p.parse_args()
def rows(path):
    with open(path,newline="") as f:yield from csv.DictReader(f)
files=sorted(Path(a.replays).rglob("seed11_original_solver_rounds.csv"))
assert len(files)==10,len(files)
new={}
for file in files:
    for r in rows(file):
        k=(r["profile_id"],float(r["sigma"]),int(r["round"]),r["strategy_id"])
        assert k not in new,k
        new[k]=r
assert len(new)==360000,len(new)
fields=("output","price","profit","cumulative_profit")
stats={f:dict(n=0,pointwise_eligible=0,pointwise_max=0.,sum_abs_diff=0.,sum_abs_archive=0.,strict_mismatch=0) for f in fields}
terminal=defaultdict(lambda:{"archive":{},"replay":{}})
actions=[];ai_changes=0;adoption_changes=0
per_case=defaultdict(lambda:dict(action_mismatches=0,terminal_pairwise_reversals=0))
seen=set()
for sigma in ("1","2"):
    for batch in range(10):
        for old in rows(Path(a.archive)/f"sigma_{sigma}_batch_{batch:02d}_rounds.csv"):
            k=(old["profile_id"],float(old["sigma"]),int(old["round"]),old["strategy_id"])
            assert k in new and k not in seen,k
            seen.add(k);n=new[k];case=(k[0],k[1])
            if old["action"]!=n["action"]:
                per_case[case]["action_mismatches"]+=1
                actions.append(dict(profile=k[0],sigma=k[1],round=k[2],strategy=k[3],archive_action=old["action"],replay_action=n["action"]))
            ai_changes+=old["active_ai_count"]!=n["active_ai_count"]
            adoption_changes+=old["adopted_count"]!=n["adopted_count"]
            for f in fields:
                x=float(old[f]);y=float(n[f]);d=abs(x-y);s=stats[f]
                s["n"]+=1;s["sum_abs_diff"]+=d;s["sum_abs_archive"]+=abs(x)
                den=max(abs(x),abs(y))
                if den>1e-6:
                    s["pointwise_eligible"]+=1;s["pointwise_max"]=max(s["pointwise_max"],d/den)
                s["strict_mismatch"]+=d>1e-7+1e-9*den
            if k[2]==200:
                terminal[case]["archive"][k[3]]=float(old["cumulative_profit"])
                terminal[case]["replay"][k[3]]=float(n["cumulative_profit"])
assert len(seen)==360000 and len(terminal)==200
rank_changes=[];winner_changes=[];pair_reversals=[];case_rows=[]
for (profile,sigma),v in sorted(terminal.items()):
    x=v["archive"];y=v["replay"]
    assert len(x)==len(y)==9 and set(x)==set(y)
    rank=lambda d:sorted(d,key=lambda sid:(-d[sid],sid))
    ra=rank(x);rb=rank(y)
    if ra!=rb:rank_changes.append(dict(profile=profile,sigma=sigma,archive=ra,replay=rb))
    if ra[0]!=rb[0]:winner_changes.append(dict(profile=profile,sigma=sigma,archive=ra[0],replay=rb[0]))
    flips=0
    for s,t in combinations(sorted(x),2):
        da=x[s]-x[t];db=y[s]-y[t]
        sign=lambda z:(z>0)-(z<0)
        if sign(da)!=sign(db):
            flips+=1;pair_reversals.append(dict(profile=profile,sigma=sigma,first=s,second=t,archive_gap=da,replay_gap=db))
    per_case[(profile,sigma)]["terminal_pairwise_reversals"]=flips
    case_rows.append(dict(profile=profile,sigma=sigma,archive_winner=ra[0],replay_winner=rb[0],ranking_changed=ra!=rb,action_mismatches=per_case[(profile,sigma)]["action_mismatches"],terminal_pairwise_reversals=flips))
summary=dict(status="DESCRIPTIVE_ONLY",source_run=43526795473,archive_run=42463803820,rows=len(seen),profile_sigma_cases=len(terminal),fields={},action_mismatches=len(actions),action_mismatch_cases=sum(v["action_mismatches"]>0 for v in per_case.values()),ai_count_mismatches=ai_changes,adoption_count_mismatches=adoption_changes,terminal_full_ranking_changes=len(rank_changes),terminal_winner_changes=len(winner_changes),terminal_pairwise_sign_changes=len(pair_reversals),terminal_pairwise_comparisons=200*36,strict_numerical_equivalence="STRICT_FAIL",economic_equivalence_established=False,research_validated=False,new_simulations=0)
for f,s in stats.items():
    summary["fields"][f]=dict(pointwise_max_relative_pct=100*s["pointwise_max"],weighted_relative_absolute_pct=100*s["sum_abs_diff"]/s["sum_abs_archive"] if s["sum_abs_archive"] else None,pointwise_eligible=s["pointwise_eligible"],total_rows=s["n"],strict_mismatches=s["strict_mismatch"])
out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
(out/"full100_existing_artifact_percent_error.json").write_text(json.dumps(summary,indent=2)+"\n")
for name,data in (("action_mismatches.csv",actions),("terminal_pairwise_reversals.csv",pair_reversals),("profile_sigma_rankings.csv",case_rows)):
    with (out/name).open("w",newline="") as f:
        cols=list(data[0]) if data else (["profile","sigma","round","strategy","archive_action","replay_action"] if name=="action_mismatches.csv" else ["profile","sigma","first","second","archive_gap","replay_gap"])
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(data)
print(json.dumps(summary,indent=2))

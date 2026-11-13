"""Strict historical archive comparison for all seed11 100 profiles at sigma1/2.
Report FAIL as a valid diagnostic; do not relax original atol/rtol or hide failures.
"""
import argparse,csv,json,math
from pathlib import Path
from collections import defaultdict
p=argparse.ArgumentParser();p.add_argument("--replays",required=True);p.add_argument("--archive",required=True);p.add_argument("--out",required=True);a=p.parse_args()
out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
files=sorted(Path(a.replays).rglob("seed11_original_solver_rounds.csv"))
assert len(files)==10,len(files)
def load(path):
    with open(path) as f:return list(csv.DictReader(f))
new={}
for file in files:
    for r in load(file):
        key=(r["profile_id"],float(r["sigma"]),int(r["round"]),r["strategy_id"])
        assert key not in new,key
        new[key]=r
assert len(new)==360000,len(new)
orig={}
for sigma in ("1","2"):
    for batch in range(10):
        file=Path(a.archive)/f"sigma_{sigma}_batch_{batch:02d}_rounds.csv"
        for r in load(file):
            key=(r["profile_id"],float(r["sigma"]),int(r["round"]),r["strategy_id"])
            assert key not in orig,key
            orig[key]=r
assert set(orig)==set(new) and len(orig)==360000
fields=("output","price","profit","cumulative_profit","active_ai_count","adopted_count")
stats={k:dict(mismatched=0,max_abs=0.) for k in fields}
action_mismatches=0
winners_orig={};winners_new={}
first={}
by_profile=defaultdict(lambda:dict(strict_fail=False,action_mismatch=0))
for key,old in orig.items():
    newr=new[key];profile,sigma,t,s=key
    label=f"{profile}_sigma{sigma:g}"
    if old["action"]!=newr["action"]:
        action_mismatches+=1;by_profile[label]["action_mismatch"]+=1
    for field in fields:
        a0=float(old[field]);b0=float(newr[field]);diff=abs(a0-b0)
        st=stats[field];st["max_abs"]=max(st["max_abs"],diff)
        if diff>1e-7+1e-9*max(abs(a0),abs(b0)):
            st["mismatched"]+=1;by_profile[label]["strict_fail"]=True
            if field not in first:first[field]=dict(key=key,archive=a0,replay=b0,absolute_difference=diff)
    if t==200:
        for target,record in ((winners_orig,old),(winners_new,newr)):
            k=(profile,sigma)
            target.setdefault(k,[]).append((float(record["cumulative_profit"]),s))
def winner(values):return sorted(values,key=lambda x:(-x[0],x[1]))[0][1]
ranking_mismatch=sum(winner(winners_orig[k])!=winner(winners_new[k]) for k in winners_orig)
report=dict(status="STRICT_PASS" if not action_mismatches and not ranking_mismatch and all(v["mismatched"]==0 for v in stats.values()) else "STRICT_FAIL",
    source="historical archive run 42463803820 artifact 13618500797",
    original_engine_commit="c614b86d9192a57fb402b4772b3c3bb6bf80b79f",
    sigma=[1,2],profiles=100,rows=360000,atol=1e-7,rtol=1e-9,
    fields=stats,action_mismatches=action_mismatches,ranking_mismatches=ranking_mismatch,
    strict_fail_profile_sigma=sum(v["strict_fail"] for v in by_profile.values()),
    first_mismatches=first,strict_archive_equivalence_established=False,
    research_validated=False)
report["strict_archive_equivalence_established"]=report["status"]=="STRICT_PASS"
(out/"seed11_historical_strict_comparison.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))

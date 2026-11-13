"""Compare one unchanged-engine replay batch to its original archive slice."""
import argparse,csv,json
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument("--replay",required=True);p.add_argument("--archive",required=True);p.add_argument("--out",required=True)
a=p.parse_args()
def read(path):
    with open(path,newline="") as f:return list(csv.DictReader(f))
replay=read(a.replay)
assert len(replay)==36000,len(replay)
profiles={r["profile_id"] for r in replay}
assert len(profiles)==10
original={}
for sigma in ("1","2"):
    for batch in range(10):
        path=Path(a.archive)/f"sigma_{sigma}_batch_{batch:02d}_rounds.csv"
        for r in read(path):
            if r["profile_id"] in profiles:
                key=(r["profile_id"],float(r["sigma"]),int(r["round"]),r["strategy_id"])
                assert key not in original
                original[key]=r
assert len(original)==len(replay)
fields=("output","price","profit","cumulative_profit","active_ai_count","adopted_count")
counts={x:0 for x in fields}
max_abs={x:0. for x in fields}
actions=0
for r in replay:
    key=(r["profile_id"],float(r["sigma"]),int(r["round"]),r["strategy_id"])
    old=original.pop(key)
    actions+=old["action"]!=r["action"]
    for f in fields:
        x=float(old[f]);y=float(r[f]);d=abs(x-y)
        max_abs[f]=max(max_abs[f],d)
        counts[f]+=d>1e-7+1e-9*max(abs(x),abs(y))
assert not original
status="STRICT_PASS" if not actions and not any(counts.values()) else "STRICT_FAIL"
result=dict(status=status,rows=len(replay),profiles=sorted(profiles),action_mismatches=actions,field_mismatches=counts,max_abs=max_abs,research_validated=False,engine_modified=False)
Path(a.out).mkdir(parents=True,exist_ok=True)
(Path(a.out)/"historical_environment_subset_diagnostic.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))

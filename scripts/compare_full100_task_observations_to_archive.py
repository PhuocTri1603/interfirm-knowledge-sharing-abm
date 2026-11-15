"""Compare existing 30 observational artifacts with the original historical archive.
No model execution. Archive lacks task K/L, so those cannot be compared historically.
"""
import argparse,csv,json,zipfile,math
from io import TextIOWrapper
from pathlib import Path
from collections import defaultdict
p=argparse.ArgumentParser()
p.add_argument("--archive",required=True);p.add_argument("--observations",required=True);p.add_argument("--out",required=True)
a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
fields=("output","price","profit","cumulative_profit","active_ai_count","adopted_count")
stats={f:dict(n_mismatched=0,max_absolute=0.,sum_absolute=0.,first=None) for f in fields}
stats.update(action=dict(n_mismatched=0,first=None))
terminal_archive=defaultdict(dict);terminal_new=defaultdict(dict)
row_count=0;bad_keys=0;per_sigma=defaultdict(lambda:dict(rows=0,field_mismatches={f:0 for f in fields},action_mismatches=0))
with zipfile.ZipFile(a.archive) as archive:
    for sigma in ("0.5","1","2"):
        for batch in range(10):
            tag=f"sigma_{sigma}_batch_{batch:02d}"
            archive_name=tag+"_rounds.csv"
            observed_zip=Path(a.observations)/f"game1-task-sigma-{float(sigma):.1f}-batch-{batch}.zip"
            assert observed_zip.exists(),observed_zip
            with zipfile.ZipFile(observed_zip) as observed:
                with archive.open(archive_name) as old_file,observed.open("firm_dynamics.csv") as new_file:
                    old={ (r["profile_id"],int(r["round"]),r["strategy_id"]):r for r in csv.DictReader(TextIOWrapper(old_file)) }
                    seen=set()
                    for r in csv.DictReader(TextIOWrapper(new_file)):
                        key=(r["profile_id"],int(r["round"]),r["strategy_id"])
                        assert key in old and key not in seen,(tag,key)
                        seen.add(key);o=old[key];row_count+=1;per_sigma[sigma]["rows"]+=1
                        if o["action"]!=r["action"]:
                            st=stats["action"];st["n_mismatched"]+=1;per_sigma[sigma]["action_mismatches"]+=1
                            if st["first"] is None:st["first"]=dict(tag=tag,key=key,archive=o["action"],new=r["action"])
                        for f in fields:
                            x=float(o[f]);y=float(r[f]);assert math.isfinite(x) and math.isfinite(y)
                            diff=abs(x-y);st=stats[f]
                            st["max_absolute"]=max(st["max_absolute"],diff);st["sum_absolute"]+=diff
                            if diff>1e-7+1e-9*max(abs(x),abs(y)):
                                st["n_mismatched"]+=1;per_sigma[sigma]["field_mismatches"][f]+=1
                                if st["first"] is None:st["first"]=dict(tag=tag,key=key,archive=x,new=y)
                        if key[1]==200:
                            terminal_archive[(key[0],sigma)][key[2]]=float(o["cumulative_profit"])
                            terminal_new[(key[0],sigma)][key[2]]=float(r["cumulative_profit"])
                    assert len(old)==len(seen)==18000,(tag,len(old),len(seen))
            with zipfile.ZipFile(observed_zip) as observed:
                with observed.open("report.json") as f:
                    gate=json.load(f)
                    assert gate["status"]=="INSTRUMENTATION_PASS" and gate["task_rows"]==360000 and gate["firm_rows"]==18000
assert row_count==540000 and len(terminal_archive)==len(terminal_new)==300
def ranking(d):return tuple(sorted(d,key=lambda k:(-d[k],k)))
winner_changes=0;ranking_changes=0;ranking_by_sigma=defaultdict(lambda:dict(winner_changes=0,ranking_changes=0))
for key,old in terminal_archive.items():
    new=terminal_new[key];assert set(old)==set(new) and len(old)==9
    x=ranking(old);y=ranking(new)
    if x[0]!=y[0]:winner_changes+=1;ranking_by_sigma[key[1]]["winner_changes"]+=1
    if x!=y:ranking_changes+=1;ranking_by_sigma[key[1]]["ranking_changes"]+=1
for f in fields:stats[f]["mean_absolute"]=stats[f].pop("sum_absolute")/row_count
strict=(stats["action"]["n_mismatched"]==0 and all(stats[f]["n_mismatched"]==0 for f in fields))
report=dict(status="STRICT_PASS" if strict else "STRICT_FAIL",archive_run=42463803820,
    observation_run=43593085278,rows=row_count,profile_sigma=300,task_rows_verified_by_batch_gates=10800000,
    strict_atol=1e-7,strict_rtol=1e-9,fields=stats,per_sigma=dict(per_sigma),
    terminal_winner_changes=winner_changes,terminal_full_ranking_changes=ranking_changes,
    ranking_by_sigma=dict(ranking_by_sigma),
    historical_task_KL_comparison="NOT_IDENTIFIABLE: original archive does not record per-task K/L allocations",
    historical_task_AI_comparison="NOT_IDENTIFIABLE: original archive records active_ai_count only, not task-level identity",
    historical_cost_components_comparison="NOT_IDENTIFIABLE: original archive has no variable/adjustment/adoption cost components",
    current_task_KL_and_cost_internal_reconciliation="PASS in all 30 observational batch gates",
    research_validated=False,engine_invoked=False)
(out/"full100_archive_vs_observation.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
# Strict mismatch is a scientific result, not an execution failure.

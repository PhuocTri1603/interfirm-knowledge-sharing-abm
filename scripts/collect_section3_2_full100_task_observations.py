"""Observe all task allocations without changing decisions, optimizer or RNG."""
import argparse,csv,json,math
from pathlib import Path
from interfirm_abm.task_a6_market import approved_profiles
from interfirm_abm.game1_nine_strategy import run_game1
from reproduce_paper_section3_2 import params

def save(path,rows):
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--batch",type=int,required=True,choices=range(10))
    ap.add_argument("--sigma",type=float,required=True,choices=(.5,1.,2.))
    ap.add_argument("--out",required=True)
    a=ap.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    firm_rows=[];task_rows=[];market_rows=[];max_error=0.
    for firm in approved_profiles()[a.batch*10:(a.batch+1)*10]:
        tasks=[]
        result=run_game1(firm,a.sigma,params(),rounds=200,audit=True,task_audit=tasks)
        assert len(tasks)==36000 and len(result["players"])==1800
        by_key={}
        for t in tasks:
            k=(t["round"],t["strategy_id"])
            acc=by_key.setdefault(k,[0.,0.,0])
            acc[0]+=t["labor_allocation"];acc[1]+=t["capital_allocation"];acc[2]+=t["actual_ai_use"]
            assert t["labor_allocation"]>=0 and t["capital_allocation"]>=0
            assert not (t["actual_ai_use"] and not t["automation_eligible"])
        for r in result["players"]:
            acc=by_key[(r["round"],r["strategy_id"])]
            err=max(abs(acc[0]-r["labor_used"]),abs(acc[1]-r["capital_used"]),abs(acc[2]-r["active_ai_count"]),
                    abs(r["profit"]-(r["revenue"]-r["variable_cost"]-r["adjustment_cost"]-r["adoption_cost"])))
            max_error=max(max_error,err)
            assert err<1e-7
            firm_rows.append(dict(profile_id=firm.firm_id,sigma=a.sigma,**r))
        for m in result["market"]:
            assert abs(m["price"]-max(0.,2.-m["quantity"]/9.))<1e-8
            market_rows.append(dict(profile_id=firm.firm_id,sigma=a.sigma,**m))
        task_rows.extend(tasks)
    assert len(firm_rows)==18000 and len(task_rows)==360000 and len(market_rows)==2000
    save(out/"firm_dynamics.csv",firm_rows);save(out/"task_dynamics.csv",task_rows);save(out/"market_dynamics.csv",market_rows)
    report=dict(status="INSTRUMENTATION_PASS",batch=a.batch,sigma=a.sigma,
                firm_rows=len(firm_rows),task_rows=len(task_rows),market_rows=len(market_rows),
                max_identity_error=max_error,engine_changed=False,
                archive_equivalence_established=False,research_validated=False)
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report))
if __name__=="__main__":main()

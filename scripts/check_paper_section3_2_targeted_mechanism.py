"""Small strict baseline gate, then instrumented economic accounting for one profile."""
import argparse,json
from pathlib import Path
import pandas as pd
from reproduce_paper_section3_2 import params,replay,compare
from interfirm_abm.task_a6_market import approved_profiles

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--profile",default="F011")
    p.add_argument("--sigma",type=float,default=.5)
    p.add_argument("--archive",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    firm=next(x for x in approved_profiles() if x.firm_id==a.profile)
    batch=(int(a.profile[1:])-1)//10
    archived=pd.read_csv(Path(a.archive)/f"sigma_{a.sigma:g}_batch_{batch:02d}_rounds.csv")
    archived=archived[archived.profile_id==a.profile].copy()
    original,_,_=replay([firm],a.sigma,params(),False)
    gate=compare(archived,original)
    report={"profile":a.profile,"sigma":a.sigma,"archive_gate":gate,
            "instrumentation_gate":None,"economic_accounting":None,"research_validated":False}
    (out/"targeted_economic_gate.json").write_text(json.dumps(report,indent=2)+"\n")
    if not gate["pass"]:
        print("STRICT_ARCHIVE_GATE_FAILED",json.dumps(report));return 2
    instrumented,firm_rows,task_rows=replay([firm],a.sigma,params(),True)
    second=compare(original,instrumented)
    report["instrumentation_gate"]=second
    if second["pass"]:
        assert len(firm_rows)==1800 and len(task_rows)==36000
        firm_rows.to_csv(out/"firm_mechanisms.csv",index=False)
        task_rows.to_csv(out/"task_mechanisms.csv",index=False)
        checks={"rows":len(firm_rows),"task_rows":len(task_rows),
                "max_cost_identity_error":float((firm_rows.total_cost-firm_rows.variable_cost-firm_rows.adjustment_cost-firm_rows.adoption_cost).abs().max()),
                "max_profit_identity_error":float((firm_rows.revenue-firm_rows.total_cost-firm_rows.profit).abs().max()),
                "market_price_min":float(firm_rows.price.min()),
                "market_price_max":float(firm_rows.price.max()),
                "capital_total":float(firm_rows.capital_used.sum()),
                "labor_total":float(firm_rows.labor_used.sum()),
                "ai_task_rounds":int(task_rows.actual_ai_use.sum())}
        report["economic_accounting"]=checks
    (out/"targeted_economic_gate.json").write_text(json.dumps(report,indent=2)+"\n")
    print("TARGETED_ECONOMIC_RESULT",json.dumps(report))
    return 0 if second["pass"] else 3
if __name__=="__main__":
    raise SystemExit(main())

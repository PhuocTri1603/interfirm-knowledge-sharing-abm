"""Gate task-level observational reproduction against previously PASSed dynamic audit."""
import argparse,csv,json,math
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("--current",required=True);p.add_argument("--baseline",required=True);p.add_argument("--out",required=True);a=p.parse_args()
cur=Path(a.current);base=Path(a.baseline);out=Path(a.out)
def rows(folder,name):
    with (folder/name).open() as f:return list(csv.DictReader(f))
gate=json.loads((base/"dynamic_gate.json").read_text())
assert gate["audit_vs_prior_fixed_simd_pass"] is True
assert len(rows(cur,"task_dynamics.csv"))==36000
fields=("round","strategy_id","action","output","price","profit","cumulative_profit","adopted_count","active_ai_count","revenue","variable_cost","adjustment_cost","adoption_cost","newly_adopted_count","market_quantity","labor_used","capital_used")
maxdiff=0.
for name,columns in (("firm_dynamics.csv",fields),("market_dynamics.csv",("round","quantity","price"))):
    x=rows(cur,name);y=rows(base,name)
    assert len(x)==len(y)
    for a,b in zip(x,y):
        for col in columns:
            if col in ("strategy_id","action"):
                assert a[col]==b[col],(name,col)
            else:
                d=abs(float(a[col])-float(b[col]));maxdiff=max(maxdiff,d)
                assert d<=1e-8,(name,col,d)
tasks=rows(cur,"task_dynamics.csv")
assert len({(r["round"],r["strategy_id"],r["task_id"]) for r in tasks})==36000
assert all(math.isfinite(float(r[k])) for r in tasks for k in ("labor_allocation","capital_allocation","task_activity","normalized_activity"))
report={"pass":True,"source_dynamic_gate_pass":True,"task_records":len(tasks),"max_baseline_difference":maxdiff,"tolerance":1e-8,"original_archive_strict_gate_not_implied":True,"research_validated":False}
out.write_text(json.dumps(report,indent=2)+"\n")
print("TASK_OBSERVATION_GATE_PASS",json.dumps(report))

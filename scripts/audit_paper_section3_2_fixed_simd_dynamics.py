"""Audit dynamic economic states with the same fixed-SIMD numerical solver; no engine edits."""
import argparse,csv,json,math
from pathlib import Path
import numpy as np
from scipy.optimize import minimize as scipy_minimize
import interfirm_abm.game1_nine_strategy as game
from interfirm_abm.task_a6_market import approved_profiles
from reproduce_paper_section3_2 import params
from trial_paper_section3_2_deterministic_solver import stable_gradient

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--profile",required=True)
    ap.add_argument("--sigma",type=float,required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    old=game.minimize
    def wrapper(fun,x0,*pos,**kw):
        if kw.get("method")!="SLSQP":return old(fun,x0,*pos,**kw)
        cs=[]
        for c in kw.get("constraints",[]):
            cc=dict(c)
            if "jac" not in cc:
                x=np.asarray(x0,float);eye=np.eye(len(x));base=float(cc["fun"](np.zeros_like(x)))
                cc["jac"]=lambda z,fn=cc["fun"],eye=eye,base=base:np.asarray([float(fn(e))-base for e in eye],float)
            cs.append(cc)
        kw["constraints"]=cs;kw["jac"]=lambda x,objective=fun:stable_gradient(objective,x)
        return scipy_minimize(fun,x0,*pos,**kw)
    game.minimize=wrapper
    try:
        firm=next(f for f in approved_profiles() if f.firm_id==a.profile)
        result=game.run_game1(firm,a.sigma,params(),rounds=200,audit=True)
    finally:game.minimize=old
    rows=result["players"];markets=result["market"]
    assert len(rows)==1800 and len(markets)==200
    fields=["round","strategy_id","action","output","price","profit","cumulative_profit","adopted_count","active_ai_count","revenue","variable_cost","adjustment_cost","adoption_cost","newly_adopted_count","market_quantity","labor_used","capital_used"]
    with (out/"firm_dynamics.csv").open("w",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=fields);w.writeheader();w.writerows(rows)
    with (out/"market_dynamics.csv").open("w",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=["round","quantity","price"]);w.writeheader();w.writerows(markets)
    max_profit=max(abs(r["profit"]-(r["revenue"]-r["variable_cost"]-r["adjustment_cost"]-r["adoption_cost"])) for r in rows)
    max_quantity=max(abs(m["quantity"]-sum(r["output"] for r in rows if r["round"]==m["round"])) for m in markets)
    max_price=max(abs(m["price"]-max(0.,2.-m["quantity"]/9.)) for m in markets)
    report={"profile":a.profile,"sigma":a.sigma,"rows":len(rows),"market_rounds":len(markets),"max_profit_identity_error":max_profit,"max_market_quantity_error":max_quantity,"max_inverse_demand_error":max_price,"capital_and_labor_nonnegative":all(r["capital_used"]>=0 and r["labor_used"]>=0 for r in rows),"research_validated":False}
    (out/"audit_report.json").write_text(json.dumps(report,indent=2))
    assert max_profit<1e-8 and max_quantity<1e-8 and max_price<1e-8
    print("AUDIT",json.dumps(report))
if __name__=="__main__":main()

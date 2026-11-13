"""Fixed-SIMD SLSQP economic-equivalence test; does not alter frozen economic engine."""
import argparse,hashlib,json,os
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
    a=ap.parse_args()
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    old=game.minimize
    calls=[0]
    def wrapper(fun,x0,*pos,**kw):
        calls[0]+=1
        if kw.get("method")!="SLSQP":
            return old(fun,x0,*pos,**kw)
        cs=[]
        for c in kw.get("constraints",[]):
            cc=dict(c)
            if "jac" not in cc:
                x=np.asarray(x0,float);eye=np.eye(len(x));base=float(cc["fun"](np.zeros_like(x)))
                cc["jac"]=lambda z,fn=cc["fun"],eye=eye,base=base:np.asarray([float(fn(e))-base for e in eye],float)
            cs.append(cc)
        kw["constraints"]=cs
        kw["jac"]=lambda x,objective=fun:stable_gradient(objective,x)
        return scipy_minimize(fun,x0,*pos,**kw)
    game.minimize=wrapper
    try:
        firm=next(f for f in approved_profiles() if f.firm_id==a.profile)
        result=game.run_game1(firm,a.sigma,params(),rounds=200)
    finally:
        game.minimize=old
    rows=result["players"]
    digest=hashlib.sha256(json.dumps({"rows":rows,"markets":result["market"],"ranking":result["ranking"]},sort_keys=True,separators=(",",":")).encode()).hexdigest()
    payload={"profile":a.profile,"sigma":a.sigma,"rounds":200,"solver_calls":calls[0],"rows":rows,"markets":result["market"],"ranking":result["ranking"],"digest":digest,"research_validated":False}
    (out/"trial.json").write_text(json.dumps(payload))
    print("TRIAL",a.profile,a.sigma,digest,len(rows),calls[0])
if __name__=="__main__":main()

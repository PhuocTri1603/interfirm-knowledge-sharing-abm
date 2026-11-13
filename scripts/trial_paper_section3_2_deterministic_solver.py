"""Test deterministic numerical SLSQP derivatives without modifying the economic engine.

This is a solver-only candidate, NOT a validated replacement for the historical archive.
"""
import argparse, hashlib, json, os
from pathlib import Path
import numpy as np
from scipy.optimize import minimize as scipy_minimize
import interfirm_abm.game1_nine_strategy as game
from interfirm_abm.task_a6_market import approved_profiles
from reproduce_paper_section3_2 import params

def stable_gradient(fun, x):
    # Central differences at fixed, coordinate-wise perturbations, using
    # deterministic Python order. No BLAS reductions in the differencing.
    x=np.asarray(x,dtype=float)
    ans=np.empty(len(x))
    for j in range(len(x)):
        h=1e-6*max(1.,abs(float(x[j])))
        plus=x.copy();minus=x.copy()
        plus[j]+=h;minus[j]-=h
        ans[j]=(float(fun(plus))-float(fun(minus)))/(2*h)
    return ans

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True)
    ap.add_argument("--rounds",type=int,default=12)
    args=ap.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    original=game.minimize
    calls=[0]
    def deterministic(fun,x0,*pos,**kw):
        calls[0]+=1
        if kw.get("method")!="SLSQP":
            return original(fun,x0,*pos,**kw)
        cs=[]
        for c in kw.get("constraints",[]):
            cc=dict(c)
            if "jac" not in cc:
                # Constraints in the frozen engine are affine budget sums;
                # compute their exact derivatives via the known expression.
                x=np.asarray(x0,dtype=float)
                e=np.eye(len(x))
                origin=float(cc["fun"](np.zeros_like(x)))
                cc["jac"]=lambda z,fn=cc["fun"],e=e,origin=origin: np.asarray(
                    [float(fn(row))-origin for row in e],dtype=float)
            cs.append(cc)
        kw["constraints"]=cs
        kw["jac"]=lambda x,objective=fun: stable_gradient(objective,x)
        return scipy_minimize(fun,x0,*pos,**kw)
    game.minimize=deterministic
    try:
        firm=next(f for f in approved_profiles() if f.firm_id=="F011")
        result=game.run_game1(firm,.5,params(),rounds=args.rounds)
    finally:
        game.minimize=original
    rows=result["players"]
    payload={"profile":"F011","sigma":.5,"rounds":args.rounds,
             "solver_calls":calls[0],"threads":{k:os.getenv(k) for k in
             ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS")},
             "rows":rows,"markets":result["market"],
             "ranking":result["ranking"],"research_validated":False}
    serialized=json.dumps({"rows":rows,"markets":result["market"],"ranking":result["ranking"]},
                          sort_keys=True,separators=(",",":"))
    payload["digest"]=hashlib.sha256(serialized.encode()).hexdigest()
    (out/"deterministic_solver_trial.json").write_text(json.dumps(payload,indent=2)+"\n")
    print("SOLVER_TRIAL",json.dumps({"digest":payload["digest"],"solver_calls":calls[0],
          "rounds":args.rounds,"rows":len(rows)}))
if __name__=="__main__":
    main()

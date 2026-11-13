"""Replay exact second SLSQP invocation with frozen game engine and fixed SIMD.
Diagnostic only; no economic-model or solver replacement.
"""
import argparse, hashlib, json, os, platform
from pathlib import Path
import numpy as np
import scipy
from scipy.optimize import minimize as scipy_minimize, lsq_linear
import interfirm_abm.game1_nine_strategy as game
from interfirm_abm.task_a6_market import approved_profiles
from reproduce_paper_section3_2 import params
from trial_paper_section3_2_deterministic_solver import stable_gradient

def digest(x):
    return hashlib.sha256(np.asarray(x,dtype="<f8").tobytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    original=game.minimize
    calls=[0]
    results=[]
    def wrapped(fun,x0,*pos,**kw):
        if kw.get("method")!="SLSQP":
            return original(fun,x0,*pos,**kw)
        calls[0]+=1
        if calls[0]!=2:
            # Preserve the deterministic-gradient trial on all preceding calls.
            cs=[]
            for c in kw.get("constraints",[]):
                cc=dict(c)
                if "jac" not in cc:
                    x=np.asarray(x0,float); eye=np.eye(len(x)); base=float(cc["fun"](np.zeros_like(x)))
                    cc["jac"]=lambda z,fn=cc["fun"],eye=eye,base=base: np.asarray([float(fn(e))-base for e in eye])
                cs.append(cc)
            kw["constraints"]=cs
            kw["jac"]=lambda x,objective=fun: stable_gradient(objective,x)
            return scipy_minimize(fun,x0,*pos,**kw)
        # Exact objective closure, bounds and constraints from call 2, not reconstructed.
        x0=np.asarray(x0,float)
        cs=[]
        for c in kw.get("constraints",[]):
            cc=dict(c)
            if "jac" not in cc:
                eye=np.eye(len(x0)); base=float(cc["fun"](np.zeros_like(x0)))
                cc["jac"]=lambda z,fn=cc["fun"],eye=eye,base=base: np.asarray([float(fn(e))-base for e in eye])
            cs.append(cc)
        kw["constraints"]=cs
        kw["jac"]=lambda x,objective=fun: stable_gradient(objective,x)
        original_input={"x0":x0.tolist(),"x0_sha256":digest(x0),
          "f0":float(fun(x0)),"gradient0":stable_gradient(fun,x0).tolist(),
          "bounds":[list(b) for b in kw["bounds"]],
          "constraints0":[float(c["fun"](x0)) for c in cs],
          "constraint_jacobians0":[np.asarray(c["jac"](x0)).tolist() for c in cs],
          "constraint_types":[c["type"] for c in cs],
          "options":kw.get("options")}
        def diagnostic(res):
            x=np.asarray(res.x,float)
            g=stable_gradient(fun,x)
            # Estimate stationarity by nonnegative inequality multipliers and free
            # equality multipliers. For this call, all constraints are equality.
            cols=[]; labels=[]; fixed=[]
            for j,c in enumerate(cs):
                a=np.asarray(c["jac"](x),float)
                cols.append(a);labels.append("constraint_"+str(j))
                fixed.append(c["type"]=="eq")
            active_tol=1e-7
            for j,(lo,hi) in enumerate(kw["bounds"]):
                if lo is not None and x[j]-lo<=active_tol:
                    a=np.zeros(len(x));a[j]=1;cols.append(a);labels.append("lower_"+str(j));fixed.append(False)
                if hi is not None and hi-x[j]<=active_tol:
                    a=np.zeros(len(x));a[j]=-1;cols.append(a);labels.append("upper_"+str(j));fixed.append(False)
            # Minimize ||g - A^T lambda|| with lambda>=0 for inequalities
            # written as c(x)>=0; equality multipliers unrestricted.
            if cols:
                A=np.stack(cols,axis=1)
                lower=np.asarray([-np.inf if f else 0. for f in fixed])
                upper=np.full(len(cols),np.inf)
                fit=lsq_linear(A,g,bounds=(lower,upper),tol=1e-12,max_iter=500)
                residual=g-A@fit.x
                mult={k:float(v) for k,v in zip(labels,fit.x)}
            else:
                residual=g;mult={}
            cv=[float(c["fun"](x)) for c in cs]
            violation=max([abs(v) if c["type"]=="eq" else max(0.,-v) for v,c in zip(cv,cs)]+[0.])
            for v,(lo,hi) in zip(x,kw["bounds"]):
                if lo is not None: violation=max(violation,max(0.,lo-v))
                if hi is not None: violation=max(violation,max(0.,v-hi))
            return {"x":x.tolist(),"sha256":digest(x),"objective":float(res.fun),
              "gradient":g.tolist(),"gradient_inf":float(np.max(np.abs(g))),
              "kkt_stationarity_inf":float(np.max(np.abs(residual))),
              "max_primal_violation":float(violation),
              "multipliers":mult,"status":int(res.status),"success":bool(res.success),
              "message":str(res.message),"nit":int(getattr(res,"nit",-1)),
              "nfev":int(getattr(res,"nfev",-1)),"njev":int(getattr(res,"njev",-1))}
        for repeat in range(3):
            result=scipy_minimize(fun,x0.copy(),*pos,**kw)
            results.append(diagnostic(result))
        return result
    game.minimize=wrapped
    try:
        firm=next(f for f in approved_profiles() if f.firm_id=="F011")
        game.run_game1(firm,.5,params(),rounds=1)
    finally:
        game.minimize=original
    assert len(results)==3 and calls[0]>=2
    runtime={"python":platform.python_version(),"numpy":np.__version__,"scipy":scipy.__version__,
      "platform":platform.platform(),"machine":platform.machine(),
      "env":{k:os.getenv(k) for k in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","BLIS_NUM_THREADS","NUMEXPR_NUM_THREADS","PYTHONHASHSEED","NPY_DISABLE_CPU_FEATURES","OPENBLAS_CORETYPE")}}
    payload={"input":original_input,"repeats":results,"runtime":runtime,"research_validated":False}
    (out/"call2_repeats.json").write_text(json.dumps(payload,indent=2))
    print("CALL2_REPEATS",json.dumps({"input_hash":original_input["x0_sha256"],"solution_hashes":[r["sha256"] for r in results],"kkt":[r["kkt_stationarity_inf"] for r in results]}))
if __name__=="__main__":
    main()

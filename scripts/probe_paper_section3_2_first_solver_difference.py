"""Isolated SLSQP first-divergence diagnostic; economic engine remains frozen."""
import argparse, hashlib, json, os, platform
from pathlib import Path
import numpy as np
import scipy
import interfirm_abm.game1_nine_strategy as game
from interfirm_abm.task_a6_market import approved_profiles
from reproduce_paper_section3_2 import params
from trial_paper_section3_2_deterministic_solver import stable_gradient
from scipy.optimize import minimize as scipy_minimize

def sha(a):
    return hashlib.sha256(np.asarray(a,dtype="<f8").tobytes()).hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    p.add_argument("--rounds",type=int,default=4)
    args=p.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    original=game.minimize
    traces=[]
    def wrapper(fun,x0,*pos,**kw):
        if kw.get("method")!="SLSQP":
            return original(fun,x0,*pos,**kw)
        constraints=[]
        for c in kw.get("constraints",[]):
            cc=dict(c)
            if "jac" not in cc:
                x=np.asarray(x0,dtype=float)
                eye=np.eye(len(x))
                base=float(cc["fun"](np.zeros_like(x)))
                cc["jac"]=lambda z,fn=cc["fun"],eye=eye,base=base: np.asarray([float(fn(e))-base for e in eye])
            constraints.append(cc)
        kw["constraints"]=constraints
        kw["jac"]=lambda x,objective=fun: stable_gradient(objective,x)
        x0=np.asarray(x0,dtype=float)
        pre={"x0":x0.tolist(),"x0_sha256":sha(x0),"f0":float(fun(x0)),
             "grad0":stable_gradient(fun,x0).tolist(),
             "constraints0":[float(c["fun"](x0)) for c in constraints],
             "constraint_types":[c["type"] for c in constraints]}
        res=scipy_minimize(fun,x0,*pos,**kw)
        x=np.asarray(res.x,dtype=float)
        g=stable_gradient(fun,x)
        violations=[]
        for c in constraints:
            v=float(c["fun"](x))
            violations.append(abs(v) if c["type"]=="eq" else max(0.,-v))
        bounds=kw.get("bounds")
        bound_violation=0.
        if bounds is not None:
            for value,b in zip(x,bounds):
                lo,hi=b
                if lo is not None: bound_violation=max(bound_violation,float(lo)-value)
                if hi is not None: bound_violation=max(bound_violation,value-float(hi))
        traces.append({"call":len(traces)+1,"input":pre,"solution":x.tolist(),
            "solution_sha256":sha(x),"objective":float(res.fun),
            "gradient":g.tolist(),"gradient_inf_norm":float(np.linalg.norm(g,np.inf)),
            "status":int(res.status),"success":bool(res.success),"message":str(res.message),
            "nit":int(getattr(res,"nit",-1)),"nfev":int(getattr(res,"nfev",-1)),
            "njev":int(getattr(res,"njev",-1)),
            "constraint_residuals":[float(c["fun"](x)) for c in constraints],
            "max_constraint_violation":max(violations,default=0.),
            "bound_violation":max(0.,bound_violation)})
        return res
    game.minimize=wrapper
    try:
        firm=next(f for f in approved_profiles() if f.firm_id=="F011")
        result=game.run_game1(firm,.5,params(),rounds=args.rounds)
    finally:
        game.minimize=original
    runtime={"python":platform.python_version(),"platform":platform.platform(),
        "processor":platform.processor(),"numpy":np.__version__,"scipy":scipy.__version__,
        "threads":{k:os.getenv(k) for k in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","BLIS_NUM_THREADS","NUMEXPR_NUM_THREADS","PYTHONHASHSEED","NPY_DISABLE_CPU_FEATURES","OPENBLAS_CORETYPE")}}
    payload={"runtime":runtime,"calls":traces,"rows":result["players"],"market":result["market"],"research_validated":False}
    (out/"slsqp_first_divergence.json").write_text(json.dumps(payload,indent=2))
    print("TARGETED_TRACE",len(traces),"calls",len(result["players"]),"rows")
if __name__=="__main__":
    main()

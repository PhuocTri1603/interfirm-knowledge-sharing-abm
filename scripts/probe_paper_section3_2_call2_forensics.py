"""Numerical forensics of SLSQP invocation #2; no economic engine edits."""
import argparse,json,hashlib,os
from pathlib import Path
import numpy as np
from scipy.optimize._numdiff import approx_derivative
from scipy.optimize import lsq_linear
import interfirm_abm.game1_nine_strategy as game
from interfirm_abm.task_a6_market import approved_profiles
from reproduce_paper_section3_2 import params

class Stop(Exception): pass

def hashvec(x):
    return hashlib.sha256(np.asarray(x,dtype="<f8").tobytes()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",required=True)
    a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    orig=game.minimize;idx=[0];report={}
    def intercept(fun,x0,*pos,**kw):
        idx[0]+=1
        if idx[0]!=2:return orig(fun,x0,*pos,**kw)
        x0=np.asarray(x0,dtype=float).copy()
        cs=kw.get("constraints",[])
        bounds=kw.get("bounds")
        n=len(x0)
        def vec(fun_,x):
            return np.atleast_1d(np.asarray(fun_(x),dtype=float)).ravel()
        def snapshot(x):
            return {"f":float(fun(x)),"c":[vec(c["fun"],x).tolist() for c in cs]}
        def numerical(x):
            fgrad=approx_derivative(fun,x,method="2-point")
            cjac=[approx_derivative(c["fun"],x,method="2-point") for c in cs]
            return np.asarray(fgrad).reshape(-1),[np.asarray(v).reshape(-1,n) for v in cjac]
        def feasibility(x):
            constraints=[]
            for c in cs:
                v=vec(c["fun"],x)
                if c["type"]=="eq": residual=float(np.max(np.abs(v)))
                else: residual=float(np.max(np.maximum(-v,0)))
                constraints.append({"type":c["type"],"violation":residual,"minimum":float(v.min()),"maximum":float(v.max())})
            bv=[]
            for j,b in enumerate(bounds or []):
                lo,hi=b
                bv.append(max(float(lo-x[j]) if lo is not None else 0,
                              float(x[j]-hi) if hi is not None else 0,0))
            return {"constraints":constraints,"bound_max_violation":max(bv,default=0)}
        def kkt(x):
            g,jacs=numerical(x)
            cols=[];labels=[]
            for i,c in enumerate(cs):
                v=vec(c["fun"],x)
                for k,vk in enumerate(v):
                    if c["type"]=="eq" or vk<=1e-6:
                        cols.append(jacs[i][k] if c["type"]=="eq" else -jacs[i][k])
                        labels.append({"constraint":i,"component":k,"type":c["type"],"value":float(vk)})
            for j,b in enumerate(bounds or []):
                lo,hi=b
                if lo is not None and x[j]-lo<=1e-6:
                    col=np.zeros(n);col[j]=-1;cols.append(col);labels.append({"bound_lower":j})
                if hi is not None and hi-x[j]<=1e-6:
                    col=np.zeros(n);col[j]=1;cols.append(col);labels.append({"bound_upper":j})
            if cols:
                mat=np.column_stack(cols)
                # Equality multipliers unrestricted; inequality multipliers >=0.
                eq_count=sum(1 for label in labels if label.get("type")=="eq")
                lb=np.array([-np.inf if label.get("type")=="eq" else 0.0 for label in labels])
                res=lsq_linear(mat,-g,bounds=(lb,np.full(len(labels),np.inf)),tol=1e-12,max_iter=500)
                multipliers=res.x
                stationarity=float(np.linalg.norm(g+mat@multipliers,np.inf))
                complementarity=max((abs(float(multipliers[i])*label["value"]) for i,label in enumerate(labels) if label.get("type")=="ineq"),default=0)
            else:
                multipliers=np.empty(0);stationarity=float(np.linalg.norm(g,np.inf));complementarity=0
            return {"gradient_norm_inf":float(np.linalg.norm(g,np.inf)),
                    "stationarity_inf_estimate":stationarity,
                    "complementarity_estimate":complementarity,
                    "active_constraints":labels,"multipliers":multipliers.tolist(),
                    "note":"Finite-difference KKT diagnostic with active-set threshold 1e-6; not an exact certificate."}
        x0_eval=snapshot(x0)
        derivatives={}
        for method in ("2-point","3-point"):
            grad=approx_derivative(fun,x0,method=method)
            derivatives[method]={"gradient":np.asarray(grad).reshape(-1).tolist(),
                "constraint_jacobians":[np.asarray(approx_derivative(c["fun"],x0,method=method)).reshape(-1,n).tolist() for c in cs]}
        traces=[];event=[0]
        def record(kind,fn):
            def wrapped(x,*aa,**kk):
                v=fn(x,*aa,**kk)
                event[0]+=1
                if event[0]<=160:
                    traces.append({"seq":event[0],"kind":kind,"x":np.asarray(x,dtype=float).tolist(),
                                   "x_hash":hashvec(x),"value":np.asarray(v,dtype=float).ravel().tolist()})
                return v
            return wrapped
        wrapped_constraints=[dict(c,fun=record("constraint_"+str(i),c["fun"])) for i,c in enumerate(cs)]
        altered=dict(kw,constraints=wrapped_constraints)
        result=orig(record("objective",fun),x0.copy(),*pos,**altered)
        x=np.asarray(result.x,dtype=float)
        # Post-hoc derivative diagnostics: only after SLSQP returns, so these
        # evaluations cannot perturb the traced optimization trajectory.
        window=[t for t in traces if 120<=t["seq"]<=136]
        distinct={}
        for t in window:
            distinct.setdefault(t["x_hash"],t["x"])
        jacobian_window=[]
        for fingerprint,coords in distinct.items():
            point=np.asarray(coords,dtype=float)
            entry={"x_hash":fingerprint,"events":[t["seq"] for t in window if t["x_hash"]==fingerprint],
                   "x":point.tolist(),"derivatives":{}}
            for method in ("2-point","3-point"):
                gj=np.asarray(approx_derivative(fun,point,method=method)).reshape(-1)
                blocks=[np.asarray(approx_derivative(c["fun"],point,method=method)).reshape(-1,n) for c in cs]
                j=np.vstack(blocks) if blocks else np.empty((0,n))
                sv=np.linalg.svd(j,compute_uv=False) if j.size else np.empty(0)
                positive=sv[sv>max(sv[0]*1e-12,1e-15)] if len(sv) else []
                entry["derivatives"][method]={"objective_gradient":gj.tolist(),
                    "constraint_jacobian":j.tolist(),"singular_values":sv.tolist(),
                    "jacobian_rank_relative_1e-12":int(len(positive)),
                    "jacobian_condition_nonzero":float(positive[0]/positive[-1]) if len(positive) else None,
                    "jacobian_full_row_rank":bool(len(sv)==len(positive)),
                    "jacobian_condition_full":float(sv[0]/sv[-1]) if len(sv) and sv[-1]>0 else None}
            jacobian_window.append(entry)
        report.update(jacobian_window=jacobian_window,
            jacobian_window_events=[t["seq"] for t in window],
            jacobian_note="Post-hoc finite differences at observed SLSQP evaluation points; condition number of equality-constraint Jacobian, not Hessian/KKT system.")
        report.update({"profile":"F011","sigma":.5,"call":2,
            "threads":{k:os.environ.get(k) for k in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS")},
            "x0":x0.tolist(),"x0_hash":hashvec(x0),"x0_evaluation":x0_eval,
            "derivatives_at_x0":derivatives,
            "solution":x.tolist(),"solution_hash":hashvec(x),
            "objective":float(result.fun),"success":bool(result.success),"status":int(result.status),
            "nit":int(result.nit),"nfev":int(result.nfev),
            "solution_feasibility":feasibility(x),"kkt":kkt(x),
            "evaluation_trace":traces,"total_evaluation_events":event[0],
            "trace_limit":160,"research_validated":False})
        raise Stop
    game.minimize=intercept
    try:
        game.run_game1(next(f for f in approved_profiles() if f.firm_id=="F011"),.5,params(),rounds=200)
        raise RuntimeError("Solver call #2 was not reached")
    except Stop:pass
    finally:game.minimize=orig
    (out/"call2_forensics.json").write_text(json.dumps(report,indent=2)+"\n")
    print("CALL2_FORENSICS",json.dumps({"solution_hash":report["solution_hash"],
          "objective":report["objective"],"stationarity_inf_estimate":report["kkt"]["stationarity_inf_estimate"],
          "constraint_violations":report["solution_feasibility"],
          "trace_events":len(report["evaluation_trace"])}))
if __name__=="__main__":main()

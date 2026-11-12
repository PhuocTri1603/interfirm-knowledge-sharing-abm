"""Isolate SLSQP call #2; compare repeated identical-input evaluations and solutions.

Original economic engine remains unchanged. The probe intentionally stops the game
before call #2 is returned, so repeated minimizations cannot influence later rounds.
"""
import argparse,hashlib,json,os,platform,sys
from pathlib import Path
import numpy as np
import scipy
import interfirm_abm.game1_nine_strategy as game
from interfirm_abm.task_a6_market import approved_profiles
from reproduce_paper_section3_2 import params

class ProbeComplete(Exception): pass

def digest(x):
    arr=np.asarray(x,dtype="<f8")
    return hashlib.sha256(arr.tobytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True)
    ap.add_argument("--repeats",type=int,default=4)
    args=ap.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    assert args.repeats>=2
    original=game.minimize
    count=[0];report={}
    def probe(fun,x0,*pos,**kw):
        count[0]+=1
        if count[0]!=2: return original(fun,x0,*pos,**kw)
        x0=np.asarray(x0,dtype=float).copy()
        bounds=kw.get("bounds")
        constraints=kw.get("constraints",())
        # Evaluate functions only after interception; do not return to the game.
        def evaluate(x):
            value=float(fun(x))
            cv=[]
            for c in constraints:
                v=np.asarray(c["fun"](x),dtype=float).ravel()
                cv.append({"type":c.get("type"),"values":v.tolist(),"hash":digest(v)})
            return {"objective":value,"constraints":cv}
        input_eval=[evaluate(x0) for _ in range(args.repeats)]
        solutions=[]
        for k in range(args.repeats):
            result=original(fun,x0.copy(),*pos,**kw)
            x=np.asarray(result.x,dtype=float)
            solutions.append({"repeat":k+1,"x":x.tolist(),"x_sha256":digest(x),
                "objective":float(result.fun),"nit":int(result.nit),
                "nfev":int(result.nfev),"status":int(result.status),
                "success":bool(result.success),
                "constraint_at_solution":evaluate(x)["constraints"]})
        # Repeat objective at the same solution to test deterministic evaluation.
        reevaluations=[evaluate(np.asarray(solutions[0]["x"],dtype=float))
                       for _ in range(args.repeats)]
        xs=np.asarray([s["x"] for s in solutions])
        report.update({"profile":"F011","sigma":0.5,"call_index":2,
            "method":kw.get("method"),"options":kw.get("options"),
            "x0":x0.tolist(),"x0_sha256":digest(x0),
            "bounds":repr(bounds),"input_evaluations":input_eval,
            "solutions":solutions,"reevaluations_at_first_solution":reevaluations,
            "max_solution_coordinate_spread":float(np.ptp(xs,axis=0).max()),
            "solution_hashes_identical":len({s["x_sha256"] for s in solutions})==1,
            "input_evaluations_identical":all(v==input_eval[0] for v in input_eval),
            "solution_evaluations_identical":all(v==reevaluations[0] for v in reevaluations),
            "python":sys.version,"numpy":np.__version__,"scipy":scipy.__version__,
            "platform":platform.platform(),
            "thread_settings":{k:os.environ.get(k) for k in
                               ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS")},
            "research_validated":False})
        raise ProbeComplete
    game.minimize=probe
    try:
        game.run_game1(next(f for f in approved_profiles() if f.firm_id=="F011"),
                       .5,params(),rounds=200)
        raise AssertionError("Expected to intercept solver call #2")
    except ProbeComplete:
        pass
    finally:
        game.minimize=original
    (out/"solver_call2_repeated.json").write_text(json.dumps(report,indent=2)+"\n")
    print("SOLVER_CALL2_REPEATED",json.dumps({k:report[k] for k in
          ("max_solution_coordinate_spread","solution_hashes_identical",
           "input_evaluations_identical","solution_evaluations_identical")}))
if __name__=="__main__": main()

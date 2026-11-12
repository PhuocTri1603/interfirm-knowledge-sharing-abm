"""Targeted observational solver-stability investigation of three outlier cases.

Wrap scipy.optimize.minimize as imported by Game 1 to collect diagnostics;
never change optimizer arguments, result, chosen plans, or economic engine.
Compare two identical runs in the same process, and original CI benchmark.
"""
import argparse,csv,json,math,sys
from collections import Counter,defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_game1_ai_counterfactual import params,simulate
from interfirm_abm.task_a6_market import approved_profiles
import interfirm_abm.game1_nine_strategy as game

CASES=((26,2.,47),(31,2.,11),(34,1.,11))
def run_case(firm,sigma,seed,disable,repeat):
    original=game.minimize
    calls=[]
    def observe(fun,x0,*args,**kwargs):
        result=original(fun,x0,*args,**kwargs)
        calls.append(dict(method=kwargs.get("method","unknown"),success=bool(result.success),
            status=int(result.status),message=str(result.message),fun=float(result.fun),
            nit=int(getattr(result,"nit",-1)),nfev=int(getattr(result,"nfev",-1)),
            nvar=len(x0),max_abs_x=float(max(abs(v) for v in result.x)) if len(result.x) else 0.,
            finite=bool(math.isfinite(float(result.fun)))))
        return result
    game.minimize=observe
    try:
        outcome=simulate(firm,sigma,params(seed),200,disable)
    finally:
        game.minimize=original
    rows=outcome["players"]
    assert len(rows)==1800
    return calls,rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--case",type=int,choices=(26,31,34),required=True)
    ap.add_argument("--out",default="results/game1_solver_outliers")
    a=ap.parse_args()
    i,sigma,seed=next(x for x in CASES if x[0]==a.case)
    firm=approved_profiles()[i]
    runs={}
    for repeat in (1,2):
        for label,disable in (("ai",False),("no",True)):
            calls,rows=run_case(firm,sigma,seed,disable,repeat)
            runs[(repeat,label)]=(calls,rows)
            print("RUN",i,sigma,seed,repeat,label,"minimize_calls",len(calls),
                  "failed_calls",sum(not c["success"] for c in calls),
                  "cobyqa_calls",sum(c["method"]=="COBYQA" for c in calls),flush=True)
    summary=[];diag=[]
    for repeat in (1,2):
        ai=runs[(repeat,"ai")][1];no=runs[(repeat,"no")][1]
        for horizon in (20,200):
            delta=sum(r["profit"] for r in ai if r["round"]<=horizon)-sum(r["profit"] for r in no if r["round"]<=horizon)
            summary.append(dict(profile_index=i,sigma=sigma,seed=seed,repeat=repeat,horizon=horizon,delta_profit=delta))
        for label in ("ai","no"):
            calls=runs[(repeat,label)][0]
            for index,c in enumerate(calls):
                diag.append(dict(profile_index=i,sigma=sigma,seed=seed,repeat=repeat,scenario=label,call_index=index,**c))
    diffs=[]
    for label in ("ai","no"):
        left={(r["round"],r["strategy_id"]):r for r in runs[(1,label)][1]}
        right={(r["round"],r["strategy_id"]):r for r in runs[(2,label)][1]}
        assert left.keys()==right.keys()
        for key in sorted(left):
            x,y=left[key],right[key]
            if any(abs(float(x[col])-float(y[col]))>1e-8 for col in ("profit","output","price","capital_used","labor_used")) or x["action"]!=y["action"]:
                diffs.append(dict(scenario=label,round=key[0],strategy_id=key[1],
                  action_first=x["action"],action_second=y["action"],
                  delta_profit=float(y["profit"])-float(x["profit"]),
                  delta_output=float(y["output"])-float(x["output"]),
                  delta_price=float(y["price"])-float(x["price"])))
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    def save(name,rows,fields):
        with (out/name).open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    save(f"summary_{i}.csv",summary,list(summary[0]))
    save(f"solver_calls_{i}.csv",diag,list(diag[0]))
    save(f"within_process_differences_{i}.csv",diffs,
         ("scenario","round","strategy_id","action_first","action_second","delta_profit","delta_output","delta_price"))
    print("SUMMARY",json.dumps(summary))
    print("WITHIN_PROCESS_DIFFERENCES",len(diffs),"first",diffs[:3])
    print("SOLVER_STATUS",dict(Counter((x["method"],x["status"]) for x in diag)))
    print("NOTE solver wrapper only; success/feasibility not global-optimality certification")
if __name__=="__main__":main()

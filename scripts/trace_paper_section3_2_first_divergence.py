"""Targeted solver trace for first archived/replay divergence. Original engine unchanged.

The archived experiment did not log SLSQP calls, so this identifies the earliest
observable divergence and the solver calls contributing to its policy/round.
It cannot identify an exact differing historical optimizer invocation.
"""
import argparse,json,platform,sys
from pathlib import Path
import numpy as np,pandas as pd,scipy
import scipy.optimize as so
import interfirm_abm.game1_nine_strategy as game
from interfirm_abm.task_a6_market import approved_profiles

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--archive",required=True)
    ap.add_argument("--out",required=True)
    ap.add_argument("--profile",default="F011")
    ap.add_argument("--sigma",type=float,default=.5)
    ap.add_argument("--atol",type=float,default=1e-7)
    ap.add_argument("--rtol",type=float,default=1e-9)
    args=ap.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    from reproduce_paper_section3_2 import params
    profile=next(x for x in approved_profiles() if x.firm_id==args.profile)
    batch=(int(args.profile[1:])-1)//10
    archive=pd.read_csv(Path(args.archive)/f"sigma_{args.sigma:g}_batch_{batch:02d}_rounds.csv")
    archive=archive[archive.profile_id==args.profile].copy()
    orig_minimize=game.minimize
    orig_candidate=game.candidate
    calls=[];candidates=[]
    context={"round":None,"strategy":None,"candidate_index":0,"optimizer_index":0}
    def traced_minimize(fun,x0,*a,**kw):
        context["optimizer_index"]+=1
        res=orig_minimize(fun,x0,*a,**kw)
        calls.append(dict(call_index=context["optimizer_index"],round=context["round"],
            strategy_id=context["strategy"],candidate_index=context["candidate_index"],
            method=kw.get("method"),success=bool(res.success),status=int(res.status),
            objective=float(res.fun),initial_x_hash=__import__("hashlib").sha256(np.asarray(x0,dtype="<f8").tobytes()).hexdigest()[:20],initial_x_norm=float(np.linalg.norm(x0)),constraint_count=len(kw.get("constraints",[])),nit=int(getattr(res,"nit",-1)),
            nfev=int(getattr(res,"nfev",-1)),x_norm=float(np.linalg.norm(res.x)),
            x_hash=__import__("hashlib").sha256(np.asarray(res.x,dtype="<f8").tobytes()).hexdigest()[:20]))
        return res
    def traced_candidate(firm,tech,l3,l4,budget,price,previous,adopted,p,last_modes=None):
        context["candidate_index"]+=1
        context["strategy"]=f"L3={l3}|L4={l4}"
        begin=len(calls)
        result=orig_candidate(firm,tech,l3,l4,budget,price,previous,adopted,p,last_modes)
        candidates.append(dict(round=context["round"],strategy_id=context["strategy"],
            candidate_index=context["candidate_index"],start_solver_call=begin+1,
            end_solver_call=len(calls),n_solver_calls=len(calls)-begin,
            budget=budget,prior_price=price,output=result[2],cost=result[3],
            modes="".join("1" if v else "0" for v in result[5])))
        return result
    # Wrap round by observing the first candidate of each round. No RNG consumption.
    # The original engine runs all 9 strategies in deterministic order per round.
    # A first candidate may be skipped if the first policy shuts down.
    # Infer round via a separate observational wrapper around adjustment called
    # for shutdown; more robust: use the 9-strategy candidate ordering against
    # replay actions after the run, with candidate indices per round.
    game.minimize=traced_minimize
    game.candidate=traced_candidate
    try:
        result=game.run_game1(profile,args.sigma,params(),rounds=200)
    finally:
        game.minimize=orig_minimize;game.candidate=orig_candidate
    rows=pd.DataFrame(result["players"])
    rows["profile_id"]=args.profile;rows["sigma"]=args.sigma
    keys=["round","strategy_id"]
    z=archive.merge(rows,on=keys,suffixes=("_archived","_replayed"),validate="one_to_one")
    assert len(z)==1800
    diffs=[]
    for field in ("output","price","profit","cumulative_profit"):
        lhs=z[field+"_archived"].to_numpy(float);rhs=z[field+"_replayed"].to_numpy(float)
        bad=np.abs(lhs-rhs)>(args.atol+args.rtol*np.maximum(np.abs(lhs),np.abs(rhs)))
        for i in np.flatnonzero(bad):
            diffs.append(dict(round=int(z.iloc[i]["round"]),strategy_id=z.iloc[i]["strategy_id"],
                variable=field,archived=float(lhs[i]),replayed=float(rhs[i]),
                absolute_error=float(abs(lhs[i]-rhs[i]))))
    diff=pd.DataFrame(diffs)
    diff.to_csv(out/"first_profile_round_differences.csv",index=False)
    first=int(diff["round"].min()) if len(diff) else None
    first_diffs=diff[diff["round"]==first] if first is not None else diff
    # Associate candidates with their rounds by ordered non-shutdown policies,
    # using archived/replayed per-round action sequence. No simulation modifications.
    active=[(int(r["round"]),r["strategy_id"]) for r in result["players"] if r["action"]!="shutdown"]
    assert len(active)==len(candidates)
    for item,(round_,strategy) in zip(candidates,active):
        assert item["strategy_id"]==strategy
        item["round"]=round_
    lookup={x["candidate_index"]:x["round"] for x in candidates}
    for c in calls:
        c["round"]=lookup[c["candidate_index"]]
    pd.DataFrame(candidates).to_csv(out/"candidate_trace.csv",index=False)
    pd.DataFrame(calls).to_csv(out/"optimizer_trace.csv",index=False)
    if first is not None:
        pd.DataFrame([x for x in candidates if x["round"]==first]).to_csv(out/"first_divergent_round_candidates.csv",index=False)
        pd.DataFrame([x for x in calls if x["round"]==first]).to_csv(out/"first_divergent_round_optimizers.csv",index=False)
    report=dict(profile_id=args.profile,sigma=args.sigma,first_divergent_round=first,
        first_divergent_observations=first_diffs.to_dict("records"),
        solver_calls_before_first_divergent_round=sum(x["round"]<first for x in calls) if first else len(calls),
        solver_calls_in_first_divergent_round=sum(x["round"]==first for x in calls) if first else 0,
        first_divergent_round_candidate_count=sum(x["round"]==first for x in candidates) if first else 0,
        versions=dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__,
                      pandas=pd.__version__,platform=platform.platform()),
        interpretation="Original archive lacks optimizer traces. Candidate and solver calls in the first divergent round are identified; exact first differing historical solver call cannot be proven.",
        research_validated=False)
    (out/"targeted_diagnostic.json").write_text(json.dumps(report,indent=2)+"\n")
    print("TARGETED_SOLVER_TRACE_COMPLETE",json.dumps(report))
if __name__=="__main__":
    main()

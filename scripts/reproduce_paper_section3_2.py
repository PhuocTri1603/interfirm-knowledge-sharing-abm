"""Reproduce the exact historical engine; collect observations only AFTER the gate passes.

Run with PYTHONPATH pointing to a checkout of original commit c614b86d9192a57fb402b4772b3c3bb6bf80b79f.
The original game module is imported unchanged. Candidate is wrapped to observe the
returned chosen plan, never to change the chosen plan or consume RNG.
"""
from __future__ import annotations
import argparse,csv,json,sys
from collections import defaultdict
from pathlib import Path
from math import fsum
import numpy as np
import pandas as pd
import interfirm_abm.game1_nine_strategy as game
from interfirm_abm.task_a6_market import approved_profiles
from interfirm_abm.task_a5_normalized import technology_for_profile

SOURCE="c614b86d9192a57fb402b4772b3c3bb6bf80b79f"
STRATEGIES=tuple(f"L3={a}|L4={b}" for a,b in game.strategy_ids())
ATOL=1e-7
RTOL=1e-9

def params():
    wage=.5/51.5
    return game.Game1Params(demand_intercept=2.,demand_slope=1./9.,
        wage=wage,rental=wage,adjustment_delta=.1,
        adoption_fee=.1*.5/20.,eta=.1,epsilon=.15,seed=11)

def compare(original,replica):
    cols=["profile_id","sigma","strategy_id","round"]
    a=original.sort_values(cols).reset_index(drop=True)
    b=replica.sort_values(cols).reset_index(drop=True)
    assert len(a)==len(b) and a[cols].equals(b[cols])
    results={}
    for field in ("output","price","profit","cumulative_profit","active_ai_count","adopted_count"):
        d=np.abs(a[field].to_numpy(dtype=float)-b[field].to_numpy(dtype=float))
        scale=np.maximum(np.abs(a[field].to_numpy(dtype=float)),np.abs(b[field].to_numpy(dtype=float)))
        fail=d>(ATOL+RTOL*scale)
        results[field]=dict(max_absolute=float(d.max()),n_mismatched=int(fail.sum()))
    results["action_mismatches"]=int((a.action!=b.action).sum())
    original_terminal=a[a["round"]==200].set_index(["profile_id","sigma","strategy_id"]).cumulative_profit
    reproduced_terminal=b[b["round"]==200].set_index(["profile_id","sigma","strategy_id"]).cumulative_profit
    results["max_terminal_profit_difference"]=float((original_terminal-reproduced_terminal).abs().max())
    def winner(df):
        return df[df["round"]==200].sort_values(
            ["profile_id","sigma","cumulative_profit","strategy_id"],
            ascending=[True,True,False,True]).groupby(["profile_id","sigma"]).first().strategy_id
    results["ranking_mismatches"]=int((winner(a)!=winner(b)).sum())
    first={}
    for field in ("output","price","profit","cumulative_profit","active_ai_count","adopted_count"):
        idx=np.flatnonzero(np.abs(a[field].to_numpy(dtype=float)-b[field].to_numpy(dtype=float))>
             (ATOL+RTOL*np.maximum(np.abs(a[field].to_numpy(dtype=float)),np.abs(b[field].to_numpy(dtype=float)))))
        if len(idx):
            i=int(idx[0]);first[field]=dict(key={k:str(a.at[i,k]) for k in cols},
                original=float(a.at[i,field]),reproduced=float(b.at[i,field]))
    results["first_mismatches"]=first
    results["pass"]=not (results["action_mismatches"] or results["ranking_mismatches"] or
                          any(results[k]["n_mismatched"] for k in
                              ("output","price","profit","cumulative_profit","active_ai_count","adopted_count")))
    return results

def replay(firms,sigma,p,instrument=False):
    original_candidate=game.candidate
    all_rows=[];task_rows=[];firm_rows=[]
    try:
        for firm in firms:
            if not instrument:
                result=game.run_game1(firm,sigma,p,rounds=200)
            else:
                tech=technology_for_profile(firm,sigma)
                queue=[]
                def observed_candidate(firm_,tech_,l3,l4,budget,price,previous,adopted,par,last_modes=None):
                    out=original_candidate(firm_,tech_,l3,l4,budget,price,previous,adopted,par,last_modes)
                    queue.append((l3,l4,budget,previous,adopted,out))
                    return out
                game.candidate=observed_candidate
                try:
                    result=game.run_game1(firm,sigma,p,rounds=200)
                finally:
                    game.candidate=original_candidate
                # candidate is called once per active strategy, in deterministic strategy/round order.
                k=0
                prior={sid:game.zero_plan() for sid in STRATEGIES}
                prior_modes={sid:(False,)*20 for sid in STRATEGIES}
                for rec in result["players"]:
                    sid=rec["strategy_id"];action=rec["action"];round_=rec["round"]
                    if action=="shutdown":
                        plan=game.zero_plan()
                        old=prior[sid];adopted=frozenset();new=frozenset()
                        modes=prior_modes[sid]
                        cost=game.adjustment(plan,old,p)
                        budget=0.
                    else:
                        l3,l4,budget,old,adopted,out=queue[k];k+=1
                        assert sid==f"L3={l3}|L4={l4}"
                        _,plan,q,cost,new,modes=out
                        assert abs(q-rec["output"])<1e-7
                    variable=p.wage*fsum(v.labor for v in plan)+p.rental*fsum(v.capital for v in plan)
                    adjust=game.adjustment(plan,old,p)
                    adoption=p.adoption_fee*len(new)
                    assert abs(cost-variable-adjust-adoption)<1e-7
                    q_check=tech.output_from_allocation(firm,list(plan))
                    assert abs(q_check-rec["output"])<1e-7
                    revenue=rec["price"]*rec["output"]
                    assert abs(revenue-cost-rec["profit"])<1e-7
                    labor=fsum(v.labor for v in plan)
                    capital=fsum(v.capital for v in plan)
                    assert labor<=firm.labor_endowment+1e-9
                    assert capital<=firm.capital_endowment+1e-9
                    firm_rows.append(dict(profile_id=firm.firm_id,sigma=sigma,strategy_id=sid,round=round_,
                        action=action,capacity_action_budget=budget,labor_used=labor,capital_used=capital,
                        labor_endowment=firm.labor_endowment,capital_endowment=firm.capital_endowment,
                        labor_utilization=labor/firm.labor_endowment if firm.labor_endowment else 0.,
                        capital_utilization=capital/firm.capital_endowment if firm.capital_endowment else 0.,
                        output=rec["output"],price=rec["price"],revenue=revenue,variable_cost=variable,
                        adjustment_cost=adjust,adoption_cost=adoption,total_cost=cost,profit=rec["profit"],
                        cumulative_profit=rec["cumulative_profit"],active_ai_count=rec["active_ai_count"],
                        adopted_count=rec["adopted_count"],newly_adopted_count=len(new)))
                    activity=firm.evaluate_allocation(list(plan))
                    for task,allocation in zip(firm.tasks,plan):
                        t=task.task_id
                        j=int(t[1:])-1
                        task_rows.append(dict(profile_id=firm.firm_id,sigma=sigma,strategy_id=sid,round=round_,
                            task_id=t,labor_productivity=task.labor_productivity,
                            capital_productivity=task.capital_productivity,
                            reference_activity=tech.reference[t],
                            normalized_activity=activity[t]/tech.reference[t],
                            labor_allocation=allocation.labor,capital_allocation=allocation.capital,
                            selected_mode="AI" if modes[j] else "labor",
                            ai_eligible=int(task.automation_eligible),
                            actual_ai_use=int(allocation.capital>1e-9),
                            new_ai_adoption=int(t in new),
                            mode_switch=int(modes[j]!=prior_modes[sid][j]) if action!="shutdown" else 0))
                    prior[sid]=plan
                    if action!="shutdown":
                        prior_modes[sid]=modes
                assert k==len(queue)
            for row in result["players"]:
                all_rows.append(dict(profile_id=firm.firm_id,sigma=sigma,**row))
    finally:
        game.candidate=original_candidate
    return pd.DataFrame(all_rows),pd.DataFrame(firm_rows),pd.DataFrame(task_rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--sigma",type=float,required=True,choices=(.5,1.,2.))
    ap.add_argument("--batch",type=int,required=True,choices=range(10))
    ap.add_argument("--archive",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    firms=approved_profiles()[a.batch*10:(a.batch+1)*10]
    assert len(firms)==10
    p=params()
    prefix=f"sigma_{a.sigma:g}_batch_{a.batch:02d}"
    original=pd.read_csv(Path(a.archive)/f"{prefix}_rounds.csv")
    # First run exact original engine, with NO instrumentation.
    replica,_,_=replay(firms,a.sigma,p,False)
    gate=compare(original,replica)
    gate.update(source_commit=SOURCE,seed=p.seed,parameters=p.__dict__,
        sigma=a.sigma,batch=a.batch,expected_rows=18000,observed_rows=len(replica),
        absolute_tolerance=ATOL,relative_tolerance=RTOL,
        reproduction_environment=dict(python=sys.version,numpy=np.__version__,
            scipy=__import__("scipy").__version__,pandas=pd.__version__),
        mechanism_interpretation_allowed=False,research_validated=False)
    (out/f"{prefix}_gate.json").write_text(json.dumps(gate,indent=2)+"\n")
    replica.to_csv(out/f"{prefix}_reproduced_rounds.csv",index=False)
    if not gate["pass"]:
        print("REPRODUCTION_GATE_FAILED",prefix,json.dumps(gate))
        return 2
    # A separate, instrumented execution must match the uninstrumented one too.
    instrumented,firm_rows,task_rows=replay(firms,a.sigma,p,True)
    second=compare(replica,instrumented)
    (out/f"{prefix}_instrumentation_gate.json").write_text(json.dumps(second,indent=2)+"\n")
    if not second["pass"]:
        print("INSTRUMENTATION_GATE_FAILED",prefix,json.dumps(second))
        return 3
    assert len(firm_rows)==18000 and len(task_rows)==360000
    firm_rows.to_csv(out/f"{prefix}_firm_mechanisms.csv",index=False)
    task_rows.to_csv(out/f"{prefix}_task_mechanisms.csv",index=False)
    print("REPRODUCTION_AND_INSTRUMENTATION_PASS",prefix)
    return 0
if __name__=="__main__":
    raise SystemExit(main())

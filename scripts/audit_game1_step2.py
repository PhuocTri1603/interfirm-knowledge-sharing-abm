"""Step-2 observational audit: selected task allocations, CES, AI and fee invariants."""
import argparse,csv
from pathlib import Path
from collections import defaultdict
from math import isfinite
import interfirm_abm.game1_nine_strategy as g
from interfirm_abm.task_a6_market import approved_profiles
from interfirm_abm.task_a5_normalized import technology_for_profile

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--profile-index",type=int,required=True)
    ap.add_argument("--sigma",type=float,required=True)
    ap.add_argument("--seed",type=int,default=11)
    ap.add_argument("--rounds",type=int,default=20)
    ap.add_argument("--out",default="results/game1_step2")
    args=ap.parse_args()
    firm=approved_profiles()[args.profile_index]
    tech=technology_for_profile(firm,args.sigma)
    p=g.Game1Params(2.,1./9.,.5/51.5,.5/51.5,.1,.1*.5/20.,.1,.15,args.seed)
    rows=[]; count=0
    original=g.candidate
    def observed(firm,tech,l3,l4,budget,price,previous,adopted,p,last_modes=None):
        nonlocal count
        score,plan,q,cost,new,modes=original(firm,tech,l3,l4,budget,price,previous,adopted,p,last_modes)
        activities=firm.evaluate_allocation(list(plan))
        assert len(plan)==20
        assert all(not (a.labor>0 and a.capital>0) for a in plan)
        assert all(a.capital==0 or t.automation_eligible for a,t in zip(plan,firm.tasks))
        assert sum(a.labor for a in plan)<=budget*firm.labor_endowment+1e-6
        assert sum(a.capital for a in plan)<=budget*firm.capital_endowment+1e-6
        assert isfinite(q) and q>=0 and abs(q-tech.output_index(activities))<1e-8
        expected={a.task_id for a in plan if a.capital>1e-9 and a.task_id not in adopted}
        assert set(new)==expected
        variable=p.wage*sum(a.labor for a in plan)+p.rental*sum(a.capital for a in plan)
        adjust=g.adjustment(plan,previous,p)
        assert abs(cost-variable-adjust-p.adoption_fee*len(new))<1e-7
        assert abs(score-(price*q-cost))<1e-7
        if l4=="no_automation": assert all(a.capital==0 for a in plan)
        for t,a in zip(firm.tasks,plan):
            rows.append(dict(profile=firm.firm_id,sigma=args.sigma,seed=args.seed,call=count,l3=l3,l4=l4,budget=budget,task=t.task_id,eligible=int(t.automation_eligible),labor=a.labor,capital=a.capital,activity=activities[t.task_id],active_ai=int(a.capital>1e-9),new_adoption=int(t.task_id in new),output=q,total_cost=cost))
        count+=1
        return score,plan,q,cost,new,modes
    g.candidate=observed
    try:
        result=g.run_game1(firm,args.sigma,p,rounds=args.rounds,audit=True)
    finally:
        g.candidate=original
    assert len(result["players"])==9*args.rounds
    assert len(rows)==count*20
    assert abs(tech.output_index(tech.reference)-1.)<1e-9
    path=Path(args.out);path.mkdir(parents=True,exist_ok=True)
    target=path/f"tasks_profile_{args.profile_index}_sigma_{args.sigma:g}_seed_{args.seed}.csv"
    with target.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(f"PASS task-level feasibility CES eligibility and fee accounting: {count} production calls, {len(rows)} task rows, {len(result['players'])} settled player rounds. Artifact {target}")
    print("LIMIT: selected plans checked; not proof of global optimum or causal AI effect.")
if __name__=="__main__": main()

"""Full 100-profile paired AI/no-AI audit with 20 vs 200 round horizons.

Observational wrapper only; core engine untouched. 20-round results are
prefixes of 200-round runs, not independently restarted simulations.
"""
import argparse,csv,sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_game1_ai_counterfactual import params,simulate
from interfirm_abm.task_a6_market import approved_profiles

def compute(firm,profile,sigma,seed,rounds):
    par=params(seed)
    ai=simulate(firm,sigma,par,rounds,False)["players"]
    no=simulate(firm,sigma,par,rounds,True)["players"]
    assert len(ai)==len(no)==9*rounds
    assert all(r["capital_used"]==0 and r["active_ai_count"]==0 and r["adoption_cost"]==0 for r in no)
    bykey={}
    for name,rows in (("ai",ai),("no",no)):
        for r in rows:
            key=(int(r["round"]),r["strategy_id"])
            assert name not in bykey.setdefault(key,{})
            bykey[key][name]=r
    assert len(bykey)==9*rounds
    out=[]
    for horizon in (20,200):
        totals=defaultdict(float)
        for (t,sid),pair in bykey.items():
            if t>horizon:continue
            x,b=pair["ai"],pair["no"]
            dq=x["output"]-b["output"];dp=x["price"]-b["price"]
            vals=dict(delta_profit=x["profit"]-b["profit"],delta_output=dq,
                delta_revenue=x["revenue"]-b["revenue"],
                delta_variable_cost=x["variable_cost"]-b["variable_cost"],
                delta_adjustment_cost=x["adjustment_cost"]-b["adjustment_cost"],
                delta_adoption_cost=x["adoption_cost"]-b["adoption_cost"],
                quantity_effect=b["price"]*dq,price_effect=b["output"]*dp,interaction_effect=dp*dq)
            assert abs(vals["delta_revenue"]-vals["quantity_effect"]-vals["price_effect"]-vals["interaction_effect"])<1e-7
            assert abs(vals["delta_profit"]-vals["delta_revenue"]+vals["delta_variable_cost"]+vals["delta_adjustment_cost"]+vals["delta_adoption_cost"])<1e-7
            for k,v in vals.items():totals[k]+=v
        out.append(dict(profile=firm.firm_id,profile_index=profile,sigma=sigma,seed=seed,horizon=horizon,**totals))
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--profile-index",type=int,required=True)
    p.add_argument("--out",default="results/game1_ai_full")
    a=p.parse_args()
    firms=approved_profiles()
    assert len(firms)==100,"Expected approved population of 100"
    assert 0<=a.profile_index<100
    rows=[]
    for sigma in (.5,1.,2.):
        for seed in (11,23,47):
            rows.extend(compute(firms[a.profile_index],a.profile_index,sigma,seed,200))
            print("PASS",a.profile_index,sigma,seed,flush=True)
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    path=out/f"profile_{a.profile_index:03d}.csv"
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print("PROFILE_COMPLETE",a.profile_index,"18 rows",flush=True)
if __name__=="__main__":main()

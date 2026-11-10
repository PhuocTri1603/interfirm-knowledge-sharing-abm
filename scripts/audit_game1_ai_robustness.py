"""Multi-profile, multi-seed AI/no-AI robustness using the unchanged engine.

Market-policy contrast, not a direct individual-firm AI effect.
"""
import argparse,csv
from pathlib import Path
from collections import defaultdict
from audit_game1_ai_counterfactual import params,simulate
from interfirm_abm.task_a6_market import approved_profiles

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--profile-index",type=int,required=True)
    p.add_argument("--sigma",type=float,choices=(.5,1.,2.),required=True)
    p.add_argument("--seed",type=int,required=True)
    p.add_argument("--rounds",type=int,default=20)
    p.add_argument("--out",default="results/game1_ai_robustness")
    a=p.parse_args()
    firm=approved_profiles()[a.profile_index]; par=params(a.seed)
    ai=simulate(firm,a.sigma,par,a.rounds,False)
    no=simulate(firm,a.sigma,par,a.rounds,True)
    assert len(ai["players"])==len(no["players"])==9*a.rounds
    assert all(r["capital_used"]==r["active_ai_count"]==r["adoption_cost"]==0 for r in no["players"])
    paired={}
    for name,result in (("ai",ai),("no",no)):
        for r in result["players"]:
            key=(r["round"],r["strategy_id"])
            paired.setdefault(key,{})[name]=r
    assert len(paired)==9*a.rounds
    total=defaultdict(float); rows=[]
    for (round_id,strategy_id),pair in sorted(paired.items()):
        x=pair["ai"];b=pair["no"]
        q0=b["output"];q1=x["output"];p0=b["price"];p1=x["price"]
        dq=q1-q0;dp=p1-p0
        d={"quantity_effect":p0*dq,"price_effect":q0*dp,"interaction_effect":dp*dq,
           "delta_revenue":x["revenue"]-b["revenue"],
           "delta_variable_cost":x["variable_cost"]-b["variable_cost"],
           "delta_adjustment_cost":x["adjustment_cost"]-b["adjustment_cost"],
           "delta_adoption_cost":x["adoption_cost"]-b["adoption_cost"],
           "delta_profit":x["profit"]-b["profit"],"delta_output":dq,
           "delta_capital":x["capital_used"]-b["capital_used"],
           "delta_labor":x["labor_used"]-b["labor_used"]}
        assert abs(d["delta_revenue"]-d["quantity_effect"]-d["price_effect"]-d["interaction_effect"])<1e-7
        assert abs(d["delta_profit"]-d["delta_revenue"]+d["delta_variable_cost"]+d["delta_adjustment_cost"]+d["delta_adoption_cost"])<1e-7
        rows.append(dict(profile=firm.firm_id,profile_index=a.profile_index,sigma=a.sigma,seed=a.seed,round=round_id,strategy_id=strategy_id,**d))
        for k,v in d.items():total[k]+=v
    prices={}
    for name,result in (("ai",ai),("no",no)):
        prices[name]={}
        for r in result["players"]:
            key=r["round"]
            if key in prices[name]:
                assert abs(prices[name][key]-r["price"])<1e-8
            prices[name][key]=r["price"]
    total["delta_market_price_sum"]=sum(prices["ai"][i]-prices["no"][i] for i in prices["ai"])
    summary=dict(profile=firm.firm_id,profile_index=a.profile_index,sigma=a.sigma,seed=a.seed,rounds=a.rounds,
       ai_active_task_rounds=sum(r["active_ai_count"] for r in ai["players"]),**total)
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    for filename,data in ((f"summary_p{a.profile_index}_s{a.sigma:g}_seed{a.seed}.csv",[summary]),
                          (f"rounds_p{a.profile_index}_s{a.sigma:g}_seed{a.seed}.csv",rows)):
        with (out/filename).open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    print("PASS robustness paired-market accounting",summary)
if __name__=="__main__":main()

"""Paired AI-policy intervention, with unchanged nine-strategy engine.

Treatment: original nine strategies.
Control: same nine slots and RNG seeds, but force L4= no_automation
for the six AI-enabled slots through a temporary candidate wrapper.
This is a market-level policy counterfactual, NOT a pure direct AI effect:
learning, prices, and competitor responses remain endogenous.
"""
import argparse,csv
from pathlib import Path
from collections import defaultdict
from math import isfinite
import interfirm_abm.game1_nine_strategy as g
from interfirm_abm.task_a6_market import approved_profiles
from interfirm_abm.task_a5_normalized import technology_for_profile

def params(seed):
    w=.5/51.5
    return g.Game1Params(2.,1./9.,w,w,.1,.1*.5/20.,.1,.15,seed)

def simulate(firm,sigma,p,rounds,disable_ai):
    original=g.candidate
    if disable_ai:
        def wrapper(firm,tech,l3,l4,budget,price,previous,adopted,p,last_modes=None):
            return original(firm,tech,l3,"no_automation",budget,price,previous,adopted,p,last_modes)
        g.candidate=wrapper
    try:
        return g.run_game1(firm,sigma,p,rounds=rounds,audit=True)
    finally:
        g.candidate=original

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--profile-index",type=int,required=True)
    a.add_argument("--sigma",type=float,choices=(.5,1.,2.),required=True)
    a.add_argument("--seed",type=int,default=11)
    a.add_argument("--rounds",type=int,default=20)
    a.add_argument("--out",default="results/game1_step2_ai")
    z=a.parse_args()
    firm=approved_profiles()[z.profile_index]; p=params(z.seed)
    baseline=simulate(firm,z.sigma,p,z.rounds,False)
    control=simulate(firm,z.sigma,p,z.rounds,True)
    assert len(baseline["players"])==len(control["players"])==9*z.rounds
    assert all(r["active_ai_count"]==0 and r["capital_used"]==0 and r["adoption_cost"]==0 for r in control["players"])
    panel=[]; grouped=defaultdict(dict)
    for name,result in (("ai_allowed",baseline),("ai_disabled",control)):
        for row in result["players"]:
            key=(row["round"],row["strategy_id"])
            grouped[key][name]=row
            panel.append(dict(profile=firm.firm_id,sigma=z.sigma,seed=z.seed,scenario=name,**row))
    comparisons=[]
    for (t,sid),pair in sorted(grouped.items()):
        b=pair["ai_allowed"];c=pair["ai_disabled"]
        comparisons.append(dict(profile=firm.firm_id,sigma=z.sigma,seed=z.seed,round=t,strategy_id=sid,
          delta_profit=b["profit"]-c["profit"],delta_output=b["output"]-c["output"],
          delta_price=b["price"]-c["price"],delta_capital=b["capital_used"]-c["capital_used"],
          delta_labor=b["labor_used"]-c["labor_used"],delta_ai_tasks=b["active_ai_count"],
          delta_adoption_cost=b["adoption_cost"]-c["adoption_cost"],
          delta_adjustment_cost=b["adjustment_cost"]-c["adjustment_cost"],
          delta_variable_cost=b["variable_cost"]-c["variable_cost"],
          delta_revenue=b["revenue"]-c["revenue"]))
        v=comparisons[-1]
        assert abs(v["delta_profit"]-(v["delta_revenue"]-v["delta_variable_cost"]-v["delta_adjustment_cost"]-v["delta_adoption_cost"]))<1e-7
    # Matched, fixed-state and fixed-price candidate comparisons. These do not
    # include dynamic learning, adoption histories, or market price feedback.
    tech=technology_for_profile(firm,z.sigma)
    static=[]
    for l3 in g.L3:
        for budget in g.BUDGETS:
            no=g.candidate(firm,tech,l3,"no_automation",budget,1.,g.zero_plan(),frozenset(),p)
            for l4 in ("cost_based","profit_based"):
                ai=g.candidate(firm,tech,l3,l4,budget,1.,g.zero_plan(),frozenset(),p)
                static.append(dict(profile=firm.firm_id,sigma=z.sigma,seed=z.seed,l3=l3,l4=l4,budget=budget,
                   fixed_price=1.,delta_predicted_profit=ai[0]-no[0],
                   delta_output=ai[2]-no[2],delta_cost=ai[3]-no[3],
                   ai_tasks=sum(x.capital>1e-9 for x in ai[1])))
    out=Path(z.out);out.mkdir(parents=True,exist_ok=True)
    for name,rows in (("round_panel",panel),("paired_round_effects",comparisons),("fixed_price_candidates",static)):
        path=out/f"{name}_profile_{z.profile_index}_sigma_{z.sigma:g}_seed_{z.seed}.csv"
        with path.open("w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        print("ARTIFACT",path)
    print("PASS AI-disabled control, matched market-level accounting and fixed-price candidate comparisons")
    print("SUMMARY",dict(profile=firm.firm_id,sigma=z.sigma,rounds=z.rounds,
      ai_tasks=sum(r["active_ai_count"] for r in baseline["players"]),
      delta_total_profit=sum(r["delta_profit"] for r in comparisons),
      delta_total_output=sum(r["delta_output"] for r in comparisons),
      delta_price_sum=sum(baseline["market"][i]["price"]-control["market"][i]["price"] for i in range(z.rounds))))
    print("LIMIT: total dynamic policy effect includes endogenous price and learning; static candidate differences are conditional, not globally optimal AI effects.")
if __name__=="__main__":main()

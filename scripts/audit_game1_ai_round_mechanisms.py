"""Observational per-round paired AI/no-AI mechanism audit; no engine modifications."""
import argparse,csv,sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_game1_ai_counterfactual import params,simulate
from interfirm_abm.task_a6_market import approved_profiles

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--profile-index",type=int,required=True)
    p.add_argument("--out",default="results/game1_ai_round_mechanisms")
    a=p.parse_args()
    firms=approved_profiles();assert len(firms)==100 and 0<=a.profile_index<100
    firm=firms[a.profile_index];rows=[]
    for sigma in (.5,1.,2.):
      for seed in (11,23,47):
        markets={}
        for scenario,disable in (("ai",False),("no",True)):
          result=simulate(firm,sigma,params(seed),200,disable)
          assert len(result["players"])==1800
          per_round=defaultdict(list)
          for r in result["players"]:per_round[int(r["round"])].append(r)
          for t in range(1,201):
            rr=per_round[t];assert len(rr)==9
            price=rr[0]["price"]
            assert all(abs(r["price"]-price)<1e-8 for r in rr)
            assert abs(sum(r["output"] for r in rr)-result["market"][t-1]["quantity"])<1e-7
            v=dict(price=price,quantity=sum(r["output"] for r in rr),
               revenue=sum(r["revenue"] for r in rr),
               variable_cost=sum(r["variable_cost"] for r in rr),
               adjustment_cost=sum(r["adjustment_cost"] for r in rr),
               adoption_cost=sum(r["adoption_cost"] for r in rr),
               profit=sum(r["profit"] for r in rr),
               labor=sum(r["labor_used"] for r in rr),
               capital=sum(r["capital_used"] for r in rr),
               ai_tasks=sum(r["active_ai_count"] for r in rr),
               active_players=sum(r["action"]!="shutdown" for r in rr))
            assert abs(v["revenue"]-price*v["quantity"])<1e-7
            assert abs(v["profit"]-v["revenue"]-(-v["variable_cost"]-v["adjustment_cost"]-v["adoption_cost"]))<1e-7
            markets[(scenario,t)]=v
        for t in range(1,201):
          x=markets[("ai",t)];b=markets[("no",t)]
          dq=x["quantity"]-b["quantity"];dp=x["price"]-b["price"]
          d={f"delta_{k}":x[k]-b[k] for k in x}
          d.update(quantity_effect=b["price"]*dq,price_effect=b["quantity"]*dp,interaction_effect=dp*dq,
                   ai_price=x["price"],no_price=b["price"],ai_quantity=x["quantity"],no_quantity=b["quantity"],
                   ai_capital=x["capital"],no_capital=b["capital"],ai_labor=x["labor"],no_labor=b["labor"],
                   ai_active_players=x["active_players"],no_active_players=b["active_players"])
          assert abs(d["delta_revenue"]-d["quantity_effect"]-d["price_effect"]-d["interaction_effect"])<1e-7
          assert abs(d["delta_profit"]-d["delta_revenue"]+d["delta_variable_cost"]+d["delta_adjustment_cost"]+d["delta_adoption_cost"])<1e-7
          rows.append(dict(profile=firm.firm_id,profile_index=a.profile_index,sigma=sigma,seed=seed,round=t,**d))
        print("PASS",a.profile_index,sigma,seed,flush=True)
    assert len(rows)==1800
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    with (out/f"profile_{a.profile_index:03d}.csv").open("w",newline="") as f:
      w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print("PROFILE_COMPLETE",a.profile_index,len(rows),flush=True)
if __name__=="__main__":main()

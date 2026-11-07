"""A6 unilateral causal intervention screen, 12 profiles x 2 contrasts x 2 slots.

Treatment is assigned to a fixed player slot. All other 255 slots retain
identical strategies and RNG seeds; their choices respond endogenously.
Within-market counterfactual effects are model-based, not real-world causality.
"""
import csv
import json
from math import fsum
from pathlib import Path
from statistics import mean
from interfirm_abm.task_a6_market import approved_profiles,approved_d1_d2_parameters,run_a6_market
from interfirm_abm.task_l34_economics import L34Parameters
from interfirm_abm.task_strategy_engine import strategy_roster

OUT=Path("artifacts/game1_a6_causal_intervention")
OUT.mkdir(parents=True,exist_ok=True)
profiles=approved_profiles()
indices=(0,9,18,27,36,45,54,63,72,81,90,99)
params=approved_d1_d2_parameters(theta=1,kappa=.5,elasticity=1,adaptive_lambda=.5,seed=11)
l34=L34Parameters(capacity_ratio=2.,adjustment_unit_cost=.001,efficiency_gain=.2,adoption_fee=.001)
roster=strategy_roster()
# Choose two different L3/L4 blocks, fixed across all 12 profiles.
slots={
 "L6": [x.strategy_id for x in roster if x.L5=="adaptive" and x.L6=="imitation"][:2],
 "L5": [x.strategy_id for x in roster if x.L5=="competitive" and x.L6=="optimization"][:2],
}
assert all(len(x)==2 for x in slots.values())
rows=[]
for index in indices:
    firm=profiles[index]
    for layer,first,second in (("L6","imitation","optimization"),("L5","competitive","cournot")):
        for sid in slots[layer]:
            runs={}
            for arm in (first,second):
                result=run_a6_market(firm,1.,params,l34_parameters=l34,rounds=200,
                    mechanism_overrides={sid:{layer:arm}})
                assert not result["research_validated"] and len(result["ranking"])==256
                payoff=dict(result["ranking"])
                prices=[m["price"] for m in result["market"]]
                actions=[p["action"] for p in result["players"] if p["strategy_id"]==sid]
                runs[arm]=dict(target_profit=payoff[sid],
                    other_profit=fsum(v for k,v in payoff.items() if k!=sid),
                    market_profit=fsum(payoff.values()),mean_price=mean(prices),
                    actions=actions)
            a,b=runs[first],runs[second]
            rows.append(dict(profile_id=firm.firm_id,layer=layer,target_slot=sid,
                control=first,treatment=second,
                target_profit_control=a["target_profit"],
                target_profit_treatment=b["target_profit"],
                treatment_minus_control_target=b["target_profit"]-a["target_profit"],
                treatment_minus_control_others=b["other_profit"]-a["other_profit"],
                treatment_minus_control_market=b["market_profit"]-a["market_profit"],
                treatment_minus_control_mean_price=b["mean_price"]-a["mean_price"],
                changed_action_rounds=sum(x!=y for x,y in zip(a["actions"],b["actions"]))))
    print("A6_CAUSAL_PROGRESS="+json.dumps(dict(completed=len(rows)//4,total=12,
        profile=firm.firm_id)),flush=True)
assert len(rows)==48
with (OUT/"unilateral_paired_effects.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary={}
for layer in ("L5","L6"):
    subset=[r for r in rows if r["layer"]==layer]
    summary[layer]=dict(pairs=len(subset),
        target_mean_effect=mean(r["treatment_minus_control_target"] for r in subset),
        others_mean_effect=mean(r["treatment_minus_control_others"] for r in subset),
        market_mean_effect=mean(r["treatment_minus_control_market"] for r in subset),
        mean_changed_action_rounds=mean(r["changed_action_rounds"] for r in subset),
        positive_target_effects=sum(r["treatment_minus_control_target"]>1e-9 for r in subset),
        negative_target_effects=sum(r["treatment_minus_control_target"]< -1e-9 for r in subset),
        near_zero_target_effects=sum(abs(r["treatment_minus_control_target"])<=1e-9 for r in subset))
report=dict(research_validated=False,scope="12 profiles, sigma 1, seed 11, two fixed slots per contrast",
    treatment_definition="optimization minus imitation (L6); cournot minus competitive (L5)",
    identification="paired unilateral interventions in same initial 256-slot market; other players respond endogenously",
    caveat="simulation-specific intervention effects, not empirical causal inference",
    summary=summary)
(OUT/"summary.json").write_text(json.dumps(report,indent=2))
print("A6_CAUSAL_SUMMARY="+json.dumps(report,sort_keys=True),flush=True)

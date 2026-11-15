"""Cournot duopoly adapter using EXACT A6 production, costs and AI candidate.
Requires parent repository on PYTHONPATH. No reimplementation of A6 equations.
This is a new two-player market design, not an unchanged A6 experiment.
"""
from __future__ import annotations
import argparse
import csv
import json
from hashlib import sha256
from pathlib import Path
from random import Random
from math import fsum

from interfirm_abm.task_based_firm import load_approved_population
from interfirm_abm.game1_nine_strategy import (
    ACTIONS, BUDGETS, Game1Params, adjustment, candidate, zero_plan
)
from interfirm_abm.task_a5_normalized import technology_for_profile

STRATEGIES = ("uniform", "productivity", "cost_adjusted")
SIGMAS = (0.5, 1.0, 2.0)

def state(seed, firm_id, player, strategy):
    digest = sha256(f"{seed}|{firm_id}|{player}|{strategy}".encode()).digest()
    return dict(strategy=strategy, rng=Random(int.from_bytes(digest[:8], "big")),
                values={a: 0. for a in ACTIONS}, previous=zero_plan(),
                modes=(False,)*20, adopted=frozenset(), cumulative_profit=0.)

def action_for(s, p):
    rng=s["rng"]
    return rng.choice(ACTIONS) if rng.random() < p.epsilon else max(
        ACTIONS, key=lambda a:(s["values"][a], -ACTIONS.index(a)))

def play(firm, sigma, p, strategy_a, strategy_b, rounds, ai_policy):
    tech=technology_for_profile(firm, sigma)
    players=[state(p.seed, firm.firm_id, "A", strategy_a),
             state(p.seed, firm.firm_id, "B", strategy_b)]
    prior_price=1.0
    records=[]
    for t in range(1, rounds+1):
        choices=[]
        for s in players:
            action=action_for(s,p)
            if action=="shutdown":
                plan=zero_plan()
                cost=adjustment(plan,s["previous"],p)
                choice=(-cost,plan,0.,cost,frozenset(),s["modes"])
            else:
                choice=candidate(firm,tech,s["strategy"],ai_policy,
                    BUDGETS[ACTIONS.index(action)-1],prior_price,
                    s["previous"],s["adopted"],p,s["modes"])
            choices.append((action,choice))
        quantity=fsum(ch[2] for _,ch in choices)
        price=max(0.,p.demand_intercept-p.demand_slope*quantity)
        for player,s,(action,choice) in zip(("A","B"),players,choices):
            _,plan,q,cost,new,modes=choice
            profit=price*q-cost
            s["values"][action]+=p.eta*(profit-s["values"][action])
            s["cumulative_profit"]+=profit
            s["previous"]=plan
            if action!="shutdown":
                s["modes"]=modes
            s["adopted"] |= new
            records.append(dict(profile_id=firm.firm_id,sigma=sigma,
                strategy_a=strategy_a,strategy_b=strategy_b,
                player=player,round=t,action=action,output=q,
                price=price,market_quantity=quantity,
                profit=profit,cumulative_profit=s["cumulative_profit"],
                active_ai_count=sum(x.capital>1e-9 for x in plan),
                adopted_count=len(s["adopted"])))
        prior_price=price
    return records

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--profiles",required=True)
    ap.add_argument("--tasks",required=True)
    ap.add_argument("--params-json",required=True,
                    help="JSON containing exact approved A6 Game1Params; never guess values")
    ap.add_argument("--out",default="results/cournot_a6_three_allocation.csv")
    ap.add_argument("--profile-id",default="F001",help="Single frozen technology profile")
    ap.add_argument("--rounds",type=int,default=200)
    ap.add_argument("--sigma",type=float,choices=SIGMAS,default=1.0)
    ap.add_argument("--ai-policy",choices=("profit_based","cost_based","no_automation"),
                    default="profit_based")
    args=ap.parse_args()
    if args.rounds<1:
        ap.error("rounds must be positive")
    p=Game1Params(**json.loads(Path(args.params_json).read_text()))
    firms=[f for f in load_approved_population(args.profiles,args.tasks) if f.firm_id==args.profile_id]
    if len(firms)!=1:
        ap.error("profile-id must identify exactly one approved profile")
    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",newline="") as f:
        writer=None
        for firm in firms:
            for sigma in (args.sigma,):
                for a in STRATEGIES:
                    for b in STRATEGIES:
                        records=play(firm,sigma,p,a,b,args.rounds,args.ai_policy)
                        if writer is None:
                            writer=csv.DictWriter(f,fieldnames=records[0].keys())
                            writer.writeheader()
                        writer.writerows(records)
    print(f"Saved {out}: {len(firms)*9} markets, {args.rounds} rounds, 2 firms")

if __name__=="__main__":
    main()

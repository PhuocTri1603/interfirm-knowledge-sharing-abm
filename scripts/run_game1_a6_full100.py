"""Full 100-configuration Game 1 A6 run; postprocess payoffs only.

Uses exactly the illustrative parameterization of scripts/run_game1_a6_pilot.py.
No modifications to market rules, strategy definitions or calibration.
"""
import csv
import json
from collections import Counter
from math import fsum, isclose
from pathlib import Path
from statistics import mean

from interfirm_abm.task_a6_market import A6Parameters, approved_profiles, run_a6_market
from interfirm_abm.task_l34_economics import L34Parameters

OUT = Path("artifacts/game1_a6_full100")
OUT.mkdir(parents=True, exist_ok=True)
PROFILES = approved_profiles()
assert len(PROFILES) == 100 and len({f.firm_id for f in PROFILES}) == 100
PARAMS = A6Parameters(demand_intercept=10.0, demand_slope=0.01,
                      epsilon=0.15, temperature=1.0,
                      imitation_probability=0.5, seed=11,
                      wage=0.001, rental=0.001)
L34 = L34Parameters(capacity_ratio=2.0, adjustment_unit_cost=0.001,
                    efficiency_gain=0.2, adoption_fee=0.001)

def writer(name, fields):
    f = (OUT / name).open("w", newline="", encoding="utf-8")
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    return f,w

market_file, market_writer = writer("market_payoff_by_round.csv",[
    "profile_id","round","market_payoff","cumulative_market_payoff","price","quantity"])
ranking_file, ranking_writer = writer("strategy_payoff_by_configuration.csv",[
    "profile_id","strategy_id","cumulative_payoff","rank","is_winner"])
summary_file, summary_writer = writer("configuration_summary.csv",[
    "profile_id","winner_count","winning_payoff","winner_ids",
    "market_payoff_round_1","market_payoff_round_200",
    "mean_market_payoff_first_20","mean_market_payoff_last_20",
    "delta_last20_minus_first20","improved_by_window_mean",
    "total_market_payoff_200_rounds","min_market_payoff","max_market_payoff"])
wincount=Counter()
all_strategies=set()
summaries=[]
for index, firm in enumerate(PROFILES, 1):
    result=run_a6_market(firm,1.0,PARAMS,l34_parameters=L34,rounds=200)
    assert not result["research_validated"]
    assert len(result["players"])==51200 and len(result["market"])==200 and len(result["ranking"])==256
    assert len({sid for sid,_ in result["ranking"]})==256
    all_strategies.update(sid for sid,_ in result["ranking"])
    # Check market accounting against the individual realized profits.
    payoff_by_round={}
    for row in result["players"]:
        t=row["round"]
        payoff_by_round.setdefault(t,[]).append(row["profit"])
    running=0.0
    flows=[]
    for m in result["market"]:
        t=m["round"]
        assert len(payoff_by_round[t])==256
        flow=fsum(payoff_by_round[t])
        assert isclose(flow,m["profit"],rel_tol=1e-9,abs_tol=1e-7)
        running+=flow
        flows.append(flow)
        market_writer.writerow(dict(profile_id=firm.firm_id,round=t,market_payoff=flow,
            cumulative_market_payoff=running,price=m["price"],quantity=m["quantity"]))
    assert isclose(running,fsum(p for _,p in result["ranking"]),rel_tol=1e-9,abs_tol=1e-6)
    top=result["ranking"][0][1]
    winners=[sid for sid,p in result["ranking"] if isclose(p,top,rel_tol=1e-12,abs_tol=1e-8)]
    for sid in winners:
        wincount[sid]+=1
    for sid,p in result["ranking"]:
        rank=1+sum(other > p+1e-8 for _,other in result["ranking"])
        ranking_writer.writerow(dict(profile_id=firm.firm_id,strategy_id=sid,
            cumulative_payoff=p,rank=rank,is_winner=int(sid in winners)))
    first20=mean(flows[:20])
    last20=mean(flows[-20:])
    summary=dict(profile_id=firm.firm_id,winner_count=len(winners),winning_payoff=top,
        winner_ids=";".join(winners),market_payoff_round_1=flows[0],
        market_payoff_round_200=flows[-1],mean_market_payoff_first_20=first20,
        mean_market_payoff_last_20=last20,delta_last20_minus_first20=last20-first20,
        improved_by_window_mean=int(last20>first20),
        total_market_payoff_200_rounds=running,min_market_payoff=min(flows),
        max_market_payoff=max(flows))
    summary_writer.writerow(summary)
    summaries.append(summary)
    if index%10==0 or index==1:
        print("A6_FULL100_PROGRESS="+json.dumps({"completed":index,"total":100,
            "last_profile":firm.firm_id,"last_market_payoff":running}),flush=True)
for f in (market_file,ranking_file,summary_file):
    f.close()
assert len(summaries)==100 and len(all_strategies)==256
report={
    "experiment":"Game1_A6_100_configurations_256_players_200_rounds",
    "research_validated":False,
    "calibration_status":"illustrative_only_not_researcher_approved",
    "parameters_a6":vars(PARAMS),"parameters_l34":vars(L34),
    "sigma":1.0,"seed":11,"configurations":100,"players_per_configuration":256,
    "rounds":200,"firm_round_observations":5120000,
    "configuration_count_improved_by_window_mean":sum(x["improved_by_window_mean"] for x in summaries),
    "configuration_count_not_improved_by_window_mean":sum(not x["improved_by_window_mean"] for x in summaries),
    "mean_change_last20_minus_first20":mean(x["delta_last20_minus_first20"] for x in summaries),
    "mean_first20_market_payoff":mean(x["mean_market_payoff_first_20"] for x in summaries),
    "mean_last20_market_payoff":mean(x["mean_market_payoff_last_20"] for x in summaries),
    "sum_market_payoff_all_configurations":fsum(x["total_market_payoff_200_rounds"] for x in summaries),
    "mean_market_payoff_200_rounds_per_configuration":mean(x["total_market_payoff_200_rounds"] for x in summaries),
    "winning_strategy_frequency":dict(sorted(wincount.items(),key=lambda x:(-x[1],x[0]))),
    "configuration_count_with_multiple_winners":sum(x["winner_count"]>1 for x in summaries),
    "limits":["100 configurations are alternative markets, not simultaneous firms",
              "single seed and sigma; not stochastic robustness",
              "sum of firm profits is not social welfare",
              "cumulative market payoff is an accounting sum; first-20 versus last-20 compares flow performance"]
}
(OUT/"full100_summary.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print("A6_FULL100_SUMMARY="+json.dumps(report,sort_keys=True),flush=True)

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
player_records=[]
per_strategy={}

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
    first_round = {row["strategy_id"]: row["profit"] for row in result["players"] if row["round"] == 1}
    final_round = {row["strategy_id"]: row["profit"] for row in result["players"] if row["round"] == 200}
    assert len(first_round) == len(final_round) == 256
    for sid,p in result["ranking"]:
        record = dict(profile_id=firm.firm_id, strategy_id=sid, cumulative_payoff=p,
                      payoff_round_1=first_round[sid], payoff_round_200=final_round[sid],
                      delta_payoff=final_round[sid]-first_round[sid],
                      is_winner=int(sid in winners))
        player_records.append(record)
        per_strategy.setdefault(sid, []).append(record)
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
assert len(player_records)==25600 and all(len(v)==100 for v in per_strategy.values())
def top(rows, key, n=10):
    return sorted(rows, key=lambda r:(-r[key], r.get("strategy_id",""),r.get("profile_id","")))[:n]
def write_table(name, rows, fields):
    with (OUT/name).open("w", newline="", encoding="utf-8") as handle:
        writer=csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
write_table("player_endpoint_delta_by_configuration.csv", player_records,
    ["profile_id","strategy_id","cumulative_payoff","payoff_round_1",
     "payoff_round_200","delta_payoff","is_winner"])
strategy_summary=[]
for sid, records in per_strategy.items():
    total=fsum(r["cumulative_payoff"] for r in records)
    avg=total/100
    avg_delta=mean(r["delta_payoff"] for r in records)
    strategy_summary.append(dict(strategy_id=sid, winning_configurations=wincount[sid],
        total_cumulative_payoff=total, mean_cumulative_payoff=avg,
        mean_delta_payoff=avg_delta,
        positive_delta_configurations=sum(r["delta_payoff"]>0 for r in records),
        minimum_cumulative_payoff=min(r["cumulative_payoff"] for r in records),
        maximum_cumulative_payoff=max(r["cumulative_payoff"] for r in records)))
write_table("strategy_r1_r2_r3_r5_summary.csv",strategy_summary,
    ["strategy_id","winning_configurations","total_cumulative_payoff",
     "mean_cumulative_payoff","mean_delta_payoff","positive_delta_configurations",
     "minimum_cumulative_payoff","maximum_cumulative_payoff"])
r1=top(player_records,"cumulative_payoff")
r2=top(strategy_summary,"winning_configurations")
r3=top(player_records,"delta_payoff")
r3_average=top(strategy_summary,"mean_delta_payoff")
r4=top(summaries,"total_market_payoff_200_rounds")
r5=top(strategy_summary,"mean_cumulative_payoff")
results=dict(
    R1_highest_individual_cumulative_payoff=r1,
    R2_most_winning_strategies=r2,
    R3_largest_individual_endpoint_delta=r3,
    R3_largest_mean_endpoint_delta_across_configurations=r3_average,
    R4_highest_total_market_payoff_configurations=r4,
    R5_highest_mean_cumulative_payoff_strategies=r5,
    endpoint_delta_definition="realized firm payoff round 200 minus realized firm payoff round 1",
    mean_endpoint_delta_across_all_player_configurations=mean(r["delta_payoff"] for r in player_records),
    count_positive_individual_endpoint_deltas=sum(r["delta_payoff"]>0 for r in player_records),
    count_negative_individual_endpoint_deltas=sum(r["delta_payoff"]<0 for r in player_records))
(OUT/"r1_r5_analysis.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
print("A6_R1_R5_RESULTS="+json.dumps(results,sort_keys=True),flush=True)

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

"""Full 100-profile fixed-output/fixed-cost revaluation from frozen archive.

Accounting only: no game engine call, no new market clearing, no causal mediation claim.
"""
import argparse,csv,json,math,zipfile
from collections import defaultdict
from io import TextIOWrapper

SIGMAS=("0.5","1","2")
PAIRS=(("1","2"),("0.5","1"),("0.5","2"))
TOL=1e-8

def read_archive(path):
    data={}
    with zipfile.ZipFile(path) as z:
        for sigma in SIGMAS:
            for batch in range(10):
                name=f"sigma_{sigma}_batch_{batch:02d}_rounds.csv"
                with z.open(name) as fh:
                    for row in csv.DictReader(TextIOWrapper(fh,encoding="utf-8")):
                        profile=row["profile_id"];round_=int(row["round"]);sid=row["strategy_id"]
                        key=(profile,sigma,round_,sid)
                        assert key not in data
                        q=float(row["output"]);p=float(row["price"]);profit=float(row["profit"])
                        assert all(map(math.isfinite,(q,p,profit))) and q>=0 and p>=0
                        data[key]=(p,q,p*q-profit,profit)
    assert len(data)==540000
    profiles=sorted({k[0] for k in data})
    strategies=sorted({k[3] for k in data})
    assert len(profiles)==100 and len(strategies)==9
    assert all(len([1 for k in data if k[0]==f and k[1]==s])==1800 for f in profiles for s in SIGMAS)
    return data,profiles,strategies

def winner(profits):
    return sorted(profits,key=lambda s:(-profits[s],s))[0]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--archive",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    from pathlib import Path
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    data,profiles,strategies=read_archive(args.archive)
    records=[];ranking=[];max_error=0.;max_price_spread=0.
    for profile in profiles:
        for old,new in PAIRS:
            totals=defaultdict(lambda:defaultdict(float))
            for round_ in range(1,201):
                old_prices=[];new_prices=[];old_q=0.;new_q=0.
                for sid in strategies:
                    p0,q0,c0,pi0=data[(profile,old,round_,sid)]
                    p1,q1,c1,pi1=data[(profile,new,round_,sid)]
                    old_prices.append(p0);new_prices.append(p1)
                    old_q+=q0;new_q+=q1
                    quantity=p0*(q1-q0);price=(p1-p0)*q1;cost=c1-c0
                    delta=pi1-pi0;cf=quantity-cost
                    error=abs(delta-cf-price)
                    max_error=max(max_error,error)
                    assert error<TOL
                    t=totals[sid]
                    for key,value in (("delta_profit",delta),("fixed_price_profit_change",cf),("price_component",price),("quantity_component",quantity),("cost_change",cost),("baseline_profit",pi0),("target_profit",pi1),("counterfactual_profit",p0*q1-c1),("symmetric_price",(p1-p0)*(q0+q1)/2)):
                        t[key]+=value
                max_price_spread=max(max_price_spread,max(old_prices)-min(old_prices),max(new_prices)-min(new_prices))
                assert max(old_prices)-min(old_prices)<TOL and max(new_prices)-min(new_prices)<TOL
                assert abs(p0-max(0.,2.-old_q/9.))<TOL
                assert abs(p1-max(0.,2.-new_q/9.))<TOL
            def aggregate(group):
                result=defaultdict(float)
                for t in group.values():
                    for key,val in t.items():result[key]+=val
                return dict(result)
            totals["ALL_PLAYERS"]=aggregate(totals)
            for sid,t in sorted(totals.items()):
                records.append(dict(profile=profile,reference_sigma=old,target_sigma=new,strategy_id=sid,**t))
            o=winner({s:totals[s]["baseline_profit"] for s in strategies})
            n=winner({s:totals[s]["target_profit"] for s in strategies})
            cf=winner({s:totals[s]["counterfactual_profit"] for s in strategies})
            # margins indicate near-ties; do not silently interpret numerical ties as robust changes.
            def margin(field):
                vals=sorted((totals[s][field] for s in strategies),reverse=True)
                return vals[0]-vals[1]
            ranking.append(dict(profile=profile,reference_sigma=old,target_sigma=new,baseline_winner=o,target_winner=n,fixed_price_winner=cf,observed_winner_changed=int(o!=n),repricing_changes_target_winner=int(cf!=n),baseline_winner_margin=margin("baseline_profit"),target_winner_margin=margin("target_profit"),counterfactual_winner_margin=margin("counterfactual_profit")))
    assert max_price_spread<TOL
    for filename,rows in (("full100_revaluation_summary.csv",records),("full100_rankings.csv",ranking)):
        with (out/filename).open("w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    report={"source":"frozen 540000-row original archive","profiles":len(profiles),"strategies":len(strategies),"rounds":200,"sigma_pairs":[list(p) for p in PAIRS],"max_identity_error":max_error,"max_within_market_price_spread":max_price_spread,"economic_engine_invoked":False,"research_validated":False,"causal_mediation_identified":False,"results":{}}
    for old,new in PAIRS:
        market=[r for r in records if r["reference_sigma"]==old and r["target_sigma"]==new and r["strategy_id"]=="ALL_PLAYERS"]
        rank=[r for r in ranking if r["reference_sigma"]==old and r["target_sigma"]==new]
        report["results"][f"{old}->{new}"]={"price_component_negative_profiles":sum(r["price_component"] < -TOL for r in market),"fixed_price_profit_positive_profiles":sum(r["fixed_price_profit_change"]>TOL for r in market),"observed_profit_positive_profiles":sum(r["delta_profit"]>TOL for r in market),"observed_profit_negative_profiles":sum(r["delta_profit"]< -TOL for r in market),"observed_winner_changes":sum(r["observed_winner_changed"] for r in rank),"repricing_changes_target_winner":sum(r["repricing_changes_target_winner"] for r in rank),"totals":{k:math.fsum(r[k] for r in market) for k in ("delta_profit","fixed_price_profit_change","price_component","quantity_component","cost_change","symmetric_price")}}
    (out/"full100_report.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()

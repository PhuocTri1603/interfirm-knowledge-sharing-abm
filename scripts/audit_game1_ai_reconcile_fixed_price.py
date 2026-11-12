"""Compare two completed CI runs and calculate ex-post fixed-price decomposition.

No simulations, no engine edits, no policy reoptimization. Uses raw saved
per-profile CSVs from GitHub Actions runs 42826231816 and 43036152839.
"""
import argparse,csv,glob,math
from collections import defaultdict,Counter
from pathlib import Path

NUMERIC=("delta_profit","delta_revenue","delta_variable_cost","delta_adjustment_cost","delta_adoption_cost","delta_quantity","quantity_effect","price_effect","interaction_effect")
def read_rows(pattern):
    paths=glob.glob(pattern,recursive=True)
    assert len(paths)==100,f"Expected 100 profile CSVs; got {len(paths)} for {pattern}"
    rows=[]
    for p in paths:
        with open(p,newline="") as f:rows.extend(csv.DictReader(f))
    return rows

def key(r,horizon=None):
    return (int(r["profile_index"]),float(r["sigma"]),int(r["seed"]),int(r["horizon"]) if horizon is None else horizon)

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--full",default="results/game1_ai_mechanism_reconcile/full/**/profile_*.csv")
    a.add_argument("--rounds",default="results/game1_ai_mechanism_reconcile/rounds/**/profile_*.csv")
    a.add_argument("--out",default="results/game1_ai_mechanism_reconcile/aggregate")
    args=a.parse_args()
    full=read_rows(args.full);rounds=read_rows(args.rounds)
    assert len(full)==1800 and len(rounds)==180000,(len(full),len(rounds))
    expected={(i,s,seed,h) for i in range(100) for s in (.5,1.,2.) for seed in (11,23,47) for h in (20,200)}
    old={}
    for r in full:
        k=key(r);assert k not in old;old[k]=r
    assert set(old)==expected
    totals=defaultdict(lambda:defaultdict(float))
    counts=Counter()
    price_rows=[]
    for r in rounds:
        i,s,seed,t=int(r["profile_index"]),float(r["sigma"]),int(r["seed"]),int(r["round"])
        assert 0<=i<100 and s in (.5,1.,2.) and seed in (11,23,47) and 1<=t<=200
        assert abs(float(r["delta_profit"])-float(r["delta_revenue"])+float(r["delta_variable_cost"])+float(r["delta_adjustment_cost"])+float(r["delta_adoption_cost"]))<1e-6
        assert abs(float(r["delta_revenue"])-float(r["quantity_effect"])-float(r["price_effect"])-float(r["interaction_effect"]))<1e-6
        # Hold each observed firm's quantity and costs fixed; price is no-AI market price.
        fixed=float(r["quantity_effect"])-float(r["delta_variable_cost"])-float(r["delta_adjustment_cost"])-float(r["delta_adoption_cost"])
        feedback=float(r["price_effect"])+float(r["interaction_effect"])
        actual=float(r["delta_profit"])
        assert math.isclose(actual,fixed+feedback,rel_tol=1e-9,abs_tol=1e-7)
        price_rows.append(dict(profile_index=i,sigma=s,seed=seed,round=t,
          delta_profit_actual=actual,delta_profit_fixed_noai_price=fixed,
          price_feedback=feedback,quantity_effect=float(r["quantity_effect"]),
          price_effect=float(r["price_effect"]),interaction_effect=float(r["interaction_effect"]),
          delta_variable_cost=float(r["delta_variable_cost"]),
          delta_capital=float(r["delta_capital"]),delta_labor=float(r["delta_labor"]),
          delta_market_price=float(r["delta_price"]),delta_market_quantity=float(r["delta_quantity"])))
        for h in (20,200):
            if t<=h:
                k=(i,s,seed,h);counts[k]+=1
                for c in NUMERIC:totals[k][c]+=float(r[c])
                totals[k]["fixed"]+=fixed;totals[k]["feedback"]+=feedback
    assert set(counts)==expected and all(counts[k]==k[3] for k in expected)
    compare=[];summary=defaultdict(list)
    for k in sorted(expected):
        r=old[k];v=totals[k];i,s,seed,h=k
        d={c:v[c]-float(r[c] if c!="delta_quantity" else r["delta_output"]) for c in NUMERIC}
        x=dict(profile_index=i,sigma=s,seed=seed,horizon=h,
          prior_delta_profit=float(r["delta_profit"]),round_delta_profit=v["delta_profit"],
          error_profit=d["delta_profit"],abs_error_profit=abs(d["delta_profit"]),
          relative_error_profit=abs(d["delta_profit"])/max(1.,abs(float(r["delta_profit"]))),
          fixed_price_profit=v["fixed"],price_feedback=v["feedback"],
          sign_prior=("+" if float(r["delta_profit"])>1e-8 else "-" if float(r["delta_profit"])< -1e-8 else "0"),
          sign_round=("+" if v["delta_profit"]>1e-8 else "-" if v["delta_profit"]< -1e-8 else "0"),
          **{"error_"+c:d[c] for c in NUMERIC if c!="delta_profit"})
        x["sign_changed"]=x["sign_prior"]!=x["sign_round"]
        compare.append(x);summary[h].append(x)
    periods=defaultdict(list)
    for r in price_rows:
        period="early_1_20" if r["round"]<=20 else "middle_21_100" if r["round"]<=100 else "late_101_200"
        periods[period].append(r)
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    def write(name,rows):
        with (out/name).open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    write("reproducibility_1800_cases.csv",compare)
    write("fixed_price_180000_market_rounds.csv",price_rows)
    write("fixed_price_900_pairs_200round.csv",[dict(profile_index=i,sigma=s,seed=seed,
         actual_profit=totals[(i,s,seed,200)]["delta_profit"],
         fixed_price_profit=totals[(i,s,seed,200)]["fixed"],
         price_feedback=totals[(i,s,seed,200)]["feedback"]) for i in range(100) for s in (.5,1.,2.) for seed in (11,23,47)])
    periods_out=[]
    for period,rs in sorted(periods.items()):
        periods_out.append(dict(period=period,n=len(rs),**{c:sum(float(r[c]) for r in rs)/len(rs) for c in
          ("delta_profit_actual","delta_profit_fixed_noai_price","price_feedback","quantity_effect","price_effect","interaction_effect","delta_variable_cost","delta_capital","delta_labor","delta_market_price","delta_market_quantity")}))
    write("fixed_price_by_period.csv",periods_out)
    for h,rr in summary.items():
        print("REPRO",h,"n",len(rr),"changed_sign",sum(x["sign_changed"] for x in rr),
            "max_abs_error",max(x["abs_error_profit"] for x in rr),
            "mean_error",sum(x["error_profit"] for x in rr)/len(rr),
            "mean_abs_error",sum(x["abs_error_profit"] for x in rr)/len(rr))
        print("TOP10_DISCREPANCIES",h,[(x["profile_index"],x["sigma"],x["seed"],round(x["error_profit"],7)) for x in sorted(rr,key=lambda x:-x["abs_error_profit"])[:10]])
    for r in periods_out:print("FIXED_PRICE_PERIOD",r)
    print("PASS completeness 1800 matched horizon comparisons; 180000 matched market-round observations; exact ex-post fixed-price identities")
if __name__=="__main__":main()

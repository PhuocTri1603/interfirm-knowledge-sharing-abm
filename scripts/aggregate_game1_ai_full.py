"""Strict completeness and horizon-sign consistency of full Game 1 audit."""
import argparse,csv,glob
from collections import defaultdict,Counter
from pathlib import Path

def sign(x,tol=1e-8):
    return "positive" if x>tol else "negative" if x< -tol else "zero"
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",default="results/game1_ai_full/downloads")
    p.add_argument("--out",default="results/game1_ai_full/aggregate")
    a=p.parse_args()
    paths=glob.glob(a.input+"/**/profile_*.csv",recursive=True)
    rows=[]
    for path in paths:
        with open(path,newline="") as f:rows.extend(csv.DictReader(f))
    expected={(i,s,seed,h) for i in range(100) for s in (.5,1.,2.) for seed in (11,23,47) for h in (20,200)}
    actual=[(int(r["profile_index"]),float(r["sigma"]),int(r["seed"]),int(r["horizon"])) for r in rows]
    assert len(rows)==1800 and set(actual)==expected and len(set(actual))==1800,f"Missing {len(expected-set(actual))}, duplicates {len(actual)-len(set(actual))}"
    pairs=defaultdict(dict); groups=defaultdict(list)
    for r in rows:
        key=(int(r["profile_index"]),float(r["sigma"]),int(r["seed"]))
        pairs[key][int(r["horizon"])]=r
        groups[(int(r["horizon"]),float(r["sigma"]))].append(r)
        v=lambda col:float(r[col])
        assert abs(v("delta_profit")-v("delta_revenue")+v("delta_variable_cost")+v("delta_adjustment_cost")+v("delta_adoption_cost"))<1e-6
        assert abs(v("delta_revenue")-v("quantity_effect")-v("price_effect")-v("interaction_effect"))<1e-6
    comparisons=[]
    for (profile,sigma,seed),d in sorted(pairs.items()):
        short,long=d[20],d[200]
        s20=sign(float(short["delta_profit"]));s200=sign(float(long["delta_profit"]))
        comparisons.append(dict(profile_index=profile,sigma=sigma,seed=seed,
          profit_20=short["delta_profit"],profit_200=long["delta_profit"],
          per_round_profit_20=float(short["delta_profit"])/20,
          per_round_profit_200=float(long["delta_profit"])/200,
          sign_20=s20,sign_200=s200,same_sign=s20==s200,
          delta_output_20=short["delta_output"],delta_output_200=long["delta_output"]))
    report=[]
    for (h,sigma),rs in sorted(groups.items()):
        counts=Counter(sign(float(r["delta_profit"])) for r in rs)
        report.append(dict(horizon=h,sigma=sigma,cases=len(rs),positive=counts["positive"],
          negative=counts["negative"],zero=counts["zero"],
          mean_profit=sum(float(r["delta_profit"]) for r in rs)/len(rs),
          mean_profit_per_round=sum(float(r["delta_profit"]) for r in rs)/(len(rs)*h)))
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    for name,data in (("all_1800_horizon_cases.csv",rows),("paired_20_vs_200.csv",comparisons),("consistency_by_horizon_sigma.csv",report)):
        with (out/name).open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    print("PASS 1800 horizon rows, 900 matched 20-vs-200 comparisons")
    print("SIGN_STABILITY",sum(x["same_sign"] for x in comparisons),"/900")
    for r in report:print("HORIZON_SUMMARY",r)
if __name__=="__main__":main()

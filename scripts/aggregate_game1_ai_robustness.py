"""Aggregate completed robustness matrix CSV files; fail on missing/duplicate cells."""
import argparse,csv,glob
from collections import defaultdict,Counter
from pathlib import Path

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--input",default="results/game1_ai_robustness/downloads")
    a.add_argument("--out",default="results/game1_ai_robustness/aggregate")
    z=a.parse_args()
    paths=glob.glob(z.input+"/**/summary_p*_s*_seed*.csv",recursive=True)
    expected={(p,s,seed) for p in (0,9,19,29,39,49,59,69,79,99) for s in (.5,1.,2.) for seed in (11,23,47)}
    rows=[]
    for path in paths:
        with open(path,newline="") as f:rows.extend(csv.DictReader(f))
    actual=[(int(r["profile_index"]),float(r["sigma"]),int(r["seed"])) for r in rows]
    assert len(rows)==len(expected)==90 and set(actual)==expected and len(set(actual))==len(actual),f"Missing or duplicate cells: {sorted(expected-set(actual))}"
    grouped=defaultdict(list)
    for r in rows:grouped[(r["profile_index"],r["sigma"])].append(float(r["delta_profit"]))
    report=[]
    for (p,s),profits in sorted(grouped.items(),key=lambda x:(int(x[0][0]),float(x[0][1]))):
        report.append(dict(profile_index=p,sigma=s,n_seeds=len(profits),positive=sum(x>1e-8 for x in profits),negative=sum(x< -1e-8 for x in profits),zero=sum(abs(x)<=1e-8 for x in profits),mean_delta_profit=sum(profits)/len(profits),min_delta_profit=min(profits),max_delta_profit=max(profits)))
    out=Path(z.out);out.mkdir(parents=True,exist_ok=True)
    for name,data in (("all_90_cases.csv",rows),("consistency_by_profile_sigma.csv",report)):
        with (out/name).open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    print("PASS 90/90 cases, 30 profile-sigma groups, 3 seeds each")
    print("SIGN COUNTS",dict(Counter("positive" if float(r["delta_profit"])>1e-8 else "negative" if float(r["delta_profit"])< -1e-8 else "zero" for r in rows)))
    for r in report:print("CONSISTENCY",r)
if __name__=="__main__":main()

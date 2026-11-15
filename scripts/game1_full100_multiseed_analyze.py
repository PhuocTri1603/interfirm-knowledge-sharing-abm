"""Evaluate 3-seed full100 robustness with researcher-approved materiality margins.
Seeds are fixed treatments, not 300 independent draws from a seed population.
"""
import argparse,csv,json,zipfile,random,math
from collections import defaultdict
from pathlib import Path
from io import TextIOWrapper
p=argparse.ArgumentParser();p.add_argument("--artifacts",required=True);p.add_argument("--out",required=True);p.add_argument("--bootstrap",type=int,default=4000)
a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
SEEDS=(11,23,47);SIGMAS=("0.5","1.0","2.0")
A="L3=cost_adjusted|L4=profit_based";B="L3=productivity|L4=profit_based"
terminal=defaultdict(dict);markets=defaultdict(list)
for seed in SEEDS:
 for sigma in SIGMAS:
  for batch in range(10):
   file=Path(a.artifacts)/f"game1-robustness-seed-{seed}-sigma-{sigma}-batch-{batch}.zip"
   assert file.exists(),file
   with zipfile.ZipFile(file) as z:
    manifest=json.loads(z.read("manifest.json"))
    assert (manifest["seed"],float(manifest["sigma"]),manifest["batch"])==(seed,float(sigma),batch)
    for r in csv.DictReader(TextIOWrapper(z.open("terminal.csv"))):
     key=(r["profile_id"],sigma,seed);sid=r["strategy_id"]
     assert sid not in terminal[key]
     terminal[key][sid]=float(r["cumulative_profit"])
    for r in csv.DictReader(TextIOWrapper(z.open("market.csv"))):
     markets[(r["profile_id"],sigma,seed)].append((int(r["round"]),float(r["price"]),float(r["quantity"])))
assert len(terminal)==900 and all(len(v)==9 for v in terminal.values())
assert len(markets)==900 and all(len(v)==200 for v in markets.values())
profiles=sorted({k[0] for k in terminal});assert len(profiles)==100
def mean(x):return sum(x)/len(x)
def quantile(x,q):
 s=sorted(x);z=(len(s)-1)*q;i=int(z);return s[i]+(s[min(i+1,len(s)-1)]-s[i])*(z-i)
rng=random.Random(20261115)
def ci(data):
 vals=list(data);assert len(vals)==100
 draws=[mean([vals[rng.randrange(100)] for _ in range(100)]) for _ in range(a.bootstrap)]
 return [quantile(draws,.05),quantile(draws,.95)],[quantile(draws,.025),quantile(draws,.975)]
def rank(d):return tuple(sorted(d,key=lambda k:(-d[k],k)))
def ab(profile,sigma,seed):
 d=terminal[(profile,sigma,seed)];return d[A]-d[B]
results=[]
# Compare seed 23 and 47 against seed 11 with the approved A-B gap margin ±4,
# and sigma contrast margin ±8. CI inclusion checks *seed sensitivity* only.
for sigma in SIGMAS:
 for seed in (23,47):
  diff=[ab(p,sigma,seed)-ab(p,sigma,11) for p in profiles]
  c90,c95=ci(diff)
  results.append(dict(metric="AB_gap",sigma=sigma,seed=seed,baseline_seed=11,
   mean_difference=mean(diff),ci90=c90,ci95=c95,approved_margin=4,
   within_margin=c90[0]>-4 and c90[1]<4,
   sign_agreement=mean([int((ab(p,sigma,seed)>0)==(ab(p,sigma,11)>0)) for p in profiles]),
   winner_agreement=mean([int(rank(terminal[(p,sigma,seed)])[0]==rank(terminal[(p,sigma,11)])[0]) for p in profiles])))
for low,high in (("0.5","1.0"),("1.0","2.0"),("0.5","2.0")):
 for seed in (23,47):
  diff=[(ab(p,high,seed)-ab(p,low,seed))-(ab(p,high,11)-ab(p,low,11)) for p in profiles]
  c90,c95=ci(diff)
  results.append(dict(metric="AB_sigma_change",sigma_pair=[low,high],seed=seed,
   baseline_seed=11,mean_difference=mean(diff),ci90=c90,ci95=c95,
   approved_margin=8,within_margin=c90[0]>-8 and c90[1]<8))
# Price and output diagnostics use market means over 200 rounds, then paired profile means.
market_checks=[]
for sigma in SIGMAS:
 for seed in (23,47):
  for col,margin in ((1,.01),(2,.01)):
   vals=[]
   for profile in profiles:
    x=sorted(markets[(profile,sigma,seed)]);y=sorted(markets[(profile,sigma,11)])
    assert [v[0] for v in x]==[v[0] for v in y]==list(range(1,201))
    # quantity is total market supply, not firm-level output; approved
    # output ±.01 is NOT automatically valid for total market quantity.
    vals.append(mean([r[col]-b[col] for r,b in zip(x,y)]))
   c90,c95=ci(vals)
   market_checks.append(dict(metric="market_price" if col==1 else "total_market_quantity",
    sigma=sigma,seed=seed,mean_difference=mean(vals),ci90=c90,ci95=c95,
    approved_margin=margin if col==1 else None,
    within_margin=(c90[0]>-margin and c90[1]<margin) if col==1 else None,
    note="Total market quantity has no approved equivalence margin" if col==2 else "Approved price margin ±0.01"))
report=dict(status="MULTISEED_DIAGNOSTIC",research_validated=False,
 seeds=list(SEEDS),technology_profiles=100,sigmas=list(SIGMAS),strategies=9,rounds=200,
 bootstrap_replicates=a.bootstrap,unit="paired technology profile",
 approved_margins=dict(AB_gap=4,AB_sigma_change=8,market_price=.01),
 results=results,market_checks=market_checks,
 interpretation="Three seeds cannot establish population-level seed robustness; profile bootstrap estimates variation across technology profiles conditional on compared seeds. Not a TOST over independent seeds.",
 engine_changed=False)
(out/"multiseed_robustness.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(dict(status=report["status"],comparisons=results,market_checks=market_checks),indent=2))

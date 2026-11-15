"""Pre-registered economic equivalence audit of archived vs instrumented Game 1.
No engine execution. Paired cluster bootstrap resamples 100 technology profiles.
Margins are fixed in normalized economic units, NOT estimated from replay errors.
"""
import argparse,csv,json,math,random,zipfile
from collections import defaultdict
from io import TextIOWrapper
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument("--archive",required=True)
ap.add_argument("--observations",required=True)
ap.add_argument("--out",required=True)
ap.add_argument("--bootstrap",type=int,default=4000)
args=ap.parse_args()
assert args.bootstrap>=1000
out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
# LOCKED A PRIORI: P0=1, Y0=1, 200 rounds. A 1% reference
# revenue deviation per round => delta=0.01; cumulative delta=2.
# These are candidate materiality margins; must be approved before interpretation.
P0=1.0;Y0=1.0;T=200;fraction=0.01
margins={"price":fraction*P0,"output":fraction*Y0,
         "profit":fraction*P0*Y0,"cumulative_profit":fraction*P0*Y0*T,
         "AB_profit_gap":2*fraction*P0*Y0*T,
         "AB_sigma_change":4*fraction*P0*Y0*T}
alpha=.05;B=args.bootstrap; rng=random.Random(20261115)
profiles=[f"F{i:03d}" for i in range(1,101)]
sigma_vals=("0.5","1","2")
A="L3=cost_adjusted|L4=profit_based"
B_strategy="L3=productivity|L4=profit_based"
terminal=defaultdict(dict);daily=defaultdict(lambda:defaultdict(list))
rankings=defaultdict(dict)
for sigma in sigma_vals:
 for batch in range(10):
  tag=f"sigma_{sigma}_batch_{batch:02d}"
  path=Path(args.observations)/f"game1-task-sigma-{float(sigma):.1f}-batch-{batch}.zip"
  with zipfile.ZipFile(args.archive) as archive,zipfile.ZipFile(path) as obs:
   with archive.open(tag+"_rounds.csv") as af,obs.open("firm_dynamics.csv") as nf:
    old={(r["profile_id"],int(r["round"]),r["strategy_id"]):r for r in csv.DictReader(TextIOWrapper(af))}
    seen=set()
    for r in csv.DictReader(TextIOWrapper(nf)):
     k=(r["profile_id"],int(r["round"]),r["strategy_id"])
     assert k in old and k not in seen
     seen.add(k);o=old[k];profile,round_,strategy=k
     for field in ("price","output","profit"):
      daily[(profile,sigma,strategy)][field].append(float(r[field])-float(o[field]))
     if round_==T:
      terminal[(profile,sigma)][strategy]=(float(o["cumulative_profit"]),float(r["cumulative_profit"]))
    assert len(seen)==len(old)==18000
assert len(terminal)==300
strategies=sorted(next(iter(terminal.values())))
assert len(strategies)==9 and A in strategies and B_strategy in strategies

def mean(xs):return sum(xs)/len(xs)
def quantile(xs,q):
 s=sorted(xs);v=(len(s)-1)*q;lo=int(v);hi=min(lo+1,len(s)-1)
 return s[lo]+(s[hi]-s[lo])*(v-lo)
def bootstrap_ci(by_profile):
 values=[by_profile[p] for p in profiles]
 assert all(math.isfinite(x) for x in values)
 estimates=[]
 for _ in range(B):
  estimates.append(mean([values[rng.randrange(100)] for _ in range(100)]))
 return [quantile(estimates,.05),quantile(estimates,.95)], [quantile(estimates,.025),quantile(estimates,.975)]
def audit(name,by_profile,margin):
 ci90,ci95=bootstrap_ci(by_profile);effect=mean(list(by_profile.values()))
 equivalent=ci90[0]>-margin and ci90[1]<margin
 excluded=ci95[1]<-margin or ci95[0]>margin
 return dict(name=name,unit="technology profile (n=100)",paired_mean_difference=effect,
             margin=[-margin,margin],bootstrap_90_CI=ci90,bootstrap_95_CI=ci95,
             TOST_bootstrap_equivalence="EQUIVALENT" if equivalent else ("NON_EQUIVALENT" if excluded else "INCONCLUSIVE"),
             method="paired cluster percentile bootstrap CI inclusion; approximate TOST, not parametric TOST")
results=[]
for sigma in sigma_vals:
 for strategy in strategies:
  for field in ("price","output","profit"):
   # Market price is repeated for 9 players: do not claim 9 independent samples.
   data={p:mean(daily[(p,sigma,strategy)][field]) for p in profiles}
   results.append(audit(f"{field}|sigma={sigma}|{strategy}",data,margins[field]))
  data={p:terminal[(p,sigma)][strategy][1]-terminal[(p,sigma)][strategy][0] for p in profiles}
  results.append(audit(f"terminal_cumulative_profit|sigma={sigma}|{strategy}",data,margins["cumulative_profit"]))
 for p in profiles:
  assert len(terminal[(p,sigma)])==9
 data={}
 for p in profiles:
  a0,a1=terminal[(p,sigma)][A];b0,b1=terminal[(p,sigma)][B_strategy]
  data[p]=(a1-b1)-(a0-b0)
 results.append(audit(f"AB_terminal_profit_gap|sigma={sigma}",data,margins["AB_profit_gap"]))
for low,high in (("0.5","1"),("1","2"),("0.5","2")):
 data={}
 for p in profiles:
  def gap(s,ix):
   return terminal[(p,s)][A][ix]-terminal[(p,s)][B_strategy][ix]
  data[p]=(gap(high,1)-gap(low,1))-(gap(high,0)-gap(low,0))
 results.append(audit(f"AB_sigma_change|{low}->{high}",data,margins["AB_sigma_change"]))

def ranks(d):
 return sorted(d,key=lambda k:(-d[k],k))
def kendall(x,y):
 n=len(x);a={v:i for i,v in enumerate(x)};b={v:i for i,v in enumerate(y)}
 concord=0;discord=0
 for i in range(n):
  for j in range(i+1,n):
   if (a[x[i]]-a[x[j]])*(b[x[i]]-b[x[j]])>0:concord+=1
   else:discord+=1
 return (concord-discord)/(n*(n-1)/2)
rank_summary={}
for sigma in sigma_vals:
 winner=0;exact=0;taus=[]
 for p in profiles:
  old={s:v[0] for s,v in terminal[(p,sigma)].items()}
  new={s:v[1] for s,v in terminal[(p,sigma)].items()}
  x=ranks(old);y=ranks(new)
  winner+=x[0]==y[0];exact+=x==y;taus.append(kendall(x,y))
 rank_summary[sigma]=dict(n=100,winner_agreement=winner/100,exact_ranking_agreement=exact/100,
                          mean_kendall_tau=mean(taus))
report=dict(status="AUDIT_COMPUTED_NOT_VALIDATED",research_validated=False,
  archive_run=42463803820,observation_run=43593085278,
  preregistered_margins=margins,margin_basis="1% of reference per-round revenue P0*Y0=1; 200-round cumulative; 2x and 4x for contrasts",
  warning="Margins are proposed economic materiality thresholds, not user-approved; results are diagnostic only. Two deterministic paired runs cannot establish multi-seed robustness.",
  alpha=alpha,bootstrap_replicates=B,bootstrap_seed=20261115,
  multiple_testing="Exploratory family of 111 tests; no simultaneous familywise guarantee. Preselect primary contrasts before confirmatory claims.",
  independence="100 technology-profile clusters; within-profile sigma/strategy/round dependence preserved",
  tests=results,rankings=rank_summary,
  historical_task_KL="NOT_IDENTIFIABLE",engine_invoked=False)
(out/"statistical_equivalence_audit.json").write_text(json.dumps(report,indent=2)+"\n")
with (out/"statistical_equivalence_summary.md").open("w") as f:
 f.write("# Game 1 statistical equivalence audit (diagnostic)\n\n")
 f.write("Status: AUDIT_COMPUTED_NOT_VALIDATED. Economic margins are proposed, not yet approved.\n\n")
 f.write("All tests use paired profile-cluster bootstrap, 4000 draws by default, 90% CI for equivalence and 95% CI for effects.\n\n")
 f.write("| Comparison | Mean new minus archive | Margin | 90% CI | Decision |\n|---|---:|---:|---|---|\n")
 for r in results:
  if r["name"].startswith("AB_"):
   f.write(f'| {r["name"]} | {r["paired_mean_difference"]:.6g} | ±{r["margin"][1]:.4g} | {r["bootstrap_90_CI"]} | {r["TOST_bootstrap_equivalence"]} |\n')
 f.write("\nRank agreement: "+json.dumps(rank_summary)+"\n")
print(json.dumps(dict(status=report["status"],tests=len(results),primary=[r for r in results if r["name"].startswith("AB_")],rankings=rank_summary),indent=2))

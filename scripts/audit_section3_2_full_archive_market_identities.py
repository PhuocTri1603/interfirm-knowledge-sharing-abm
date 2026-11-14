"""Independent archive-wide economic identity and market validation; never invokes engine."""
import argparse,csv,json,math,zipfile
from io import TextIOWrapper
from collections import defaultdict
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("--archive",required=True);p.add_argument("--out",required=True);a=p.parse_args()
out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
markets=defaultdict(lambda:dict(q=0.,prices=[],profits={},outputs={},actions={},ai={},adopted={},cum={}))
rows=0;invalid=[];neg_output=0;neg_price=0;nonfinite=0;negative_implied_cost=0
with zipfile.ZipFile(a.archive) as z:
    for sigma in ("0.5","1","2"):
        for batch in range(10):
            name=f"sigma_{sigma}_batch_{batch:02d}_rounds.csv"
            with z.open(name) as f:
                for r in csv.DictReader(TextIOWrapper(f,encoding="utf-8")):
                    rows+=1
                    profile=r["profile_id"];t=int(r["round"]);sid=r["strategy_id"]
                    key=(profile,sigma,t)
                    q=float(r["output"]);price=float(r["price"]);pi=float(r["profit"]);cp=float(r["cumulative_profit"])
                    if not all(math.isfinite(x) for x in (q,price,pi,cp)):nonfinite+=1
                    neg_output+=q<0;neg_price+=price<0
                    negative_implied_cost+=(price*q-pi)<-1e-8
                    m=markets[key]
                    if sid in m["profits"]:raise AssertionError(("duplicate",key,sid))
                    m["q"]+=q;m["prices"].append(price);m["profits"][sid]=pi;m["outputs"][sid]=q;m["actions"][sid]=r["action"];m["ai"][sid]=int(r["active_ai_count"]);m["adopted"][sid]=int(r["adopted_count"]);m["cum"][sid]=cp
assert rows==540000 and len(markets)==60000
max_price_spread=0.;max_inverse_demand_error=0.;bad_markets=[];bad_player_counts=0
for key,m in markets.items():
    if len(m["prices"])!=9:bad_player_counts+=1
    spread=max(m["prices"])-min(m["prices"])
    error=abs(m["prices"][0]-max(0.,2.-m["q"]/9.))
    max_price_spread=max(max_price_spread,spread)
    max_inverse_demand_error=max(max_inverse_demand_error,error)
    if spread>1e-8 or error>1e-8:bad_markets.append(dict(profile=key[0],sigma=key[1],round=key[2],price_spread=spread,inverse_demand_error=error))
# Do not assert cumulative_profit=sum(round_profit): capital valuation can differ by design.
report=dict(status="PASS" if not (bad_markets or bad_player_counts or neg_output or neg_price or nonfinite or negative_implied_cost) else "FAIL",
    archive_rows=rows,markets=len(markets),profiles=100,sigmas=[0.5,1,2],strategies=9,rounds=200,
    max_within_market_price_spread=max_price_spread,max_inverse_demand_error=max_inverse_demand_error,
    bad_markets=len(bad_markets),bad_player_counts=bad_player_counts,nonfinite=nonfinite,negative_output=neg_output,negative_price=neg_price,negative_implied_cost=negative_implied_cost,
    scope="archive-only: supply, common price, inverse demand, implied total costs; no direct K/L, AI allocation or cost components",
    causal_mechanism_validated=False,full_economic_mechanism_certified=False,research_validated=False,engine_invoked=False)
(out/"full_archive_market_identity_audit.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
if report["status"]!="PASS":raise SystemExit(1)

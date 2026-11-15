"""Full-100 multi-seed Game 1, no engine modifications."""
import argparse,csv,json
from dataclasses import replace
from pathlib import Path
from interfirm_abm.task_a6_market import approved_profiles
from interfirm_abm.game1_nine_strategy import run_game1
from reproduce_paper_section3_2 import params

p=argparse.ArgumentParser()
p.add_argument("--batch",type=int,required=True,choices=range(10))
p.add_argument("--sigma",type=float,required=True,choices=(.5,1.,2.))
p.add_argument("--seed",type=int,required=True,choices=(11,23,47))
p.add_argument("--out",required=True)
a=p.parse_args()
out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
rows=[];market=[]
for profile in approved_profiles()[a.batch*10:(a.batch+1)*10]:
 result=run_game1(profile,a.sigma,replace(params(),seed=a.seed),rounds=200,audit=True)
 assert len(result["players"])==1800 and len(result["market"])==200
 for r in result["players"]:
  if r["round"]==200:
   rows.append(dict(profile_id=profile.firm_id,sigma=a.sigma,seed=a.seed,
                    strategy_id=r["strategy_id"],cumulative_profit=r["cumulative_profit"]))
 for m in result["market"]:
  market.append(dict(profile_id=profile.firm_id,sigma=a.sigma,seed=a.seed,
                     round=m["round"],price=m["price"],quantity=m["quantity"]))
assert len(rows)==90 and len(market)==2000
for name,data in (("terminal.csv",rows),("market.csv",market)):
 with (out/name).open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
(out/"manifest.json").write_text(json.dumps(dict(seed=a.seed,sigma=a.sigma,batch=a.batch,
  profiles=10,terminal_rows=90,market_rows=2000,engine_changed=False,
  research_validated=False),indent=2)+"\n")
print(json.dumps(dict(seed=a.seed,sigma=a.sigma,batch=a.batch,status="DATA_COLLECTED")))

"""Gate dynamic audit against prior fixed-SIMD 200-round player and market trajectories."""
import argparse,csv,json,math
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("--audit",required=True);p.add_argument("--trial",required=True);p.add_argument("--out",required=True);a=p.parse_args()
audit=Path(a.audit);trial=json.loads(Path(a.trial).read_text());out=Path(a.out)
rows=list(csv.DictReader((audit/"firm_dynamics.csv").open()))
markets=list(csv.DictReader((audit/"market_dynamics.csv").open()))
base={(int(r["round"]),r["strategy_id"]):r for r in trial["rows"]}
checks={}
for field in ("output","price","profit","cumulative_profit","active_ai_count","adopted_count"):
    checks[field]={"max_abs":0.,"mismatches":0}
action_mismatches=0
assert len(rows)==len(base)==1800
for r in rows:
    b=base[(int(r["round"]),r["strategy_id"])]
    action_mismatches+=int(r["action"]!=b["action"])
    for field in checks:
        x=float(r[field]);y=float(b[field]);d=abs(x-y)
        checks[field]["max_abs"]=max(checks[field]["max_abs"],d)
        checks[field]["mismatches"]+=int(d>1e-7+1e-9*max(abs(x),abs(y)))
market_errors={"quantity":0.,"price":0.}
assert len(markets)==len(trial["markets"])==200
for r,b in zip(markets,trial["markets"]):
    assert int(r["round"])==int(b["round"])
    for f in market_errors:market_errors[f]=max(market_errors[f],abs(float(r[f])-float(b[f])))
passed=action_mismatches==0 and all(v["mismatches"]==0 for v in checks.values()) and max(market_errors.values())<=1e-7
report={"profile":trial["profile"],"sigma":trial["sigma"],"audit_vs_prior_fixed_simd_pass":passed,"action_mismatches":action_mismatches,"checks":checks,"market_errors":market_errors,"research_validated":False}
out.write_text(json.dumps(report,indent=2));print("DYNAMIC_GATE",json.dumps(report))
if not passed:raise SystemExit(2)

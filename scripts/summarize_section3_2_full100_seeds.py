"""Aggregate all 100 profiles × 3 seeds with strict completeness and accounting gates."""
import argparse,csv,json,math
from pathlib import Path
from collections import defaultdict,Counter
p=argparse.ArgumentParser();p.add_argument("--input",required=True);p.add_argument("--out",required=True);a=p.parse_args()
root=Path(a.input);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
files=sorted(root.rglob("paired_seed_markets.csv"));gates=sorted(root.rglob("batch_gate.json"))
assert len(files)==len(gates)==30,(len(files),len(gates))
rows=[]
for f in files:
    with f.open() as h:rows.extend(csv.DictReader(h))
assert len(rows)==300,len(rows)
expected={(f"F{i:03d}",s) for i in range(1,101) for s in (11,23,47)}
actual=[(r["profile"],int(r["seed"])) for r in rows]
assert len(set(actual))==300 and set(actual)==expected
for f in gates:
    v=json.loads(f.read_text())
    assert v["pass_accounting"] and v["engine_modified"] is False and len(v["profiles"])==10
for r in rows:
    assert float(r["max_accounting_residual"])<1e-7
    assert r["engine_modified"]=="False"
byseed=defaultdict(list)
for r in rows:byseed[int(r["seed"])].append(r)
fields=("price_revaluation","quantity_contribution","cost_change","fixed_price_profit_change","observed_profit_change","gap_A_minus_B_sigma1","gap_A_minus_B_sigma2","gap_A_minus_B_change","mean_market_supply_sigma1","mean_market_supply_sigma2","mean_market_price_sigma1","mean_market_price_sigma2")
summary=[]
for seed,rr in sorted(byseed.items()):
    assert len(rr)==100
    z=dict(seed=seed,profiles=100,negative_price_profiles=sum(float(r["price_revaluation"])< -1e-8 for r in rr),
       positive_fixed_price_profiles=sum(float(r["fixed_price_profit_change"])>1e-8 for r in rr),
       positive_observed_profit_profiles=sum(float(r["observed_profit_change"])>1e-8 for r in rr),
       winner_changed_profiles=sum(int(r["observed_winner_changed"]) for r in rr),
       repricing_changed_winner_profiles=sum(int(r["repricing_changes_winner"]) for r in rr),
       positive_A_minus_B_gap_sigma1=sum(float(r["gap_A_minus_B_sigma1"])>1e-8 for r in rr),
       positive_A_minus_B_gap_sigma2=sum(float(r["gap_A_minus_B_sigma2"])>1e-8 for r in rr))
    for k in fields:z[k+"_sum"]=math.fsum(float(r[k]) for r in rr)
    summary.append(z)
profile_winner_variability=sum(len({r["winner_sigma2"] for r in rows if r["profile"]==f"F{i:03d}"})>1 for i in range(1,101))
for name,rr in (("full100_paired_seed_markets.csv",rows),("full100_paired_seed_summary.csv",summary)):
    with (out/name).open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
report=dict(status="PASS_ACCOUNTING_AND_COVERAGE",profiles=100,seeds=[11,23,47],markets=600,
  paired_profile_seed_comparisons=300,firm_rounds=1080000,
  sigma2_winner_varies_across_seeds_profiles=profile_winner_variability,
  negative_price_all_300=all(float(r["price_revaluation"])< -1e-8 for r in rows),
  positive_fixed_price_all_300=all(float(r["fixed_price_profit_change"])>1e-8 for r in rows),
  original_engine_unchanged=True,strict_historical_archive_equivalence_not_proven=True,
  counterfactual_is_accounting_not_causal=True,research_validated=False,seeds=summary)
(out/"full100_paired_seed_report.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))

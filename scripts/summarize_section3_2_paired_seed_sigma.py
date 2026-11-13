"""Aggregate paired profile-seed markets, preserving paired design and failures."""
import argparse,csv,json,math
from pathlib import Path
from collections import defaultdict
p=argparse.ArgumentParser();p.add_argument("--input",required=True);p.add_argument("--out",required=True);a=p.parse_args()
root=Path(a.input);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
files=sorted(root.rglob("paired_seed_market.csv"))
rows=[]
for file in files:
    with file.open() as f:rows.extend(csv.DictReader(f))
expected_profiles=("F001","F011","F021","F031","F041","F051","F061","F071","F081","F091")
expected={(p,s) for p in expected_profiles for s in (11,23,47)}
actual={(r["profile"],int(r["seed"])) for r in rows}
assert len(rows)==30 and actual==expected,(len(rows),expected-actual,actual-expected)
assert len(list(root.rglob("paired_seed_gate.json")))==30
for file in root.rglob("paired_seed_gate.json"):
    gate=json.loads(file.read_text())
    assert gate["pass_accounting"] and not gate["engine_modified"]
fields=("price_revaluation","quantity_contribution","cost_change","fixed_price_profit_change","observed_profit_change","gap_A_minus_B_sigma1","gap_A_minus_B_sigma2","gap_A_minus_B_change","mean_market_supply_sigma1","mean_market_supply_sigma2","mean_market_price_sigma1","mean_market_price_sigma2")
byseed=defaultdict(list)
for r in rows:
    assert float(r["max_accounting_residual"])<1e-7
    byseed[int(r["seed"])].append(r)
summary=[]
for seed,rs in sorted(byseed.items()):
    assert len(rs)==10
    d=dict(seed=seed,profiles=len(rs),negative_price_profiles=sum(float(r["price_revaluation"])< -1e-8 for r in rs),
        positive_fixed_price_profiles=sum(float(r["fixed_price_profit_change"])>1e-8 for r in rs),
        positive_observed_profit_profiles=sum(float(r["observed_profit_change"])>1e-8 for r in rs),
        winner_changed_profiles=sum(int(r["observed_winner_changed"]) for r in rs),
        repricing_changed_winner_profiles=sum(int(r["repricing_changes_winner"]) for r in rs),
        positive_A_minus_B_gap_sigma1=sum(float(r["gap_A_minus_B_sigma1"])>1e-8 for r in rs),
        positive_A_minus_B_gap_sigma2=sum(float(r["gap_A_minus_B_sigma2"])>1e-8 for r in rs))
    for f in fields:d[f+"_sum"]=math.fsum(float(r[f]) for r in rs)
    summary.append(d)
for filename,values in (("paired_seed_markets.csv",rows),("paired_seed_summary.csv",summary)):
    with (out/filename).open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(values[0]));w.writeheader();w.writerows(values)
report=dict(status="PASS_ACCOUNTING_AND_COVERAGE",scope="10 predeclared synthetic profiles, seeds 11/23/47, sigma 1/2, 200 rounds, nine strategies",markets=60,paired_profile_seed_comparisons=30,original_engine_unchanged=True,strict_archive_equivalence_not_established=True,causal_mediation_identified=False,research_validated=False,
    sign_consistency=dict(negative_price_all_seeds=all(s["negative_price_profiles"]==10 for s in summary),positive_fixed_price_all_seeds=all(s["positive_fixed_price_profiles"]==10 for s in summary)),
    seeds=summary)
(out/"paired_seed_report.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))

"""Post-hoc fixed-output, fixed-cost repricing; no economic-engine invocation."""
import argparse,csv,json,math
from pathlib import Path
from collections import defaultdict

def read_case(root, profile, sigma):
    directory=root / f"dynamic-audit-{profile}-sigma-{sigma}"
    if not directory.is_dir():
        raise FileNotFoundError(directory)
    gate=json.loads((directory/"dynamic_gate.json").read_text())
    audit=json.loads((directory/"audit_report.json").read_text())
    assert gate["audit_vs_prior_fixed_simd_pass"] is True
    assert audit["profile"]==profile and float(audit["sigma"])==float(sigma)
    with (directory/"firm_dynamics.csv").open() as f:
        rows=list(csv.DictReader(f))
    with (directory/"market_dynamics.csv").open() as f:
        markets=list(csv.DictReader(f))
    assert len(rows)==1800 and len(markets)==200
    r={(int(x["round"]),x["strategy_id"]):x for x in rows}
    m={int(x["round"]):x for x in markets}
    assert len(r)==1800 and len(m)==200
    assert all(abs(float(x["price"])-float(m[int(x["round"])]["price"]))<1e-10 for x in rows)
    assert all(abs(float(x["market_quantity"])-float(m[int(x["round"])]["quantity"]))<1e-10 for x in rows)
    return r,m

def cost(r):
    return sum(float(r[k]) for k in ("variable_cost","adjustment_cost","adoption_cost"))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    root=Path(a.root);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    profiles=("F011","F021","F071","F091")
    cases={(f,s):read_case(root,f,s) for f in profiles for s in ("0.5","1","2")}
    records=[];max_identity=0.;max_revenue=0.
    for profile in profiles:
        for reference,target in (("1","2"),("0.5","1"),("0.5","2")):
            old,old_m=cases[(profile,reference)]
            new,new_m=cases[(profile,target)]
            assert old.keys()==new.keys()
            for key in sorted(old):
                x=old[key];y=new[key];round_id,sid=key
                p0=float(old_m[round_id]["price"]);p1=float(new_m[round_id]["price"])
                q0=float(x["output"]);q1=float(y["output"])
                c0=cost(x);c1=cost(y)
                pi0=float(x["profit"]);pi1=float(y["profit"])
                assert abs(pi0-(p0*q0-c0))<1e-8 and abs(pi1-(p1*q1-c1))<1e-8
                # Baseline price, target decisions: output and cost held exactly as recorded.
                cf_baseline=p0*q1-c1
                quantity_base=p0*(q1-q0)
                price_final=(p1-p0)*q1
                # Symmetric alternative: target price and baseline quantity.
                quantity_final=p1*(q1-q0)
                price_base=(p1-p0)*q0
                delta_profit=pi1-pi0
                delta_cost=c1-c0
                residual=delta_profit-(quantity_base+price_final-delta_cost)
                reverse=delta_profit-(quantity_final+price_base-delta_cost)
                max_identity=max(max_identity,abs(residual),abs(reverse))
                max_revenue=max(max_revenue,abs((p1*q1-p0*q0)-(quantity_base+price_final)))
                records.append(dict(profile=profile,reference_sigma=reference,target_sigma=target,round=round_id,strategy_id=sid,reference_price=p0,target_price=p1,reference_output=q0,target_output=q1,reference_cost=c0,target_cost=c1,reference_profit=pi0,target_profit=pi1,counterfactual_profit_at_reference_price=cf_baseline,delta_profit=delta_profit,quantity_at_reference_price=quantity_base,price_at_target_quantity=price_final,delta_cost=delta_cost,quantity_at_target_price=quantity_final,price_at_reference_quantity=price_base,identity_error=residual))
    assert max_identity<1e-8 and max_revenue<1e-8
    fields=list(records[0])
    with (out/"counterfactual_rounds.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(records)
    groups=defaultdict(list)
    for r in records:
        groups[(r["profile"],r["reference_sigma"],r["target_sigma"],r["strategy_id"])].append(r)
        groups[(r["profile"],r["reference_sigma"],r["target_sigma"],"ALL_PLAYERS")].append(r)
    summaries=[]
    for (profile,reference,target,sid),rs in sorted(groups.items()):
        def total(k):return math.fsum(r[k] for r in rs)
        summaries.append(dict(profile=profile,reference_sigma=reference,target_sigma=target,strategy_id=sid,observations=len(rs),delta_profit=total("delta_profit"),counterfactual_delta_profit_at_reference_price=total("quantity_at_reference_price")-total("delta_cost"),quantity_at_reference_price=total("quantity_at_reference_price"),price_at_target_quantity=total("price_at_target_quantity"),delta_cost=total("delta_cost"),quantity_at_target_price=total("quantity_at_target_price"),price_at_reference_quantity=total("price_at_reference_quantity"),reference_profit=total("reference_profit"),target_profit=total("target_profit")))
    with (out/"counterfactual_summary.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(summaries[0]));w.writeheader();w.writerows(summaries)
    report={"profiles":list(profiles),"sigma_pairs":[["1","2"],["0.5","1"],["0.5","2"]],"round_records":len(records),"summary_records":len(summaries),"max_profit_identity_error":max_identity,"max_revenue_identity_error":max_revenue,"all_input_dynamic_gates_passed":True,"economic_engine_invoked":False,"scope":"Conditional fixed-output/fixed-cost repricing; NOT a new market equilibrium or causal identification","research_validated":False}
    (out/"counterfactual_report.json").write_text(json.dumps(report,indent=2)+"\n")
    print("COUNTERFACTUAL",json.dumps(report))
    for r in summaries:
        if r["strategy_id"]=="ALL_PLAYERS":print("MARKET",json.dumps(r))
if __name__=="__main__":main()

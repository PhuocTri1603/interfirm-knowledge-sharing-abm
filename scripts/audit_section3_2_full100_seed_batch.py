"""Run one 10-profile batch at one seed; same frozen economic engine as scoped audit."""
import argparse,csv,json
from pathlib import Path
from interfirm_abm.task_a6_market import approved_profiles
from audit_section3_2_paired_seed_sigma import run,winner,A,B
from math import fsum
p=argparse.ArgumentParser();p.add_argument("--batch",type=int,required=True);p.add_argument("--seed",type=int,required=True);p.add_argument("--out",required=True);a=p.parse_args()
assert 0<=a.batch<10 and a.seed in (11,23,47)
profiles=approved_profiles()[a.batch*10:(a.batch+1)*10]
assert len(profiles)==10
out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
rows=[]
for profile in profiles:
    x,m1,ss=run(profile,a.seed,1.)
    y,m2,ss2=run(profile,a.seed,2.)
    assert ss==ss2 and len(ss)==9
    d={s:dict(pi1=0.,pi2=0.,cf2=0.,quantity=0.,cost=0.,price=0.) for s in ss}
    for t in range(1,201):
        p1=float(m1[t]["price"]);p2=float(m2[t]["price"])
        for s in ss:
            old=x[t,s];new=y[t,s];q1=float(old["output"]);q2=float(new["output"])
            pi1=float(old["profit"]);pi2=float(new["profit"])
            c1=p1*q1-pi1;c2=p2*q2-pi2
            v=d[s]
            for k,value in (("pi1",pi1),("pi2",pi2),("cf2",p1*q2-c2),("quantity",p1*(q2-q1)),("cost",c2-c1),("price",(p2-p1)*q2)):
                v[k]+=value
    total=lambda k:fsum(z[k] for z in d.values())
    delta=total("pi2")-total("pi1")
    residual=abs(delta-(total("quantity")-total("cost")+total("price")))
    assert residual<1e-7
    w1=winner({s:z["pi1"] for s,z in d.items()});w2=winner({s:z["pi2"] for s,z in d.items()});wc=winner({s:z["cf2"] for s,z in d.items()})
    rows.append(dict(profile=profile.firm_id,seed=a.seed,sigma_reference=1,sigma_target=2,
        price_revaluation=total("price"),quantity_contribution=total("quantity"),cost_change=total("cost"),
        fixed_price_profit_change=total("quantity")-total("cost"),observed_profit_change=delta,
        mean_market_price_sigma1=fsum(float(m1[t]["price"]) for t in m1)/200,
        mean_market_price_sigma2=fsum(float(m2[t]["price"]) for t in m2)/200,
        mean_market_supply_sigma1=fsum(float(m1[t]["quantity"]) for t in m1)/200,
        mean_market_supply_sigma2=fsum(float(m2[t]["quantity"]) for t in m2)/200,
        gap_A_minus_B_sigma1=d[A]["pi1"]-d[B]["pi1"],
        gap_A_minus_B_sigma2=d[A]["pi2"]-d[B]["pi2"],
        gap_A_minus_B_change=(d[A]["pi2"]-d[B]["pi2"])-(d[A]["pi1"]-d[B]["pi1"]),
        winner_sigma1=w1,winner_sigma2=w2,winner_sigma2_repriced=wc,
        observed_winner_changed=int(w1!=w2),repricing_changes_winner=int(w2!=wc),
        max_accounting_residual=residual,engine_modified=False,research_validated=False))
with (out/"paired_seed_markets.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(out/"batch_gate.json").write_text(json.dumps(dict(batch=a.batch,seed=a.seed,profiles=[r["profile"] for r in rows],pass_accounting=True,strict_archive_equivalence_not_claimed=True,engine_modified=False,research_validated=False),indent=2)+"\n")
print("BATCH_PASS",a.batch,a.seed,len(rows))

"""Paired-seed sigma 1->2 price-revaluation and winner audit; frozen engine unchanged.

Runs one technology profile and one RNG seed at both sigma levels, 200 rounds,
nine interacting strategies per market. Accounting counterfactual only.
"""
import argparse,csv,json,math
from dataclasses import replace
from pathlib import Path
import interfirm_abm.game1_nine_strategy as game
from interfirm_abm.task_a6_market import approved_profiles
from reproduce_paper_section3_2 import params
A="L3=cost_adjusted|L4=profit_based"
B="L3=productivity|L4=profit_based"
def run(profile,seed,sigma):
    p=replace(params(),seed=seed)
    result=game.run_game1(profile,sigma,p,rounds=200)
    players={(int(r["round"]),r["strategy_id"]):r for r in result["players"]}
    markets={int(r["round"]):r for r in result["market"]}
    assert len(players)==1800 and len(markets)==200
    strategies=sorted({k[1] for k in players})
    assert len(strategies)==9
    for t in range(1,201):
        q=sum(float(players[t,s]["output"]) for s in strategies)
        assert abs(q-float(markets[t]["quantity"]))<1e-7
        assert abs(float(markets[t]["price"])-max(0,2-q/9))<1e-7
        assert max(float(players[t,s]["price"]) for s in strategies)-min(float(players[t,s]["price"]) for s in strategies)<1e-7
    return players,markets,strategies
def winner(profits):
    return sorted(profits,key=lambda s:(-profits[s],s))[0]
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--profile",required=True)
    ap.add_argument("--seed",required=True,type=int)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    assert args.seed in (11,23,47)
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    profile=next(x for x in approved_profiles() if x.firm_id==args.profile)
    old,m1,ss=run(profile,args.seed,1.)
    new,m2,ss2=run(profile,args.seed,2.)
    assert ss==ss2 and A in ss and B in ss
    sums={s:{"pi1":0.,"pi2":0.,"cf2":0.,"quantity":0.,"cost":0.,"price":0.} for s in ss}
    for t in range(1,201):
        p1=float(m1[t]["price"]);p2=float(m2[t]["price"])
        for s in ss:
            x=old[t,s];y=new[t,s]
            q1=float(x["output"]);q2=float(y["output"])
            pi1=float(x["profit"]);pi2=float(y["profit"])
            c1=p1*q1-pi1;c2=p2*q2-pi2
            quantity=p1*(q2-q1);cost=c2-c1;price=(p2-p1)*q2
            assert abs((pi2-pi1)-(quantity-cost+price))<1e-8
            z=sums[s]
            for k,v in (("pi1",pi1),("pi2",pi2),("cf2",p1*q2-c2),("quantity",quantity),("cost",cost),("price",price)):
                z[k]+=v
    def total(k):return math.fsum(v[k] for v in sums.values())
    d=total("pi2")-total("pi1")
    quantity=total("quantity");cost=total("cost");price=total("price")
    assert abs(d-(quantity-cost+price))<1e-7
    w1=winner({s:z["pi1"] for s,z in sums.items()})
    w2=winner({s:z["pi2"] for s,z in sums.items()})
    wc=winner({s:z["cf2"] for s,z in sums.items()})
    row=dict(profile=args.profile,seed=args.seed,sigma_reference=1,sigma_target=2,
        price_revaluation=price,quantity_contribution=quantity,cost_change=cost,
        fixed_price_profit_change=quantity-cost,observed_profit_change=d,
        mean_market_price_sigma1=math.fsum(float(m1[t]["price"]) for t in m1)/200,
        mean_market_price_sigma2=math.fsum(float(m2[t]["price"]) for t in m2)/200,
        mean_market_supply_sigma1=math.fsum(float(m1[t]["quantity"]) for t in m1)/200,
        mean_market_supply_sigma2=math.fsum(float(m2[t]["quantity"]) for t in m2)/200,
        gap_A_minus_B_sigma1=sums[A]["pi1"]-sums[B]["pi1"],
        gap_A_minus_B_sigma2=sums[A]["pi2"]-sums[B]["pi2"],
        gap_A_minus_B_change=(sums[A]["pi2"]-sums[B]["pi2"])-(sums[A]["pi1"]-sums[B]["pi1"]),
        winner_sigma1=w1,winner_sigma2=w2,winner_sigma2_repriced=wc,
        observed_winner_changed=int(w1!=w2),repricing_changes_winner=int(w2!=wc),
        max_accounting_residual=abs(d-(quantity-cost+price)),
        engine_modified=False,research_validated=False)
    with (out/"paired_seed_market.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(row));w.writeheader();w.writerow(row)
    (out/"paired_seed_gate.json").write_text(json.dumps(dict(profile=args.profile,seed=args.seed,pass_accounting=True,strict_original_archive_equivalence_not_claimed=True,seed11_not_necessarily_original_archive_path=True,rows_per_sigma=1800,rounds=200,strategies=9,engine_modified=False,research_validated=False),indent=2)+"\n")
    print(json.dumps(row,indent=2))
if __name__=="__main__":main()

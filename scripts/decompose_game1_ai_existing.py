"""Decompose existing paired AI/no-AI CSV artifacts; never rerun the engine."""
import argparse,csv,glob,math
from collections import defaultdict
from pathlib import Path

def read(path):
    with open(path,newline="") as f:return list(csv.DictReader(f))
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",default="results/game1_decomposition/input")
    ap.add_argument("--out",default="results/game1_decomposition")
    z=ap.parse_args()
    files=sorted(glob.glob(z.input+"/**/round_panel_profile_*_sigma_*_seed_*.csv",recursive=True))
    if len(files)!=4:raise AssertionError(f"Expected four original paired panels, got {len(files)}: {files}")
    summary=[]; detail=[]
    for path in files:
        rows=read(path); groups=defaultdict(dict)
        for r in rows:
            key=(r["profile"],r["sigma"],r["seed"],int(r["round"]),r["strategy_id"])
            if r["scenario"] in groups[key]:raise AssertionError("Duplicate paired row")
            groups[key][r["scenario"]]=r
        if len(groups)!=180 or len(rows)!=360:raise AssertionError(f"Incomplete paired data: {path}")
        totals=defaultdict(float)
        for key,pair in groups.items():
            a=pair["ai_allowed"]; b=pair["ai_disabled"]
            def f(row,col):return float(row[col])
            q0=f(b,"output");q1=f(a,"output");p0=f(b,"price");p1=f(a,"price")
            dq=q1-q0;dp=p1-p0
            d=dict(profile=key[0],sigma=key[1],seed=key[2],round=key[3],strategy_id=key[4],
                quantity_effect=p0*dq,price_effect=q0*dp,interaction_effect=dp*dq,
                delta_revenue=f(a,"revenue")-f(b,"revenue"),
                delta_input_cost=f(a,"variable_cost")-f(b,"variable_cost"),
                delta_adjustment_cost=f(a,"adjustment_cost")-f(b,"adjustment_cost"),
                delta_ai_fee=f(a,"adoption_cost")-f(b,"adoption_cost"),
                delta_profit=f(a,"profit")-f(b,"profit"),
                delta_output=dq,delta_price=dp,
                delta_labor=f(a,"labor_used")-f(b,"labor_used"),
                delta_capital=f(a,"capital_used")-f(b,"capital_used"))
            if abs(d["delta_revenue"]-d["quantity_effect"]-d["price_effect"]-d["interaction_effect"])>1e-7:raise AssertionError("Revenue identity failed")
            if abs(d["delta_profit"]-d["delta_revenue"]+d["delta_input_cost"]+d["delta_adjustment_cost"]+d["delta_ai_fee"])>1e-7:raise AssertionError("Profit identity failed")
            detail.append(d)
            for k,v in d.items():
                if k not in ("profile","sigma","seed","round","strategy_id"):totals[k]+=v
        summary.append(dict(profile=key[0],sigma=key[1],seed=key[2],**totals))
    output=Path(z.out);output.mkdir(parents=True,exist_ok=True)
    for name,rows in (("decomposition_summary.csv",summary),("decomposition_by_player_round.csv",detail)):
        with (output/name).open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    for r in summary:
        print("DECOMPOSITION",r)
    print("PASS: 4 original paired panels; 720 paired player-round records; exact revenue and profit identities")
if __name__=="__main__":main()

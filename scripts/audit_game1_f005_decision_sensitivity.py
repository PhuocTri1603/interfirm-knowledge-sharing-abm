"""Observe F005 seed-47 Q-value margins without changing actions or learning."""
import csv
from pathlib import Path
from interfirm_abm.game1_nine_strategy import Game1Params, run_game1
from interfirm_abm.task_a6_market import approved_profiles

def main():
    firm=approved_profiles()[4]
    assert firm.firm_id=="F005"
    out=Path("results/game1_f005_decision_sensitivity")
    out.mkdir(parents=True,exist_ok=True)
    for fee in (1,3):
        p=Game1Params(2.,1./9.,.5/51.5,.5/51.5,.1,
                      .1*.5/20.*fee,.1,.15,47)
        trace=[]
        result=run_game1(firm,2.,p,rounds=200,audit=True,decision_trace=trace)
        target=out/f"F005_sigma2_seed47_fee{fee}_q_margins.csv"
        with target.open("w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=list(trace[0]))
            writer.writeheader()
            writer.writerows(trace)
        focal=[r for r in trace if r["strategy_id"]=="L3=productivity|L4=cost_based"]
        print("fee",fee,"focal rounds 90-110:")
        for r in focal:
            if 90<=r["round"]<=110:
                print(r["round"],r["action"],r["greedy_action"],
                      "Q(b2)-Q(b3)",f'{r["b2_b3_gap"]:.12g}',
                      "Q(b3)-Q(b4)",f'{r["b3_b4_gap"]:.12g}',
                      "top-two margin",f'{r["greedy_margin"]:.12g}')
        # Confirm opt-in diagnostics are behavior-neutral, including every numeric record.
        control=run_game1(firm,2.,p,rounds=200,audit=True)
        assert result["players"]==control["players"],"Diagnostic trace changed player outputs"
        assert result["market"]==control["market"],"Diagnostic trace changed market"
        print("PASS: optional decision trace does not change results",fee)
    print("PASS: 200-round Q-value sensitivity traces exported")

if __name__=="__main__":
    main()

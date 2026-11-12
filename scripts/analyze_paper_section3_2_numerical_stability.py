"""Summarize archived-vs-replayed economics without treating failed numerical gates as validation."""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True);p.add_argument("--archive",required=True);p.add_argument("--out",required=True)
    a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    gates=sorted(Path(a.root).rglob("sigma_*_batch_*_gate.json"))
    summary={"expected_batches":30,"observed_batches":len(gates),"strict_pass_batches":0,
             "reproduction_gate":"NOT_ESTABLISHED","research_validated":False}
    if len(gates)!=30:
        summary["error"]="Missing batches: no full-sample inference permitted"
        (out/"section32_full_sample_gate_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
        print(json.dumps(summary));return 2
    reports=[json.loads(g.read_text()) for g in gates]
    summary["strict_pass_batches"]=sum(bool(g["pass"]) for g in reports)
    summary["gate_failures"]=[{"sigma":g["sigma"],"batch":g["batch"],
       "mismatches":{k:g[k]["n_mismatched"] for k in
       ("output","price","profit","cumulative_profit","active_ai_count","adopted_count")},
       "ranking_mismatches":g["ranking_mismatches"],"action_mismatches":g["action_mismatches"],
       "max_terminal_profit_difference":g["max_terminal_profit_difference"]}
       for g in reports if not g["pass"]]
    archived=[];replayed=[]
    for g in reports:
        prefix=f"sigma_{g['sigma']:g}_batch_{g['batch']:02d}"
        archive=Path(a.archive)/f"{prefix}_rounds.csv"
        replicas=list(Path(a.root).rglob(f"{prefix}_reproduced_rounds.csv"))
        if not archive.exists() or len(replicas)!=1:
            summary["error"]=f"Missing or ambiguous data for {prefix}"
            (out/"section32_full_sample_gate_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
            return 2
        archived.append(pd.read_csv(archive))
        replayed.append(pd.read_csv(replicas[0]))
    original=pd.concat(archived,ignore_index=True)
    new=pd.concat(replayed,ignore_index=True)
    keys=["profile_id","sigma","strategy_id","round"]
    assert len(original)==len(new)==540000
    z=original.merge(new,on=keys,suffixes=("_archived","_replayed"),validate="one_to_one")
    assert len(z)==540000
    terminal=z[z["round"]==200].copy()
    terminal["terminal_abs_diff"]=(terminal.cumulative_profit_archived-terminal.cumulative_profit_replayed).abs()
    summary["round_observations"]=len(z)
    summary["max_terminal_abs_diff"]=float(terminal.terminal_abs_diff.max())
    summary["terminal_abs_diff_quantiles"]={str(q):float(terminal.terminal_abs_diff.quantile(q))
                                          for q in (0,.5,.9,.95,.99,1)}
    def rank(frame,field):
        return (frame.sort_values(["profile_id","sigma",field,"strategy_id"],
                ascending=[True,True,False,True])
                .groupby(["profile_id","sigma"],as_index=False).first()
                [["profile_id","sigma","strategy_id"]].rename(columns={"strategy_id":"winner"}))
    wa=rank(terminal,"cumulative_profit_archived")
    wr=rank(terminal,"cumulative_profit_replayed")
    w=wa.merge(wr,on=["profile_id","sigma"],suffixes=("_archived","_replayed"))
    summary["market_winner_changes"]=int((w.winner_archived!=w.winner_replayed).sum())
    w.to_csv(out/"section32_market_winner_stability.csv",index=False)
    policies=["L3=cost_adjusted|L4=profit_based","L3=productivity|L4=profit_based"]
    t=terminal[terminal.strategy_id.isin(policies)]
    def paired(field):
        wide=t.pivot(index=["profile_id","sigma"],columns="strategy_id",values=field)
        return wide[policies[0]]-wide[policies[1]]
    old=paired("cumulative_profit_archived")
    fresh=paired("cumulative_profit_replayed")
    paired_df=pd.DataFrame({"difference_archived":old,"difference_replayed":fresh}).reset_index()
    paired_df["difference_shift"]=paired_df.difference_replayed-paired_df.difference_archived
    paired_df["sign_changed"]=np.sign(paired_df.difference_archived)!=np.sign(paired_df.difference_replayed)
    paired_df.to_csv(out/"section32_paired_policy_numerical_stability.csv",index=False)
    summary["paired_policy_sign_changes"]=int(paired_df.sign_changed.sum())
    summary["paired_policy_by_sigma"]={}
    for sigma,sub in paired_df.groupby("sigma"):
        summary["paired_policy_by_sigma"][str(sigma)]={
          "archived_mean_difference":float(sub.difference_archived.mean()),
          "replayed_mean_difference":float(sub.difference_replayed.mean()),
          "max_abs_shift":float(sub.difference_shift.abs().max()),
          "sign_changes":int(sub.sign_changed.sum())}
    summary["reproduction_gate"]="PASS" if summary["strict_pass_batches"]==30 else "FAIL"
    summary["mechanism_interpretation_allowed"]=summary["reproduction_gate"]=="PASS"
    (out/"section32_full_sample_gate_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
    return 0

if __name__=="__main__":raise SystemExit(main())

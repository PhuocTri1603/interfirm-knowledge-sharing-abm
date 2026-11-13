"""Compare existing fixed-SIMD outputs to immutable historical archive, without replay."""
import argparse,csv,json,zipfile
from pathlib import Path
from itertools import combinations
import numpy as np
import pandas as pd
from reproduce_paper_section3_2 import compare

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--trials",required=True)
    ap.add_argument("--archive-zip",required=True)
    ap.add_argument("--baseline",default=None)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    paths=sorted(Path(a.trials).rglob("trial.json"))
    if len(paths)<2:
        raise RuntimeError("At least two runner outputs required")
    trials={}
    for path in paths:
        d=json.loads(path.read_text());key=(d["profile"],float(d["sigma"]))
        trials.setdefault(key,[]).append(d)
    reproducible={}
    for key,ds in sorted(trials.items()):
        reproducible[str(key)]=len(ds)==2 and len({d["digest"] for d in ds})==1 and all(d["rounds"]==200 and len(d["rows"])==1800 for d in ds)
    print("REPRODUCIBILITY",json.dumps(reproducible))
    report={"reproducibility":reproducible,"cases":{},"cross_sigma":{},"strict_archive_gate_pass":False,"research_validated":False}
    if not all(reproducible.values()):
        (out/"economic_equivalence.json").write_text(json.dumps(report,indent=2))
        raise RuntimeError("Reproducibility gate failed; archive comparison blocked")
    if a.baseline:
        d=json.loads(Path(a.baseline).read_text());trials[(d["profile"],float(d["sigma"]))]=[d,d]
    originals={};reproduced={}
    with zipfile.ZipFile(a.archive_zip) as z:
        for (profile,sigma),ds in sorted(trials.items()):
            batch=(int(profile[1:])-1)//10
            archive_name=f"sigma_{sigma:g}_batch_{batch:02d}_rounds.csv"
            with z.open(archive_name) as f: orig=pd.read_csv(f)
            orig=orig[orig.profile_id==profile].copy()
            new=pd.DataFrame([{"profile_id":profile,"sigma":sigma,**r} for r in ds[0]["rows"]])
            strict=compare(orig,new)
            keys=["round","strategy_id"]
            x=orig.sort_values(keys).reset_index(drop=True)
            y=new.sort_values(keys).reset_index(drop=True)
            assert len(x)==len(y)==1800 and x[keys].equals(y[keys])
            relative={}
            for field in ("output","price","profit","cumulative_profit"):
                old=x[field].to_numpy(float);now=y[field].to_numpy(float);delta=np.abs(old-now)
                den=np.maximum(np.abs(old),np.abs(now))
                mask=den>1e-6
                relative[field]={"max_absolute":float(delta.max()),"mean_absolute":float(delta.mean()),"weighted_relative":float(delta.sum()/np.abs(old).sum()) if np.abs(old).sum() else None,"max_pointwise_relative_gt_1e-6":float(np.max(delta[mask]/den[mask])) if mask.any() else None}
            pairs=0;flips=0;terminal_flips=0;min_terminal_gap=float("inf");max_terminal_gap_relative=0.
            for round_ in range(1,201):
                xa=x[x["round"]==round_].set_index("strategy_id").cumulative_profit
                ya=y[y["round"]==round_].set_index("strategy_id").cumulative_profit
                for i,j in combinations(sorted(xa.index),2):
                    o=float(xa[i]-xa[j]);n=float(ya[i]-ya[j]);pairs+=1
                    if np.sign(o)!=np.sign(n):
                        flips+=1
                        if round_==200:terminal_flips+=1
                    if round_==200 and o!=0:
                        min_terminal_gap=min(min_terminal_gap,abs(o))
                        max_terminal_gap_relative=max(max_terminal_gap_relative,abs(n-o)/abs(o))
            t0=x[x["round"]==200].set_index("strategy_id").cumulative_profit
            t1=y[y["round"]==200].set_index("strategy_id").cumulative_profit
            winner0=t0.idxmax();winner1=t1.idxmax()
            actions=int((x.action!=y.action).sum())
            ai=int((x.active_ai_count!=y.active_ai_count).sum()+(x.adopted_count!=y.adopted_count).sum())
            report["cases"][f"{profile}|{sigma:g}"]={"strict":strict,"relative":relative,"pairwise_round_comparisons":pairs,"pairwise_sign_flips":flips,"terminal_sign_flips":terminal_flips,"min_terminal_pair_gap":min_terminal_gap,"max_terminal_gap_relative_error":max_terminal_gap_relative,"winner_archive":winner0,"winner_new":winner1,"action_mismatches":actions,"ai_count_mismatches":ai,"ordering_equivalent":flips==0 and actions==0 and ai==0 and winner0==winner1}
            originals[(profile,sigma)]=t0
            reproduced[(profile,sigma)]=t1
            print("CASE",profile,sigma,"strict",strict["pass"],"flips",flips,"actions",actions,"AI",ai,"winner",winner0,winner1,"max_terminal_gap_relative_error",max_terminal_gap_relative)
    for profile in sorted({k[0] for k in trials}):
        for s1,s2 in combinations((.5,1.,2.),2):
            k1=(profile,s1);k2=(profile,s2)
            if k1 not in originals or k2 not in originals:continue
            signs=0;max_error=0.;details={}
            for sid in originals[k1].index:
                effect=float(originals[k2][sid]-originals[k1][sid])
                trial_effect=float(reproduced[k2][sid]-reproduced[k1][sid])
                if np.sign(effect)!=np.sign(trial_effect):signs+=1
                max_error=max(max_error,abs(trial_effect-effect))
                details[sid]={"archive_effect":effect,"new_effect":trial_effect,"sign_changed":bool(np.sign(effect)!=np.sign(trial_effect))}
            report["cross_sigma"][f"{profile}|{s1:g}->{s2:g}"]={"sign_flips":signs,"max_effect_absolute_error":max_error,"strategies":details}
            print("CROSS_SIGMA",profile,s1,s2,"sign_flips",signs,"max_effect_error",max_error)
    report["strict_archive_gate_pass"]=all(c["strict"]["pass"] for c in report["cases"].values())
    (out/"economic_equivalence.json").write_text(json.dumps(report,indent=2))
    print("REPORT_WRITTEN",str(out/"economic_equivalence.json"))
if __name__=="__main__":main()

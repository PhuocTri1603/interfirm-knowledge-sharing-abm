"""Compare independent solver executions without relaxing the baseline gate."""
import argparse,json
from pathlib import Path
import pandas as pd

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--traces",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    dirs=sorted(x.parent for x in Path(a.traces).rglob("optimizer_trace.csv"))
    if len(dirs)<2:
        raise RuntimeError(f"Need at least two independent traces, got {len(dirs)}")
    tables=[pd.read_csv(d/"optimizer_trace.csv") for d in dirs]
    reports=[json.loads((d/"targeted_diagnostic.json").read_text()) for d in dirs]
    env=[(d/"environment.txt").read_text() for d in dirs]
    fields=["round","strategy_id","candidate_index","method","initial_x_hash","x_hash","success","status","nit","nfev"]
    diffs=[]
    for j in range(1,len(tables)):
        left,right=tables[0],tables[j]
        n=min(len(left),len(right))
        for i in range(n):
            changed=[field for field in fields if str(left.iloc[i][field])!=str(right.iloc[i][field])]
            if changed:
                diffs.append(dict(repeat=str(dirs[j].name),call_index=i+1,
                    round=int(left.iloc[i]["round"]),strategy_id=left.iloc[i]["strategy_id"],
                    candidate_index=int(left.iloc[i]["candidate_index"]),fields=",".join(changed),
                    first_input_equal=left.iloc[i]["initial_x_hash"]==right.iloc[i]["initial_x_hash"],
                    first_output_equal=left.iloc[i]["x_hash"]==right.iloc[i]["x_hash"],
                    left_objective=float(left.iloc[i]["objective"]),
                    right_objective=float(right.iloc[i]["objective"])))
                break
        if len(left)!=len(right):
            diffs.append(dict(repeat=str(dirs[j].name),call_index=n+1,fields="solver_call_count",
                              left_count=len(left),right_count=len(right)))
    summary=dict(traces=[str(d) for d in dirs],solver_calls=[len(t) for t in tables],
        first_archived_divergent_rounds=[r["first_divergent_round"] for r in reports],
        environments_identical=len(set(env))==1,
        first_pairwise_solver_differences=diffs,
        reproducibility_gate="NOT_ESTABLISHED" if diffs or any(r["first_divergent_round"] is not None for r in reports)
        else "PASS_FOR_THREE_TARGETED_F011_EXECUTIONS_ONLY",
        research_validated=False)
    (out/"independent_solver_comparison.json").write_text(json.dumps(summary,indent=2)+"\n")
    pd.DataFrame(diffs).to_csv(out/"first_solver_differences.csv",index=False)
    print(json.dumps(summary,indent=2))
if __name__=="__main__": main()

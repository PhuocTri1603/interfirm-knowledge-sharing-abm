"""Compare four independent SLSQP call-two probes, preserving exact numerical evidence."""
import argparse,json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",required=True);ap.add_argument("--out",required=True)
    a=ap.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    files=sorted(Path(a.root).rglob("solver_call2_repeated.json"))
    cases=[]
    for p in files:
        d=json.loads(p.read_text())
        cases.append({"name":p.parent.name,"data":d})
    rows=[]
    for x in cases:
        d=x["data"]
        rows.append({"runner":x["name"],"threads":d["thread_settings"],
                     "x0_hash":d["x0_sha256"],
                     "objective_at_x0":d["input_evaluations"][0]["objective"],
                     "constraint_at_x0":d["input_evaluations"][0]["constraints"],
                     "input_evaluations_identical":d["input_evaluations_identical"],
                     "solution_evaluations_identical":d["solution_evaluations_identical"],
                     "solutions_identical_within_runner":d["solution_hashes_identical"],
                     "max_solution_coordinate_spread":d["max_solution_coordinate_spread"],
                     "solutions":[{"hash":s["x_sha256"],"objective":s["objective"],
                                   "nit":s["nit"],"nfev":s["nfev"],"status":s["status"],
                                   "success":s["success"]} for s in d["solutions"]]})
    all_x0_equal=len({r["x0_hash"] for r in rows})==1
    all_eval_equal=all(r["objective_at_x0"]==rows[0]["objective_at_x0"] and
                       r["constraint_at_x0"]==rows[0]["constraint_at_x0"] for r in rows)
    first_solution_hashes={r["solutions"][0]["hash"] for r in rows}
    summary={"expected_independent_runners":4,"observed":len(rows),
             "initial_x_identical_across_runners":all_x0_equal,
             "initial_objective_and_constraints_identical_across_runners":all_eval_equal,
             "first_solution_identical_across_runners":len(first_solution_hashes)==1,
             "cases":rows,
             "interpretation_limitations":[
                 "Identical evaluations at x0 do not prove identical finite-difference gradients or entire SLSQP evaluation sequences.",
                 "Each repeated minimization starts with the same x0 and captured closure, but repeated calls could modify unobserved closure/global state.",
                 "This targeted probe is not an archive reproduction gate and does not validate the economic mechanism."],
             "research_validated":False}
    (out/"slsqp_call2_comparison.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
    if len(rows)!=4: raise SystemExit(2)
if __name__=="__main__":main()

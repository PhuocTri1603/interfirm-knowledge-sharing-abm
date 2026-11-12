"""Assess representative runs without treating a partial pass as economic validation."""
import argparse,json
from pathlib import Path

PROFILES=("F021","F071","F091")
SIGMAS=(0.5,1.0,2.0)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    root=Path(a.root);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    records=[]
    for profile in PROFILES:
        for sigma in SIGMAS:
            matching=list(root.rglob("targeted_economic_gate.json"))
            found=[]
            for path in matching:
                try:
                    obj=json.loads(path.read_text())
                except (ValueError,OSError):
                    continue
                if obj.get("profile")==profile and obj.get("sigma")==sigma:
                    found.append(obj)
            if len(found)!=1:
                records.append({"profile":profile,"sigma":sigma,"status":"missing_or_duplicate","n_reports":len(found)})
                continue
            report=found[0]
            archive=report.get("archive_gate") or {}
            instrumentation=report.get("instrumentation_gate") or {}
            accounting=report.get("economic_accounting") or {}
            passed=bool(archive.get("pass") and instrumentation.get("pass") and accounting)
            records.append({"profile":profile,"sigma":sigma,
                "status":"pass" if passed else "fail",
                "archive_pass":archive.get("pass",False),
                "instrumentation_pass":instrumentation.get("pass",False),
                "archive_action_mismatches":archive.get("action_mismatches"),
                "archive_ranking_mismatches":archive.get("ranking_mismatches"),
                "archive_max_terminal_profit_difference":archive.get("max_terminal_profit_difference"),
                "firm_rows":accounting.get("rows"),"task_rows":accounting.get("task_rows"),
                "max_cost_identity_error":accounting.get("max_cost_identity_error"),
                "max_profit_identity_error":accounting.get("max_profit_identity_error")})
    all_pass=len(records)==9 and all(x["status"]=="pass" for x in records)
    summary={"expected_cases":9,"passed_cases":sum(x["status"]=="pass" for x in records),
             "all_representative_gates_pass":all_pass,
             "economic_decomposition_permitted":all_pass,
             "full_sample_validated":False,"research_validated":False,
             "cases":records}
    (out/"representative_gate_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
    if not all_pass: raise SystemExit(2)
if __name__=="__main__":main()

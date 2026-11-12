"""Require three independently passing F011 runs before representative profiles are tested."""
import json,sys
from pathlib import Path
root=Path(sys.argv[1])
paths=sorted(root.rglob("targeted_diagnostic.json"))
reports=[json.loads(p.read_text()) for p in paths]
inputs=[(p.parent/"solver_input_002.json").read_text() for p in paths if (p.parent/"solver_input_002.json").exists()]
passing=len(paths)==3 and all(x["first_divergent_round"] is None for x in reports)
input_equal=len(inputs)==3 and len(set(inputs))==1
summary={"independent_runs":len(paths),"archived_first_divergent_rounds":[r["first_divergent_round"] for r in reports],
         "solver_call_2_static_inputs_equal":input_equal,"three_replays_pass":passing,
         "representative_gate":passing and input_equal,"research_validated":False}
out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
(out/"repeatability_gate.json").write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps(summary,indent=2))
if not summary["representative_gate"]:
    sys.exit(2)

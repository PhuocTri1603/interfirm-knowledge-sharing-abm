"""Cross-run comparison of isolated SLSQP numerical forensics."""
import argparse,json
from pathlib import Path
import numpy as np

def first_difference(a,b):
    n=min(len(a),len(b))
    for i in range(n):
        x,y=a[i],b[i]
        if x["kind"]!=y["kind"] or x["x_hash"]!=y["x_hash"] or x["value"]!=y["value"]:
            return {"event":i+1,"left":x,"right":y,
                    "different_input":x["x_hash"]!=y["x_hash"],
                    "different_value":x["value"]!=y["value"]}
    return {"event":n+1,"reason":"length difference"} if len(a)!=len(b) else None

def main():
    p=argparse.ArgumentParser();p.add_argument("--root",required=True);p.add_argument("--out",required=True)
    a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    cases=[{"name":f.parent.name,"data":json.loads(f.read_text())} for f in sorted(Path(a.root).rglob("call2_forensics.json"))]
    comparisons=[]
    for i in range(len(cases)):
        for j in range(i+1,len(cases)):
            l,r=cases[i],cases[j];x=np.asarray(l["data"]["solution"]);y=np.asarray(r["data"]["solution"])
            d=x-y
            comparisons.append({"left":l["name"],"right":r["name"],
                "max_abs_coordinate_distance":float(np.max(np.abs(d))),
                "euclidean_distance":float(np.linalg.norm(d)),
                "relative_euclidean_distance":float(np.linalg.norm(d)/max(1.,np.linalg.norm(x),np.linalg.norm(y))),
                "max_coordinate_index":int(np.argmax(np.abs(d))),
                "objective_difference":float(l["data"]["objective"]-r["data"]["objective"]),
                "initial_two_point_gradient_max_abs_difference":float(np.max(np.abs(
                    np.asarray(l["data"]["derivatives_at_x0"]["2-point"]["gradient"])-
                    np.asarray(r["data"]["derivatives_at_x0"]["2-point"]["gradient"])))),
                "first_evaluation_trace_difference":first_difference(l["data"]["evaluation_trace"],r["data"]["evaluation_trace"])})
    for pair in comparisons:
        left=next(c["data"] for c in cases if c["name"]==pair["left"])
        right=next(c["data"] for c in cases if c["name"]==pair["right"])
        l={e["x_hash"]:e for e in left.get("jacobian_window",[])}
        r={e["x_hash"]:e for e in right.get("jacobian_window",[])}
        shared=sorted(set(l)&set(r))
        comparisons_at_shared=[]
        for h in shared:
            for method in ("2-point","3-point"):
                ld=l[h]["derivatives"][method];rd=r[h]["derivatives"][method]
                lg=np.asarray(ld["objective_gradient"]);rg=np.asarray(rd["objective_gradient"])
                lj=np.asarray(ld["constraint_jacobian"]);rj=np.asarray(rd["constraint_jacobian"])
                comparisons_at_shared.append({"x_hash":h,"method":method,
                    "gradient_max_abs_difference":float(np.max(np.abs(lg-rg))),
                    "jacobian_max_abs_difference":float(np.max(np.abs(lj-rj))) if lj.size else 0,
                    "jacobian_condition_left":ld["jacobian_condition_full"],
                    "jacobian_condition_right":rd["jacobian_condition_full"]})
        pair["shared_window_points"]=len(shared)
        pair["shared_point_derivative_differences"]=comparisons_at_shared
        pair["left_window_jacobian_condition"]=[{"events":e["events"],"condition_2point":e["derivatives"]["2-point"]["jacobian_condition_full"],"condition_3point":e["derivatives"]["3-point"]["jacobian_condition_full"]} for e in l.values()]
        pair["right_window_jacobian_condition"]=[{"events":e["events"],"condition_2point":e["derivatives"]["2-point"]["jacobian_condition_full"],"condition_3point":e["derivatives"]["3-point"]["jacobian_condition_full"]} for e in r.values()]
    summary={"cases":[{"name":c["name"],"threads":c["data"]["threads"],"success":c["data"]["success"],
             "objective":c["data"]["objective"],"nit":c["data"]["nit"],"nfev":c["data"]["nfev"],
             "stationarity_inf_estimate":c["data"]["kkt"]["stationarity_inf_estimate"],
             "complementarity_estimate":c["data"]["kkt"]["complementarity_estimate"],
             "feasibility":c["data"]["solution_feasibility"]} for c in cases],
             "pairwise":comparisons,"research_validated":False,
             "limitations":["Finite-difference KKT residual is approximate and sensitive to active-set threshold.",
                 "Trace records first 160 objective/constraint evaluations; later first differences are not ruled out.",
                 "Diagnostic evaluation of derivatives precedes optimization and may affect stateful functions; compare with previous non-instrumented probe."]}
    (out/"call2_forensic_comparison.json").write_text(json.dumps(summary,indent=2)+"\n")
    for c in comparisons:
        d=c["first_evaluation_trace_difference"]
        print("PAIR",c["left"],c["right"],"max_coordinate",c["max_abs_coordinate_distance"],
              "l2",c["euclidean_distance"],"first_trace_event",d["event"] if d else None,
              "input_changed",d.get("different_input") if d else None,
              "shared_jacobian_points",c["shared_window_points"],
              "max_shared_gradient_difference",max((x["gradient_max_abs_difference"] for x in c["shared_point_derivative_differences"]),default=None))
    if len(cases)!=4:raise SystemExit("Expected four forensic reports")
if __name__=="__main__":main()

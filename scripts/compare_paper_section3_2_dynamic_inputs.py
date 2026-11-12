"""Compare archived F011 diagnostic artifacts, including dynamic closure state and numerical runtime."""
import argparse,hashlib,json,re
from pathlib import Path

def load(p):
    return json.loads(p.read_text()) if p.exists() else None

def sha(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True).encode()).hexdigest()

def diff(a,b,prefix=""):
    if type(a)!=type(b): return [prefix+": type differs"]
    if isinstance(a,dict):
        keys=set(a)|set(b)
        return [s for k in sorted(keys) for s in
                (diff(a[k],b[k],prefix+"."+k) if k in a and k in b else [prefix+"."+k+": missing"])]
    if isinstance(a,list):
        if len(a)!=len(b): return [prefix+": length differs"]
        return [s for i,(x,y) in enumerate(zip(a,b)) for s in diff(x,y,prefix+f"[{i}]")]
    return [prefix] if a!=b else []

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True);p.add_argument("--out",required=True)
    a=p.parse_args();root=Path(a.root);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    dirs=sorted(x.parent for x in root.rglob("targeted_diagnostic.json"))
    if len(dirs)<2: raise RuntimeError("At least two diagnostic artifact folders required")
    items=[]
    for d in dirs:
        report=load(d/"targeted_diagnostic.json")
        record={"name":d.name,"archive_first_divergence":report["first_divergent_round"],
                "solver_calls":report["solver_calls_before_first_divergent_round"]+report["solver_calls_in_first_divergent_round"] if report["first_divergent_round"] else report["solver_calls_before_first_divergent_round"]}
        for filename in ("solver_input_001.json","solver_input_002.json","solver_input_003.json",
                         "candidate_state_001.json","candidate_state_002.json"):
            record[filename]=load(d/filename)
        for filename in ("environment.txt","numerical_runtime.txt","thread_settings.txt"):
            f=d/filename
            record[filename]=f.read_text() if f.exists() else None
        items.append(record)
    comparisons=[]
    for i in range(len(items)):
        for j in range(i+1,len(items)):
            x,y=items[i],items[j]
            comparison={"left":x["name"],"right":y["name"],"archive_match_left":x["archive_first_divergence"] is None,
                        "archive_match_right":y["archive_first_divergence"] is None}
            for filename in ("solver_input_001.json","solver_input_002.json","solver_input_003.json",
                             "candidate_state_001.json","candidate_state_002.json",
                             "environment.txt","numerical_runtime.txt","thread_settings.txt"):
                v,w=x[filename],y[filename]
                comparison[filename]={"present_both":v is not None and w is not None,
                    "equal":v==w,"left_sha256":sha(v),"right_sha256":sha(w),
                    "different_paths":diff(v,w)[:100] if filename.endswith(".json") and v is not None and w is not None else []}
            comparisons.append(comparison)
    result={"profiles":[{"name":v["name"],"archive_first_divergence":v["archive_first_divergence"],
                         "solver_calls":v["solver_calls"]} for v in items],
            "comparisons":comparisons,
            "limitations":["Original historical archive has no SLSQP call inputs or closures.",
                           "Closure serialization captures static snapshots, not all hidden native numerical state.",
                           "Equality of captured inputs does not prove identical objective evaluations.",
                           "A matching F011 run does not validate the entire sample."],
            "research_validated":False}
    (out/"dynamic_state_comparison.json").write_text(json.dumps(result,indent=2)+"\n")
    for c in comparisons:
        print(c["left"],"vs",c["right"],"archived",c["archive_match_left"],c["archive_match_right"])
        for name in ("solver_input_002.json","candidate_state_001.json","numerical_runtime.txt","thread_settings.txt"):
            v=c[name];print(" ",name,"equal",v["equal"],"different_paths",v["different_paths"][:8])
if __name__=="__main__":main()

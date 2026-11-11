"""Aggregate 180k paired round observations; audit decomposition and early/late mechanisms."""
import argparse,csv,glob
from collections import defaultdict
from pathlib import Path

FIELDS=("delta_profit","delta_revenue","delta_variable_cost","delta_adjustment_cost","delta_adoption_cost","delta_capital","delta_labor","delta_quantity","delta_price","quantity_effect","price_effect","interaction_effect","ai_capital","no_capital","ai_price","no_price","ai_quantity","no_quantity","ai_active_players","no_active_players")
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--input",default="results/game1_ai_round_mechanisms/downloads")
 p.add_argument("--out",default="results/game1_ai_round_mechanisms/aggregate")
 a=p.parse_args()
 paths=glob.glob(a.input+"/**/profile_*.csv",recursive=True)
 assert len(paths)==100,f"Expected 100 profile files, found {len(paths)}"
 count=0; groups=defaultdict(lambda:defaultdict(float));n=defaultdict(int)
 # Each round is averaged over 900 matched markets. Periods are 1-20,21-100,101-200.
 for path in paths:
  with open(path,newline="") as f:
   for r in csv.DictReader(f):
    profile=int(r["profile_index"]);sigma=float(r["sigma"]);seed=int(r["seed"]);t=int(r["round"])
    assert 0<=profile<100 and sigma in (.5,1.,2.) and seed in (11,23,47) and 1<=t<=200
    count+=1
    assert abs(float(r["delta_profit"])-float(r["delta_revenue"])+float(r["delta_variable_cost"])+float(r["delta_adjustment_cost"])+float(r["delta_adoption_cost"]))<1e-6
    assert abs(float(r["delta_revenue"])-float(r["quantity_effect"])-float(r["price_effect"])-float(r["interaction_effect"]))<1e-6
    for key in (("round",t),("period","early_1_20" if t<=20 else "middle_21_100" if t<=100 else "late_101_200"),("sigma_period",sigma,"early_1_20" if t<=20 else "middle_21_100" if t<=100 else "late_101_200")):
     n[key]+=1
     for col in FIELDS:groups[key][col]+=float(r[col])
 assert count==180000,f"Expected 180000 paired-round rows, got {count}"
 out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
 for kind,filename in (("round","by_round.csv"),("period","by_period.csv"),("sigma_period","by_sigma_period.csv")):
  data=[]
  for key in sorted((k for k in n if k[0]==kind),key=str):
   assert n[key]==(900 if kind in ("round","period") and key[0]=="round" else n[key])
   data.append(dict(group=kind,key="|".join(map(str,key[1:])),n=n[key],**{col:groups[key][col]/n[key] for col in FIELDS}))
  with (out/filename).open("w",newline="") as f:
   w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
  print("OUTPUT",filename,len(data))
 print("PASS 180000 paired market-round rows, all accounting identities")
if __name__=="__main__":main()

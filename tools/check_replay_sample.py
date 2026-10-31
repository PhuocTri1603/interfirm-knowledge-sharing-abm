"""Independent exact row checks against original CSV for the replay build."""
import argparse,csv,io,json,zipfile
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('archive');parser.add_argument('--data',default='web/data');args=parser.parse_args()
seeds={2026,2075,2125};firms={1,2,3,4};rounds={1,11,20,50,100,200}
def unpack(document):
 if isinstance(document,list):return document
 result=[]
 for values in document['records']:
  r=dict(zip(document['columns'],values));r['technology']=document['technologies'][r['technology']];r['policy']=document['policies'][r['policy']];r['seed']=document['seed'];r['optimal_share'],r['optimal_output']=document['optima'][r['technology']];result.append(r)
 return result
partitions={s:unpack(json.loads((Path(args.data)/f'seed-{s}.json').read_text())) for s in seeds}
lookup={(r['seed'],r['policy'],r['firm_id'],r['round']):r for rows in partitions.values() for r in rows if r['firm_id'] in firms and r['round'] in rounds}
n=0
with zipfile.ZipFile(args.archive) as z, z.open('firm_round_trajectories.csv') as f:
 for row in csv.DictReader(io.TextIOWrapper(f)):
  key=(int(row['seed']),row['policy'],int(row['firm_id']),int(row['round']))
  if key not in lookup:continue
  actual=lookup[key]
  for k,v in row.items():
   expected=(v=='True') if k=='accepted' else v if k in ('policy','technology') else float(v)
   assert actual[k]==expected,(key,k)
  n+=1
assert n==144,n
print('PASS: 144 exact source rows, 3 seeds, 4 technologies, 6 rounds, 2 policies; all 14 fields')

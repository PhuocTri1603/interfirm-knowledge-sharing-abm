"""Build exact, per-seed replay partitions from the verified private artifact."""
import argparse,csv,hashlib,io,json,math,zipfile
from pathlib import Path
DIGEST='5b2438e1bc5cddc297e325357bce729c690f4765bea64dcfa93d4bda13982d44'
SOURCE='40266bf38b644bb169fcb5d1358f9649ab7085cb'
FIELDS=['firm_id','round','technology','candidate_share','candidate_output','accepted','capital_share','current_output','seed','policy','optimal_share','optimal_output','share_distance_to_optimum','output_efficiency_pct']
def convert(row):
    if list(row)!=FIELDS: raise ValueError('Unexpected history schema')
    result={}
    for k,v in row.items():
        if k in ('firm_id','round','seed'): result[k]=int(v)
        elif k=='accepted':
            if v not in ('True','False'): raise ValueError('Invalid boolean')
            result[k]=v=='True'
        elif k in ('technology','policy'): result[k]=v
        else:
            result[k]=float(v)
            if not math.isfinite(result[k]): raise ValueError('Nonfinite value')
    if result['policy'] not in ('random','guided') or result['technology'] not in ('CES','Linear','Leontief','Cobb-Douglas'): raise ValueError('Invalid category')
    if not (1<=result['firm_id']<=100 and 1<=result['round']<=200 and 2026<=result['seed']<=2125): raise ValueError('Invalid identity')
    if not (.05<=result['capital_share']<=.95 and .05<=result['candidate_share']<=.95): raise ValueError('Invalid share')
    return result

def build(archive,output,packed=False):
    digest=hashlib.file_digest(open(archive,'rb'),'sha256').hexdigest()
    if digest!=DIGEST: raise ValueError('Artifact digest mismatch')
    output=Path(output); output.mkdir(parents=True,exist_ok=True)
    manifest={'source_commit':SOURCE,'run':41171674224,'artifact_id':13030944570,'artifact_sha256':digest,'horizon':200,'budget':100,'seeds':[],'partitions':{},'columns':FIELDS,'rows':0}
    with zipfile.ZipFile(archive) as z:
        if z.read('source_commit.txt').decode().strip()!=SOURCE: raise ValueError('Source mismatch')
        metadata=json.loads(z.read('metadata.json'))
        if (metadata['n_firms'],metadata['n_rounds'],metadata['expected_history_rows'])!=(100,200,4000000): raise ValueError('Configuration mismatch')
        current=None; records=[]; completed=set()
        def flush(seed,records):
            keys={(r['policy'],r['firm_id'],r['round']) for r in records}
            if len(records)!=40000 or len(keys)!=40000: raise ValueError('Incomplete/duplicate seed partition')
            if any(sum(r['technology']==tech and r['round']==1 and r['policy']=='random' for r in records)!=25 for tech in ('CES','Linear','Leontief','Cobb-Douglas')): raise ValueError('Unbalanced technology')
            document=records
            if packed:
                technologies=['Cobb-Douglas','Leontief','Linear','CES']
                columns=['firm_id','round','technology','policy','candidate_share','candidate_output','accepted','capital_share','current_output','share_distance_to_optimum','output_efficiency_pct']
                optima={}
                rows=[]
                for r in records:
                    optimum=[r['optimal_share'],r['optimal_output']]
                    if r['technology'] in optima and optima[r['technology']]!=optimum: raise ValueError('Optimum changed')
                    optima[r['technology']]=optimum
                    rows.append([technologies.index(r[k]) if k=='technology' else ['random','guided'].index(r[k]) if k=='policy' else r[k] for k in columns])
                document={'format':'packed-v1','seed':seed,'technologies':technologies,'policies':['random','guided'],'optima':optima,'columns':columns,'records':rows}
            payload=json.dumps(document,separators=(',',':'),allow_nan=False).encode()
            filename=f'seed-{seed}.json'; (output/filename).write_bytes(payload)
            manifest['seeds'].append(seed);manifest['partitions'][str(seed)]={'file':filename,'rows':len(records),'sha256':hashlib.sha256(payload).hexdigest(),'bytes':len(payload)}
            manifest['rows']+=len(records)
        with z.open('firm_round_trajectories.csv') as raw:
            for row in csv.DictReader(io.TextIOWrapper(raw)):
                r=convert(row)
                if current is not None and r['seed']!=current:
                    flush(current,records);completed.add(current);records=[]
                current=r['seed']
                if current in completed: raise ValueError('Noncontiguous seed')
                records.append(r)
            flush(current,records)
    if manifest['seeds']!=list(range(2026,2126)) or manifest['rows']!=4000000: raise ValueError('Incomplete dataset')
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Verified and partitioned',manifest['rows'],'rows across',len(manifest['seeds']),'seeds')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('archive',type=Path);p.add_argument('--output',type=Path,default=Path('web/data'));p.add_argument('--packed',action='store_true');a=p.parse_args();build(a.archive,a.output,a.packed)

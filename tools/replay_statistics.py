"""Seed-level Monte Carlo summaries of matched exported observations."""
import math
from statistics import mean, stdev

TECHNOLOGIES = ['Cobb-Douglas', 'Leontief', 'Linear', 'CES']
T99 = 1.9842169515086827  # two-sided 95% Student t, df=99

def interval(values):
    if len(values) != 100 or not all(math.isfinite(x) for x in values):
        raise ValueError('Expected 100 finite independent seed statistics')
    center = mean(values)
    half = T99 * stdev(values) / math.sqrt(100)
    return {'mean': center, 'low': center-half, 'high': center+half, 'n':100}

def seed_statistics(records, horizon):
    lookup = {(r['policy'],r['firm_id'],r['round']):r for r in records}
    if len(lookup) != len(records) or len(records) != 200*horizon:
        raise ValueError('Incomplete or duplicate seed observations')
    result = {}
    for group in ['All']+TECHNOLOGIES:
        rounds=[]
        for n in range(1,horizon+1):
            pairs=[]
            for firm in range(1,101):
                r,g=(lookup[p,firm,n] for p in ('random','guided'))
                if r['technology'] != g['technology']:
                    raise ValueError('Paired technology mismatch')
                if group=='All' or r['technology']==group: pairs.append((r,g))
            expected=100 if group=='All' else 25
            if len(pairs)!=expected: raise ValueError('Unbalanced technology')
            entry={'random':mean(r['output_efficiency_pct'] for r,g in pairs),
                   'guided':mean(g['output_efficiency_pct'] for r,g in pairs),
                   'advantage':mean(100*(g['current_output']-r['current_output'])/r['current_output'] for r,g in pairs)}
            for threshold in (95,99,99.9):
                a=100*mean(r['output_efficiency_pct']>=threshold for r,g in pairs)
                b=100*mean(g['output_efficiency_pct']>=threshold for r,g in pairs)
                entry[f'r{threshold}']=a;entry[f'g{threshold}']=b;entry[f'd{threshold}']=b-a
            rounds.append(entry)
        result[group]=rounds
    return result

def summarize(seeds,horizon):
    if len(seeds)!=100: raise ValueError('Expected 100 seeds')
    return {group:[{key:interval([s[group][n][key] for s in seeds])
                        for key in seeds[0][group][n]}
                   for n in range(horizon)] for group in ['All']+TECHNOLOGIES}

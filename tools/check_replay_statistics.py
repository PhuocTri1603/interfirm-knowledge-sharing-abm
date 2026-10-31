"""Independent streamed CSV audit of replay population summaries.

Does not import the production builder or replay_statistics. Only the selected
rounds are retained; expected numbers are recomputed from the original ZIP.
"""
import argparse
import csv
import io
import json
import math
from pathlib import Path
import zipfile

TECHNOLOGIES = ('Cobb-Douglas', 'Leontief', 'Linear', 'CES')
ROUNDS = (1, 11, 20, 50, 100, 200)
TOLERANCE = 1e-9


def student_quantile(df=99, probability=.975):
    """Numerically integrate the Student density and invert its CDF.

    Simpson integration avoids reusing the application's hardcoded quantile.
    """
    coefficient = math.exp(math.lgamma((df+1)/2)-math.lgamma(df/2)) / math.sqrt(df*math.pi)

    def cdf(x):
        intervals = 2048
        step = x / intervals
        total = 0.0
        for j in range(intervals+1):
            density = coefficient * (1+(j*step)**2/df)**(-(df+1)/2)
            total += density * (1 if j in (0, intervals) else 4 if j % 2 else 2)
        return .5 + total * step / 3

    low, high = 0., 8.
    for _ in range(55):
        middle = (low+high)/2
        if cdf(middle) < probability:
            low = middle
        else:
            high = middle
    return (low+high)/2


def average(values):
    return math.fsum(values)/len(values)


def confidence(values, quantile):
    if len(values) != 100 or not all(math.isfinite(v) for v in values):
        raise ValueError('Expected 100 finite seed statistics')
    center = average(values)
    variance = math.fsum((v-center)**2 for v in values)/99
    half = quantile * math.sqrt(variance/100)
    return dict(mean=center, low=center-half, high=center+half, n=100)


def audit(archive, data):
    summary = json.loads((Path(data)/'summary.json').read_text())
    horizon = summary['horizon']
    if horizon not in (50, 100, 200):
        raise ValueError('Unexpected horizon')
    rounds = tuple(r for r in ROUNDS if r <= horizon)
    observations = {}
    with zipfile.ZipFile(archive) as z:
        if z.read('source_commit.txt').decode().strip() != summary['source_commit']:
            raise ValueError('Source commit mismatch')
        metadata = json.loads(z.read('metadata.json'))
        if metadata['n_rounds'] != horizon or metadata['n_firms'] != 100:
            raise ValueError('Original artifact configuration mismatch')
        with z.open('firm_round_trajectories.csv') as raw:
            for row in csv.DictReader(io.TextIOWrapper(raw)):
                round_number = int(row['round'])
                if round_number not in rounds:
                    continue
                seed, firm = int(row['seed']), int(row['firm_id'])
                policy, technology = row['policy'], row['technology']
                if not 2026 <= seed <= 2125 or not 1 <= firm <= 100:
                    raise ValueError('Unexpected source observation identity')
                if policy not in ('random', 'guided') or technology not in TECHNOLOGIES:
                    raise ValueError('Unexpected source category')
                key = (seed, round_number, firm, policy)
                if key in observations:
                    raise ValueError(f'Duplicate source key: {key}')
                output, efficiency = float(row['current_output']), float(row['output_efficiency_pct'])
                if not math.isfinite(output) or not math.isfinite(efficiency) or output <= 0:
                    raise ValueError('Nonfinite or nonpositive sampled output')
                observations[key] = technology, output, efficiency
    if len(observations) != 100*100*2*len(rounds):
        raise ValueError('Incomplete sampled source records')

    quantile = student_quantile()
    comparisons, max_error = 0, 0.
    for group in ('All',)+TECHNOLOGIES:
        for round_number in rounds:
            values = {}
            for seed in range(2026, 2126):
                pairs = []
                for firm in range(1, 101):
                    random = observations[seed, round_number, firm, 'random']
                    guided = observations[seed, round_number, firm, 'guided']
                    if random[0] != guided[0]:
                        raise ValueError('Paired technology mismatch')
                    if group == 'All' or random[0] == group:
                        pairs.append((random, guided))
                if len(pairs) != (100 if group == 'All' else 25):
                    raise ValueError('Unexpected group population')
                statistics = {
                    'random': average([r[2] for r, g in pairs]),
                    'guided': average([g[2] for r, g in pairs]),
                    'advantage': average([100*(g[1]-r[1])/r[1] for r, g in pairs]),
                }
                for threshold in (95, 99, 99.9):
                    random_rate = 100*sum(r[2] >= threshold for r, g in pairs)/len(pairs)
                    guided_rate = 100*sum(g[2] >= threshold for r, g in pairs)/len(pairs)
                    statistics['r'+str(threshold)] = random_rate
                    statistics['g'+str(threshold)] = guided_rate
                    statistics['d'+str(threshold)] = guided_rate-random_rate
                for metric, value in statistics.items():
                    values.setdefault(metric, []).append(value)
            for metric, seed_values in values.items():
                expected = confidence(seed_values, quantile)
                actual = summary['groups'][group][round_number-1][metric]
                for field, value in expected.items():
                    error = abs(actual[field]-value)
                    if not math.isfinite(actual[field]) or error > TOLERANCE:
                        raise AssertionError((group, round_number, metric, field, actual[field], value, error))
                    comparisons += 1
                    max_error = max(max_error, error)
    print(json.dumps(dict(status='PASS', horizon=horizon, rounds=rounds,
                          sampled_rows=len(observations), comparisons=comparisons,
                          max_absolute_error=max_error, tolerance=TOLERANCE,
                          independent_t99=quantile)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--data', required=True, type=Path)
    arguments = parser.parse_args()
    audit(arguments.archive, arguments.data)

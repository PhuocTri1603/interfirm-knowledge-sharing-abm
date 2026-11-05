"""Paired CES/AI-shock economic experiments, isolated from diagnostic fixtures.

Explicit *provisional* comparative-static model, not calibrated economics.
A=1 and alpha=0.5 throughout. AI changes sigma, not A. Each agent
selects a feasible (K,L) plan under fixed factor prices. Market demand is
P(Q)=max(0,(a-Q)/b). Payoff=P(Q)*q - wL-rK.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import fsum, isfinite
from random import Random

from interfirm_abm.task_ces_reference import ces_output


@dataclass(frozen=True)
class CESExperiment:
    sigma_before: float = 0.7
    sigma_after: float = 1.5
    ai_round: int = 101
    rounds: int = 200
    capital_price: float = 1.0
    labor_price: float = 1.0
    demand_intercept: float = 900.0
    demand_slope: float = 100.0
    seed: int = 17

    def __post_init__(self):
        values = (self.sigma_before, self.sigma_after, self.capital_price,
                  self.labor_price, self.demand_intercept, self.demand_slope)
        if not all(isfinite(x) and x > 0 for x in values):
            raise ValueError("positive finite economic parameters required")
        if self.rounds < 2 or not 1 < self.ai_round <= self.rounds:
            raise ValueError("AI shock must occur after round 1 and within horizon")
        if type(self.seed) is not int or self.seed < 0:
            raise ValueError("seed must be nonnegative integer")


PLANS = ((1., 3.), (2., 2.), (3., 1.), (4., 2.), (2., 4.))


def _seed(master: int, agent: int) -> int:
    return int.from_bytes(sha256(f"{master}|{agent}".encode()).digest()[:8], "big")


def simulate(spec: CESExperiment, *, ai: bool, players: int = 64,
             learning: str = "trial_error", epsilon: float = .15,
             temperature: float = 1.) -> dict:
    if players < 2 or not 0 <= epsilon <= 1 or temperature <= 0:
        raise ValueError("invalid simulation controls")
    if learning not in ("optimization", "trial_error", "softmax"):
        raise ValueError("peer imitation requires an approved observation regime")
    rngs = [Random(_seed(spec.seed, i)) for i in range(players)]
    histories = [dict() for _ in range(players)]
    last_price = 2.
    rows = []
    for t in range(1, spec.rounds + 1):
        sigma = spec.sigma_after if ai and t >= spec.ai_round else spec.sigma_before
        decisions = []
        for i in range(players):
            options = []
            for k, l in PLANS:
                output = ces_output(k, l, sigma, a=1., alpha=.5)
                expected = last_price * output - spec.capital_price*k - spec.labor_price*l
                # adaptive own-history feedback, only for previously observed choices
                score = histories[i].get((k, l), (0., 0))[0] / histories[i][(k, l)][1] if (k, l) in histories[i] else expected
                options.append((k, l, output, score))
            if learning == "optimization":
                chosen = max(range(len(options)), key=lambda j: (options[j][3], -j))
            elif learning == "trial_error":
                chosen = rngs[i].randrange(len(options)) if rngs[i].random() < epsilon else max(range(len(options)), key=lambda j: (options[j][3], -j))
            else:
                from math import exp
                peak = max(x[3] for x in options)
                weights = [exp((x[3] - peak) / temperature) for x in options]
                draw = rngs[i].random() * fsum(weights)
                chosen = len(options)-1
                for j, weight in enumerate(weights):
                    draw -= weight
                    if draw < 0:
                        chosen = j
                        break
            decisions.append(options[chosen])
        q_total = fsum(d[2] for d in decisions)
        price = max(0., (spec.demand_intercept - q_total)/spec.demand_slope)
        total_profit = 0.
        total_k = total_l = 0.
        for i, (k, l, q, _) in enumerate(decisions):
            profit = price*q - spec.capital_price*k - spec.labor_price*l
            old_sum, old_n = histories[i].get((k,l), (0., 0))
            histories[i][(k,l)] = (old_sum+profit, old_n+1)
            total_profit += profit
            total_k += k
            total_l += l
        rows.append({"round":t,"ai":ai,"sigma":sigma,"price":price,
                     "quantity":q_total,"total_profit":total_profit,
                     "capital":total_k,"labor":total_l,"capital_labor_ratio":total_k/total_l})
        last_price = price
    return {"rows":rows,"seed":spec.seed,"ai":ai,"learning":learning,
            "model_status":"provisional_ces_comparative_static_not_research_validated"}


def paired_counterfactual(spec: CESExperiment, **kwargs) -> dict:
    treated = simulate(spec, ai=True, **kwargs)
    control = simulate(spec, ai=False, **kwargs)
    before = slice(0, spec.ai_round-1)
    after = slice(spec.ai_round-1, None)
    def avg(rows, key, window):
        sample = rows[window]
        return fsum(x[key] for x in sample)/len(sample)
    metrics = {}
    for key in ("quantity","total_profit","capital_labor_ratio","price"):
        metrics[key] = {
            "pre_difference":avg(treated["rows"],key,before)-avg(control["rows"],key,before),
            "post_difference":avg(treated["rows"],key,after)-avg(control["rows"],key,after),
        }
    return {"spec":spec,"treated":treated,"control":control,"metrics":metrics,
            "identification":"paired simulated counterfactual; not causal evidence about real firms"}


def robustness(seeds=(11,17,23,31,47), sigma_after_values=(1.2,1.5,2.0),
               players=64, rounds=200):
    from dataclasses import replace
    baseline = CESExperiment(rounds=rounds, ai_round=rounds//2+1)
    results = []
    for sigma in sigma_after_values:
        for seed in seeds:
            spec = replace(baseline, seed=seed, sigma_after=sigma)
            comparison = paired_counterfactual(spec, players=players)
            results.append({"seed":seed,"sigma_after":sigma,**{
                "delta_"+key:values["post_difference"] for key,values in comparison["metrics"].items()
            }})
    return results

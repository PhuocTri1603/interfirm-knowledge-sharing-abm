"""Nine-strategy Game 1 experimental runner. Research validation pending.

L3: uniform / output-maximizing / net-profit-maximizing.
L4: labor-only / task unit-cost / whole-firm local-profit search.
Shared epsilon-greedy constant-step action values, including shutdown.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from math import fsum, isfinite
from random import Random

import numpy as np
from scipy.optimize import minimize

from interfirm_abm.task_a5_normalized import technology_for_profile
from interfirm_abm.task_based_firm import TaskAllocation

TASKS = tuple(f"T{i:02d}" for i in range(1, 21))
L3 = ("uniform", "productivity", "cost_adjusted")
L4 = ("no_automation", "cost_based", "profit_based")
BUDGETS = (0.30, 0.48, 0.66, 0.84)
ACTIONS = ("shutdown", "b1", "b2", "b3", "b4")


@dataclass(frozen=True)
class Game1Params:
    demand_intercept: float
    demand_slope: float
    wage: float
    rental: float
    adjustment_delta: float
    adoption_fee: float
    eta: float
    epsilon: float
    seed: int = 11

    def __post_init__(self):
        values = (self.demand_intercept, self.demand_slope, self.wage,
                  self.rental, self.adjustment_delta, self.adoption_fee,
                  self.eta, self.epsilon)
        if any(not isfinite(v) for v in values):
            raise ValueError("parameters must be finite")
        if min(values[:4]) <= 0 or min(values[4:6]) < 0:
            raise ValueError("invalid economic parameters")
        if not 0 < self.eta <= 1 or not 0 <= self.epsilon <= 1:
            raise ValueError("invalid learning parameters")


def strategy_ids():
    return tuple((a, b) for a, b in product(L3, L4))


def zero_plan():
    return tuple(TaskAllocation(t, 0., 0.) for t in TASKS)


def adjustment(plan, previous, p):
    return p.adjustment_delta * (
        p.wage * fsum(abs(a.labor - b.labor) for a, b in zip(plan, previous))
        + p.rental * fsum(abs(a.capital - b.capital) for a, b in zip(plan, previous))
    )


def plan_cost(plan, previous, adopted, p):
    new = frozenset(a.task_id for a in plan if a.capital > 1e-9 and a.task_id not in adopted)
    variable = p.wage * fsum(a.labor for a in plan) + p.rental * fsum(a.capital for a in plan)
    return variable + adjustment(plan, previous, p) + p.adoption_fee * len(new), new


def allocate(firm, tech, modes, l3, budget, price, previous, adopted, p):
    """Numerical constrained allocation. Solver failure is explicit, never silently accepted."""
    tasks = firm.tasks
    indices_l = [j for j in range(20) if not modes[j]]
    indices_k = [j for j in range(20) if modes[j]]
    cap_l = budget * firm.labor_endowment if indices_l else 0.
    cap_k = budget * firm.capital_endowment if indices_k else 0.
    if l3 == "uniform":
        return tuple(TaskAllocation(t.task_id,
            cap_l / len(indices_l) if j in indices_l else 0.,
            cap_k / len(indices_k) if j in indices_k else 0.)
            for j, t in enumerate(tasks))
    indices = indices_l + indices_k
    if not indices:
        return zero_plan()
    bounds = [(0., cap_l if j in indices_l else cap_k) for j in indices]
    init = np.array([cap_l / len(indices_l) if j in indices_l else cap_k / len(indices_k)
                     for j in indices], dtype=float)
    def to_plan(z):
        amounts = {j: max(0., float(v)) for j, v in zip(indices, z)}
        return tuple(TaskAllocation(t.task_id,
            amounts.get(j, 0.) if j in indices_l else 0.,
            amounts.get(j, 0.) if j in indices_k else 0.)
            for j, t in enumerate(tasks))
    def objective(z):
        plan = to_plan(z)
        q = tech.output_from_allocation(firm, list(plan))
        if l3 == "productivity":
            return -q
        cost, _ = plan_cost(plan, previous, adopted, p)
        return cost - price * q
    constraints = []
    if indices_l:
        positions = tuple(indices.index(j) for j in indices_l)
        constraints.append({"type": "eq" if l3 == "productivity" else "ineq",
            "fun": (lambda z, ix=positions, cap=cap_l: sum(z[k] for k in ix) - cap)
            if l3 == "productivity" else
            (lambda z, ix=positions, cap=cap_l: cap - sum(z[k] for k in ix))})
    if indices_k:
        positions = tuple(indices.index(j) for j in indices_k)
        constraints.append({"type": "eq" if l3 == "productivity" else "ineq",
            "fun": (lambda z, ix=positions, cap=cap_k: sum(z[k] for k in ix) - cap)
            if l3 == "productivity" else
            (lambda z, ix=positions, cap=cap_k: cap - sum(z[k] for k in ix))})
    # SLSQP is deterministic for fixed inputs; finite-difference derivative near
    # CES boundaries can fail. Such failures must be surfaced, not treated as results.
    result = minimize(objective, init, method="SLSQP", bounds=bounds,
                      constraints=constraints, options={"maxiter": 250, "ftol": 1e-9})
    if not result.success:
        raise RuntimeError(f"L3 optimizer failed: {result.message}")
    plan = to_plan(result.x)
    firm.evaluate_allocation(list(plan))
    return plan


def candidate(firm, tech, l3, l4, budget, price, previous, adopted, p, last_modes=None):
    tasks = firm.tasks
    old_modes = tuple(a.capital > 1e-9 for a in previous) if last_modes is None else last_modes
    def evaluate(modes):
        plan = allocate(firm, tech, modes, l3, budget, price, previous, adopted, p)
        q = tech.output_from_allocation(firm, list(plan))
        cost, new = plan_cost(plan, previous, adopted, p)
        return price * q - cost, plan, q, cost, new, tuple(modes)
    if l4 == "no_automation":
        return evaluate((False,) * 20)
    if l4 == "cost_based":
        # Fixed labor-only target at the same action budget, prior to mode selection.
        baseline = allocate(firm, tech, (False,) * 20, l3, budget,
                            price, previous, adopted, p)
        modes = []
        for j, task in enumerate(tasks):
            x = task.labor_productivity * baseline[j].labor
            if not task.automation_eligible or x <= 0:
                modes.append(False)
                continue
            ai_capital = x / task.capital_productivity
            labor_cost = p.wage * baseline[j].labor
            ai_cost = p.rental * ai_capital + (
                0. if task.task_id in adopted else p.adoption_fee)
            # Compare mode-change adjustment for the focal task from prior state.
            old = previous[j]
            labor_cost += p.adjustment_delta * (
                p.wage * abs(baseline[j].labor - old.labor)
                + p.rental * abs(old.capital))
            ai_cost += p.adjustment_delta * (
                p.wage * abs(old.labor)
                + p.rental * abs(ai_capital - old.capital))
            modes.append(ai_cost < labor_cost)
        return evaluate(tuple(modes))
    if l4 != "profit_based":
        raise ValueError("unknown L4")
    modes = list(old_modes)
    # A task may not use AI if technology marks it ineligible.
    modes = [v and t.automation_eligible for v, t in zip(modes, tasks)]
    best = evaluate(tuple(modes))
    while True:
        changed = False
        for j, task in enumerate(tasks):
            if not task.automation_eligible:
                continue
            trial = modes.copy()
            trial[j] = not trial[j]
            proposed = evaluate(tuple(trial))
            if proposed[0] > best[0] + 1e-10:
                modes, best, changed = trial, proposed, True
        if not changed:
            return best


def run_game1(firm, sigma, p, rounds=200):
    if rounds < 1:
        raise ValueError("rounds must be positive")
    tech = technology_for_profile(firm, sigma)
    states = {}
    for l3, l4 in strategy_ids():
        sid = f"L3={l3}|L4={l4}"
        seed = int.from_bytes(sha256(f"{p.seed}|{firm.firm_id}|{sid}".encode()).digest()[:8], "big")
        states[sid] = dict(l3=l3, l4=l4, rng=Random(seed), Q={a: 0. for a in ACTIONS},
                           previous=zero_plan(), modes=(False,) * 20, adopted=frozenset(), profit=0., updates=0)
    rows, markets = [], []
    prior_price = 1.
    for t in range(1, rounds + 1):
        selections = {}
        for sid, s in states.items():
            rng = s["rng"]
            action = rng.choice(ACTIONS) if rng.random() < p.epsilon else max(
                ACTIONS, key=lambda a: (s["Q"][a], -ACTIONS.index(a)))
            if action == "shutdown":
                cost = adjustment(zero_plan(), s["previous"], p)
                chosen = (-cost, zero_plan(), 0., cost, frozenset(), s["modes"])
            else:
                chosen = candidate(firm, tech, s["l3"], s["l4"],
                                   BUDGETS[ACTIONS.index(action) - 1],
                                   prior_price, s["previous"], s["adopted"], p, s["modes"])
            selections[sid] = (action, chosen)
        total_q = fsum(out[2] for _, out in selections.values())
        price = max(0., p.demand_intercept - p.demand_slope * total_q)
        for sid, (action, (_, plan, q, cost, new, modes)) in selections.items():
            s = states[sid]
            reward = price * q - cost
            s["Q"][action] += p.eta * (reward - s["Q"][action])
            s["profit"] += reward
            s["updates"] += 1
            s["previous"] = plan
            if action != "shutdown":
                s["modes"] = modes
            s["adopted"] |= new
            rows.append(dict(round=t, strategy_id=sid, action=action, output=q,
                             price=price, profit=reward, cumulative_profit=s["profit"],
                             adopted_count=len(s["adopted"])))
        markets.append(dict(round=t, quantity=total_q, price=price))
        prior_price = price
    ranking = sorted(((sid, s["profit"]) for sid, s in states.items()),
                     key=lambda v: (-v[1], v[0]))
    return dict(profile_id=firm.firm_id, sigma=sigma, market=markets, players=rows,
                ranking=ranking, feedback_counts={sid: s["updates"] for sid, s in states.items()},
                research_validated=False)

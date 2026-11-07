"""A6 experimental engine: explicit economic parameters, no diagnostic peer leakage.

Demand and stochastic policy parameters are REQUIRED inputs, not approved defaults.
Legacy strategy IDs remain unchanged; L5='price' is interpreted as target-price
ONLY in this A6 engine. Not a Nash-equilibrium solver.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import exp, fsum, isfinite
from pathlib import Path
from random import Random

from interfirm_abm.task_a5_normalized import SIGMA_SCENARIOS, technology_for_profile, TASK_IDS
from interfirm_abm.task_based_firm import TaskAllocation, load_approved_population
from interfirm_abm.task_strategy_engine import strategy_roster, OwnOutcome, choose_self_imitation
from interfirm_abm.task_strategy_actions import build_actions
from interfirm_abm.task_strategy_engine import DecisionInformation
from interfirm_abm.task_economic_policy import MarketObservation
from interfirm_abm.task_l34_economics import L34Parameters, effective_firm, capacity_limited, economic_extra_cost


@dataclass(frozen=True)
class A6Parameters:
    demand_intercept: float
    demand_slope: float
    epsilon: float
    temperature: float
    imitation_probability: float  # legacy API compatibility only; ignored by approved self-imitation
    seed: int
    wage: float = 1.0
    rental: float = 1.0
    adaptive_lambda: float = 0.5

    def __post_init__(self):
        positives = (self.demand_intercept, self.demand_slope,
                     self.temperature, self.wage, self.rental)
        if any(not isfinite(x) or x <= 0 for x in positives):
            raise ValueError("demand, temperature and factor prices must be positive")
        if any(not isfinite(x) or x < 0 or x > 1
               for x in (self.epsilon, self.imitation_probability)):
            raise ValueError("behavior probabilities must be in [0,1]")
        if not isfinite(self.adaptive_lambda) or not 0 <= self.adaptive_lambda <= 1:
            raise ValueError("adaptive_lambda must be in [0,1]")
        if type(self.seed) is not int or self.seed < 0:
            raise ValueError("seed must be nonnegative integer")


# D1/D2 frozen specification. L3/L4 and L6 parameters remain separately experimental.
D2_LABOR_REFERENCE = 51.5
D1_REFERENCE_MARKET_QUANTITY = 256.0


def approved_d1_d2_parameters(*, theta=1.0, kappa=0.5, elasticity=1.0,
                              adaptive_lambda=0.5, epsilon=0.15,
                              temperature=1.0, imitation_probability=0.5, seed=11):
    """Construct approved D1/D2 price parameters, common across all configurations.

    P0=1, Q0=256; elasticity is absolute point elasticity at that anchor.
    theta=w/r; kappa is factor cost at common L*=51.5 divided by P0*Y0.
    """
    if any(not isfinite(v) or v <= 0 for v in (theta, kappa, elasticity)):
        raise ValueError("theta, kappa and elasticity must be positive finite")
    b = 1.0 / (D1_REFERENCE_MARKET_QUANTITY * elasticity)
    a = 1.0 + 1.0 / elasticity
    w = kappa / D2_LABOR_REFERENCE
    return A6Parameters(demand_intercept=a, demand_slope=b,
                        epsilon=epsilon, temperature=temperature,
                        imitation_probability=imitation_probability, seed=seed,
                        wage=w, rental=w / theta, adaptive_lambda=adaptive_lambda)


def reference_allocation(firm):
    """Approved A5 labor-only feasible anchor; y=1 under every sigma."""
    return tuple(TaskAllocation(k, firm.labor_endowment / 20.0, 0.0)
                 for k in TASK_IDS)


def reference_market_quantity(firm, players=256):
    if players <= 0:
        raise ValueError("players must be positive")
    return float(players)  # A5 normalized reference output is exactly one.


def rank_softmax(scores, temperature, rng):
    """Rank not money scale: score values may be tuples (lexicographic)."""
    if not scores or temperature <= 0 or not isfinite(temperature):
        raise ValueError("nonempty scores and positive temperature required")
    ordered = sorted(scores, key=lambda k: (scores[k], k), reverse=True)
    # Exact tie: stable action-id order; ranks start at zero.
    ordered = sorted(scores, key=lambda k: k)
    ordered = sorted(ordered, key=lambda k: scores[k], reverse=True)
    weights = [exp(-j / temperature) for j in range(len(ordered))]
    draw = rng.random() * fsum(weights)
    for k, weight in zip(ordered, weights):
        draw -= weight
        if draw < 0:
            return k
    return ordered[-1]


def _plan_cost(plan, parameters):
    return parameters.wage * fsum(x.labor for x in plan) + parameters.rental * fsum(x.capital for x in plan)


def _candidate_plans(identity, firm, observation, own_history):
    # Reuse L3/L4 feasible allocation proposals but never their legacy
    # L5 reserve prices, valuations, or L6 peer-learning machinery.
    info = DecisionInformation(observation, tuple(own_history))
    return {k: action.allocation for k, action in build_actions(identity, firm, info).items()}


def run_a6_market(firm, sigma, parameters, *, l34_parameters: L34Parameters, rounds=1, identities=None):
    """Execute one shared-technology market with explicit (unapproved) calibration.

    This is an implementation/invariant-test runner, not a validated baseline.
    It can run all 256 players; historical strategy IDs are preserved.
    """
    if not isinstance(l34_parameters, L34Parameters):
        raise ValueError('explicit L3/L4 economic parameters required')
    if sigma not in SIGMA_SCENARIOS or rounds < 1:
        raise ValueError("unsupported sigma or rounds")
    identities = tuple(strategy_roster() if identities is None else identities)
    if not identities or len({x.strategy_id for x in identities}) != len(identities):
        raise ValueError("unique nonempty strategy roster required")
    technology = technology_for_profile(firm, sigma)
    qref = reference_market_quantity(firm, len(identities))
    # D1-A2/A4: P0=1 first-round belief; market prices observed with one-round lag.
    prior_price = 1.0
    # D1-A2: correct own-quantity demand slope, not the legacy half-slope prior.
    prior_slope = parameters.demand_slope
    states = {}
    for identity in identities:
        sid = identity.strategy_id
        seed = int.from_bytes(sha256(f"{parameters.seed}|{firm.firm_id}|{sid}|a6-paired".encode()).digest()[:8], "big")
        states[sid] = dict(identity=identity, rng=Random(seed), profit=0.0,
                           last_q=1.0, price_belief=prior_price, scores={},
                           feedback_count=0, history=[], previous_plan=None, adopted=frozenset())
    market_history = []
    rows = []
    for t in range(1, rounds + 1):
        last = market_history[-1] if market_history else None
        observation = MarketObservation(t, None if last is None else last["price"],
                                        None if last is None else last["quantity"])
        selected = {}
        for sid, state in states.items():
            identity = state["identity"]
            production_firm = effective_firm(firm, identity.L4, l34_parameters)
            candidates = _candidate_plans(identity, production_firm, observation, state["history"])
            if identity.L3 == "capacity":
                candidates = {key: capacity_limited(plan, production_firm, firm, l34_parameters)
                              for key, plan in candidates.items()}
            own_belief = state["price_belief"] if identity.L5 == "adaptive" else (
                prior_price if last is None else last["price"])
            scores, predicted_profits = {}, {}
            for key, plan in candidates.items():
                # A5 references remain fixed to the original configuration.
                q = technology.output_index(production_firm.evaluate_allocation(list(plan)))
                adjustment, adoption, _ = economic_extra_cost(
                    identity, plan, state["previous_plan"], firm, state["adopted"], l34_parameters)
                cost = _plan_cost(plan, parameters) + adjustment + adoption
                if identity.L5 == "cournot" or identity.L5 == "price":
                    # D1-A2: forecast changes only from own lagged quantity.
                    # At t=1, last_q=1 and prior_price=1.
                    predicted_price = max(0.0, own_belief - prior_slope * (q - state["last_q"]))
                else:
                    predicted_price = own_belief
                predicted_profits[key] = predicted_price * q - cost
                if identity.L5 == "price":
                    # D1-A3: cost-based 10% markup target, not Bertrand pricing.
                    target = 1.1 * cost / q if q > 0 else float("inf")
                    scores[key] = (-abs(predicted_price - target), predicted_profits[key])
                else:
                    scores[key] = (predicted_profits[key],)
            # Stage 1: participation; shutdown is never given a fake price distance.
            best_predicted = max(predicted_profits.values())
            if best_predicted <= 0:
                chosen = None
            else:
                # Stage 2: L6 selects among production actions.
                rng = state["rng"]
                ordered = sorted(scores, key=lambda k: k)
                ordered.sort(key=lambda k: scores[k], reverse=True)
                preferred = ordered[0]
                if identity.L6 == "optimization":
                    chosen = preferred
                elif identity.L6 == "trial_error":
                    chosen = rng.choice(ordered) if rng.random() < parameters.epsilon else preferred
                elif identity.L6 == "softmax":
                    chosen = rank_softmax(scores, parameters.temperature, rng)
                elif identity.L6 == "imitation":
                    # Approved Game 1 rule: repeat own best realized action.
                    # Only completed-round own history is available here.
                    chosen = choose_self_imitation(tuple(state["history"]), ordered, preferred)
                else:
                    raise ValueError("unknown L6")
            plan = candidates[chosen] if chosen is not None else reference_allocation(firm)
            if chosen is None:
                plan = tuple(TaskAllocation(k, 0.0, 0.0) for k in TASK_IDS)
            q = technology.output_index(production_firm.evaluate_allocation(list(plan)))
            adjustment, adoption, unlocks = economic_extra_cost(
                identity, plan, state["previous_plan"], firm, state["adopted"], l34_parameters)
            cost = _plan_cost(plan, parameters) + adjustment + adoption
            selected[sid] = (chosen, q, cost, plan, unlocks, adjustment, adoption)
        total_q = fsum(v[1] for v in selected.values())
        price = max(0.0, parameters.demand_intercept - parameters.demand_slope * total_q)
        total_profit = 0.0
        for sid, (chosen, q, cost, plan, unlocks, adjustment, adoption) in selected.items():
            profit = price * q - cost
            state = states[sid]
            state["profit"] += profit
            state["last_q"] = q
            if chosen is not None:
                state["previous_plan"] = plan
                state["adopted"] = state["adopted"] | unlocks
            if state["identity"].L5 == "adaptive":
                lam = parameters.adaptive_lambda
                state["price_belief"] = (1.0 - lam) * state["price_belief"] + lam * price
            # Exactly one realized feedback for chosen production action.
            if chosen is not None:
                state["history"].append(OwnOutcome(t, chosen, profit))
                state["feedback_count"] += 1
            total_profit += profit
            rows.append(dict(round=t, strategy_id=sid, action=chosen or "shutdown",
                             quantity=q, cost=cost, adjustment_cost=adjustment,
                             adoption_cost=adoption, price=price, profit=profit,
                             cumulative_profit=state["profit"]))
        market_history.append(dict(round=t, quantity=total_q, price=price, profit=total_profit))
    ranking = sorted(((sid, state["profit"]) for sid, state in states.items()),
                     key=lambda pair: (-pair[1], pair[0]))
    return dict(profile_id=firm.firm_id, sigma=sigma, reference_quantity=qref,
                market=market_history, players=rows, ranking=ranking,
                feedback_counts={sid: state["feedback_count"] for sid, state in states.items()},
                research_validated=False, status="A6_EXPLICIT_PARAMETERS_UNVALIDATED")


def approved_profiles():
    root = Path(__file__).resolve().parents[2] / "data" / "firms"
    return load_approved_population(root / "task_based_100_firms_profiles.csv",
                                    root / "task_based_100_firms_tasks.csv")

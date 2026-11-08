"""Instrument actual SLSQP/COBYQA calls without changing their outputs.

Checks convergence flags, primal feasibility, objective recomputation, and
solver failure frequencies. Does NOT certify global optimality or KKT.
"""
import argparse
import csv
from collections import Counter
from pathlib import Path

import numpy as np
import interfirm_abm.game1_nine_strategy as engine
from interfirm_abm.task_a6_market import approved_profiles

ORIGINAL_MINIMIZE = engine.minimize


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile-index", type=int, default=0)
    ap.add_argument("--sigma", type=float, choices=(.5, 1., 2.), default=2.)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--out", default="results/game1_solver_audit")
    args = ap.parse_args()
    firm = approved_profiles()[args.profile_index]
    calls = []
    def instrument(fun, x0, **kwargs):
        result = ORIGINAL_MINIMIZE(fun, x0, **kwargs)
        method = kwargs.get("method")
        x = np.asarray(result.x, dtype=float)
        bounds = kwargs.get("bounds", ())
        finite = bool(np.all(np.isfinite(x)) and np.isfinite(result.fun))
        lower = max([0.] + [float(lo)-float(v) for v,(lo,hi) in zip(x,bounds)])
        upper = max([0.] + [float(v)-float(hi) for v,(lo,hi) in zip(x,bounds)])
        residuals = []
        for c in kwargs.get("constraints", []):
            value = float(c["fun"](x))
            residuals.append(abs(value) if c["type"] == "eq" else max(0.,-value))
        residual = max([lower, upper] + residuals)
        objective_error = abs(float(fun(x)) - float(result.fun)) if finite else float("inf")
        calls.append(dict(method=method, success=int(result.success),
                          status=int(result.status), message=str(result.message),
                          nfev=int(getattr(result, "nfev", -1)),
                          nit=int(getattr(result, "nit", -1)),
                          constraint_residual=residual,
                          objective_error=objective_error,
                          objective=float(result.fun)))
        return result
    engine.minimize = instrument
    try:
        p = engine.Game1Params(2., 1./9., .5/51.5, .5/51.5,
                               .1, .1*.5/20., .1, .15, args.seed)
        result = engine.run_game1(firm, args.sigma, p, rounds=args.rounds, audit=True)
    finally:
        engine.minimize = ORIGINAL_MINIMIZE
    if not calls:
        raise AssertionError("No optimizer calls recorded")
    path = Path(args.out)
    path.mkdir(parents=True, exist_ok=True)
    target = path / f"solver_profile_{args.profile_index}_sigma_{args.sigma:g}_seed_{args.seed}.csv"
    with target.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(calls[0]))
        writer.writeheader()
        writer.writerows(calls)
    successes = [c for c in calls if c["success"]]
    if any(c["constraint_residual"] > 1e-6 or c["objective_error"] > 1e-6 for c in successes):
        raise AssertionError("Successful solver result violates numerical audit tolerance")
    print(f"PASS solver diagnostics: {len(calls)} calls, {len(successes)} successful")
    print("Methods:", dict(Counter(c["method"] for c in calls)))
    print("Failures:", dict(Counter((c["method"], c["message"]) for c in calls if not c["success"])))
    print(f"Artifact: {target}")
    print("WARNING: convergence flag + primal feasibility != KKT or global optimality.")


if __name__ == "__main__":
    main()

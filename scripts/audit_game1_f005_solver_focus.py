"""Focused F005 200-round solver audit, both adoption-fee scenarios.

Instrumentation only; does not modify economic choices or optimizer results.
"""
import argparse
import csv
from collections import Counter
from pathlib import Path
import numpy as np
import interfirm_abm.game1_nine_strategy as engine
from interfirm_abm.task_a6_market import approved_profiles

ORIGINAL = engine.minimize

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--sigma", type=float, choices=(0.5, 1.0, 2.0), default=2.0)
    ap.add_argument("--fee-multiplier", type=int, choices=(1, 3), required=True)
    ap.add_argument("--rounds", type=int, default=200)
    args = ap.parse_args()
    firm = approved_profiles()[4]
    assert firm.firm_id == "F005", firm.firm_id
    calls = []
    def instrument(fun, x0, **kwargs):
        res = ORIGINAL(fun, x0, **kwargs)
        x = np.asarray(res.x, dtype=float)
        bounds = kwargs.get("bounds", ())
        finite = bool(np.all(np.isfinite(x)) and np.isfinite(res.fun))
        violations = [0.]
        for v, (lo, hi) in zip(x, bounds):
            violations.extend([max(0., float(lo)-v), max(0., v-float(hi))])
        for constraint in kwargs.get("constraints", []):
            value = float(constraint["fun"](x))
            violations.append(abs(value) if constraint["type"] == "eq" else max(0., -value))
        residual = max(violations)
        error = abs(float(fun(x))-float(res.fun)) if finite else float("inf")
        calls.append(dict(call=len(calls)+1, method=kwargs.get("method"),
                          success=int(res.success), status=int(res.status),
                          message=str(res.message), nfev=int(getattr(res,"nfev",-1)),
                          nit=int(getattr(res,"nit",-1)),
                          constraint_residual=residual, objective_error=error,
                          objective=float(res.fun), finite=int(finite)))
        return res
    engine.minimize = instrument
    try:
        p = engine.Game1Params(2., 1./9., .5/51.5, .5/51.5, .1,
                               .1*.5/20.*args.fee_multiplier, .1, .15, args.seed)
        result = engine.run_game1(firm, args.sigma, p, rounds=args.rounds, audit=True)
    finally:
        engine.minimize = ORIGINAL
    if not calls:
        raise AssertionError("No optimizer calls")
    output = Path("results/game1_f005_solver_focus")
    output.mkdir(parents=True, exist_ok=True)
    stem = f"F005_sigma_{args.sigma:g}_seed_{args.seed}_fee_{args.fee_multiplier}"
    with (output / f"{stem}_solver.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(calls[0]))
        writer.writeheader()
        writer.writerows(calls)
    with (output / f"{stem}_rounds.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(result["players"][0]))
        writer.writeheader()
        writer.writerows(result["players"])
    failed = [c for c in calls if not c["success"]]
    bad = [c for c in calls if c["success"] and
           (not c["finite"] or c["constraint_residual"]>1e-6 or c["objective_error"]>1e-6)]
    print(f"F005 sigma={args.sigma} seed={args.seed} fee={args.fee_multiplier}: "
          f"{len(calls)} calls, {len(failed)} unsuccessful, {len(bad)} invalid successful results")
    print("Methods:",dict(Counter(c["method"] for c in calls)))
    print("Failures:",dict(Counter(c["message"] for c in failed)))
    if bad:
        raise AssertionError(f"{len(bad)} successful solver outputs failed feasibility/accounting")
    print("PASS successful solver outputs feasible and objective consistent.")
    print("LIMITATION: not a KKT or global-optimality certificate; "
          "failed starts may be rescued by other starts.")

if __name__ == "__main__":
    main()

---
name: simulation-validation
description: Verify ABM implementation, invariants, economic logic, edge cases, data exports and interpretation independently of green CI.
---
# Simulation Validation

## Trigger
Use when changing Python code, validating model behavior, checking simulation artifacts, or interpreting apparent convergence.

## Procedure
1. Read production, firm, learning, simulation and optimum implementations plus relevant tests.
2. Check numerical domains: finite nonnegative K/L, valid shares, positive budget, finite outputs, feasible optima and all production-function edge cases.
3. Check state transitions: `K+L=B`; accepted candidate iff strict output improvement; rejected candidate leaves current allocation/output unchanged; accepted output nondecreasing for deterministic fixed technology.
4. Check assignment and pairing: 100 firms imply 25 per technology; no duplicate firm/round/policy/seed keys; identical initial conditions across matched policies; candidate count equals configured rounds.
5. Check results: expected rows `seeds*firms*rounds*policies`; paired rows `seeds*firms*rounds`; no missing values; output efficiency <=100% within tolerance; no impossible shares.
6. Run `python -m pytest -q` for code changes and focused smoke checks before full runs. Inspect actual CI job logs, not just top-level status.
7. For convergence, examine threshold achievement, right-censoring and time profiles. Do not infer universal convergence from mean near-optimal output.
8. Report failures with minimal reproducible example, suspected cause, scope of impact, fix proposal and rerun requirements. Economic changes require researcher approval.

## Completion
Validation report identifies code revision, tests actually run, data checks, failed assertions, unresolved threats and whether results are fit for interpretation.

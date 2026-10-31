---
name: research-audit
description: Independently audit consistency across research decisions, economic equations, code, tests, Monte Carlo artifacts, figures and scholarly claims.
---
# Research Audit

## When to use
At milestone completion, before publishing results, after significant model changes, and before marking a research game complete.

## Procedure
1. Freeze audit scope: branch, commit, documents, source files, test logs, datasets and figures. Record inaccessible evidence.
2. Check decision ledger versus implemented mechanisms. Flag unapproved changes and unimplemented claims.
3. Map each equation/parameter/agent rule to code and tests. Verify default versus experiment overrides.
4. Verify experimental controls, paired seeds, units, sample sizes, time horizons, missingness, uniqueness, bounds and expected row counts.
5. Independently recalculate a sample of primary numerical claims from raw data, including interval aggregation and technology breakdowns.
6. Audit references: existence, accurate metadata, source relevance, strength of evidence and novelty statements.
7. Audit website data lineage and sample rendered values if visualization is in scope.
8. Classify findings **critical / major / minor / informational**; report evidence, impact, remediation and owner. Do not silently repair economic mechanisms.
9. Re-run or verify tests after permitted fixes; distinguish **passed**, **failed**, **not run**, and **not verifiable**.

## Output
Audit report with scope, evidence table, findings, remaining risks and explicit sign-off recommendation.

## Acceptance
No unaddressed critical issue for sign-off; a green workflow alone never suffices. Game 1 remains open until model docs, literature and real-data website are independently reviewed.

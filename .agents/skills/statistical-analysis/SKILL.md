---
name: statistical-analysis
description: Analyze matched ABM Monte Carlo results, convergence, uncertainty, heterogeneity and sensitivity without pseudoreplication or unsupported causal claims.
---
# Statistical Analysis

## When to use
After simulation outputs are validated, and whenever producing numerical claims, figures, intervals or convergence findings.

## Inputs
Exact source commit; experiment configuration; raw firm-round and paired outputs; metadata; declared estimands; analysis environment.

## Procedure
1. Read research-governance, experiment-design, simulation-validation and reproducibility skills. Verify data integrity before statistics.
2. Declare the estimand and aggregation unit. For matched Random–Guided comparisons compute firm–seed paired differences, then aggregate by seed before calculating across-seed uncertainty. Never treat 10,000 firm–seed rows as 10,000 independent Monte Carlo replications.
3. Report both absolute efficiency differences (percentage points) and relative output advantage (percent) with distinct names and formulas. Do not interchange them.
4. Describe distribution and heterogeneity by production technology and seed; include mean, median, dispersion, and uncertainty appropriate to design.
5. For convergence, specify threshold (e.g. 95%, 99%, 99.9%), first-hit time, right-censoring, share attained by horizon and horizon sensitivity. Distinguish attainment from proof of asymptotic convergence.
6. Use matched comparisons and seed-level intervals; check whether results depend on outliers, parameters, horizon, and choice of outcome. Label exploratory comparisons.
7. Generate tables and plots directly from verified data; attach data provenance, calculation code and figure-ready units. Reconcile published numbers to raw files.

## Output
Analysis notebook/script or reproducible commands; summary tables; figures with source labels; uncertainty; sensitivity; caveats and interpretation.

## Acceptance
All reported statistics can be regenerated from cited artifacts and exact code; no pseudoreplication, invented p-values or unsupported generalization.

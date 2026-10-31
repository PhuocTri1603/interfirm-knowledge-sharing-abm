---
name: experiment-design
description: Pre-specify agent-based simulation comparisons, matched controls, outcomes, horizons, Monte Carlo uncertainty and sensitivity before running.
---
# Experiment Design

## Trigger
Use before adding or changing simulation experiments, treatments, hypotheses, parameter sweeps or outcome metrics.

## Procedure
1. Define research question, estimand, hypothesis and mechanism being isolated; distinguish exploration from confirmatory experiments.
2. Specify unit of analysis (firm, firm–seed, round, seed), randomization, comparison pairing and independence assumptions.
3. Declare all treatments and controls: production types, initialization, budget, candidate opportunities, information, randomness and acceptance rule.
4. State exact seeds, seed-generation procedure, firms/type, horizon, policy parameters, outcome definitions and data schema **before execution**.
5. For Game 1 baseline, compare Random vs Guided using matched randomness; preserve one candidate per firm per round, 100 seeds and horizons 50/100/200 unless researcher approves otherwise.
6. Define pre-run validation criteria, primary and secondary outcomes, convergence thresholds, censoring treatment, confidence interval aggregation and multiple-comparison caveats.
7. Estimate resource requirements; use smoke tests before full Monte Carlo; register experiment identifier and output directory.
8. Review with researcher before changing the economic mechanism or declaring a new treatment.

## Cautions
- A shared A multiplier without other changes may scale output without changing the theoretical optimal capital share.
- Monte Carlo seeds, not correlated firms within a seed, should be the main independent replication unit for confidence intervals.
- Threshold attainment and average efficiency answer different questions.
- Do not reinterpret horizon sensitivity as evidence of knowledge transfer.

## Completion
A reproducible protocol exists with controls, estimands, failure conditions and expected outputs prior to full run.

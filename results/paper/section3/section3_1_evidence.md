# Section 3.1 — Nine-policy evidence (not manuscript conclusions)

**Original source commit:** `c614b86d9192a57fb402b4772b3c3bb6bf80b79f`; **run:** #42463803820; **artifact:** 13618500797. Re-analysis of existing original outputs, not a new experiment.

**Original parameters and seed:** `{"adjustment_delta": 0.1, "adoption_fee": 0.0025, "demand_intercept": 2.0, "demand_slope": 0.1111111111111111, "epsilon": 0.15, "eta": 0.1, "rental": 0.009708737864077669, "seed": 11, "wage": 0.009708737864077669}`. 100 synthetic profiles × 3 σ × 9 simultaneously competing policies × 200 rounds.

## Integrity
540,000/540,000 firm-rounds; 2,700 complete trajectories; 0 duplicate keys; 60000 market-rounds.
Max cumulative-profit error 4.547e-13; terminal sum error 4.547e-13; same-market price spread 0.000e+00; inverse-demand error 6.661e-16.

## Statistical definitions
Technology profiles are the paired units, n=100 per sigma. SD is sample SD (ddof=1); intervals mean ± 1.96×SD/√100 (descriptive synthetic-profile variation, not empirical causal confidence intervals). All 36 unordered policy pairs per sigma are in the pairwise CSV. Ties within absolute 1e-8 share first-place credit equally; positive profit means >1e-8.

## Numerical findings
- σ=0.5: highest mean profit: `L3=cost_adjusted|L4=profit_based` (149.1409); highest win credit: `L3=cost_adjusted|L4=profit_based` (61/100). These are different metrics.
- σ=1: highest mean profit: `L3=cost_adjusted|L4=profit_based` (151.8405); highest win credit: `L3=cost_adjusted|L4=profit_based` (56/100). These are different metrics.
- σ=2: highest mean profit: `L3=productivity|L4=profit_based` (120.9071); highest win credit: `L3=cost_adjusted|L4=profit_based` (31/100). These are different metrics.

## Figure captions
1. **Figure 3.1:** Mean cumulative realized profit and profile interquartile range for all nine policies, faceted by σ.
2. **Figure 3.2:** Within-profile paired differences for four comparisons; boxplots show median, IQR, 1.5-IQR whiskers and outliers, diamonds show means; dashed zero reference.
3. **Figure 3.3:** Fractionally tie-adjusted first-place profile credit by policy and σ, distinct from mean profitability.

## Interpretation and limits
The data support descriptive heterogeneity of realized profitability across policies and sigma conditions. They do not establish global optimality or independently identify price causation. Original parameters are exploratory and uncalibrated; only seed 11 was run. Original round panels omit revenue and disaggregated variable/adjustment/adoption costs, so independent component-level profit accounting cannot be verified from these artifacts. Original engine uses endogenous market clearing and learning; rankings are conditional on this design. Cross-workflow numerical reproducibility of separate later AI/no-AI experiments remains unresolved. `research_validated=false`.

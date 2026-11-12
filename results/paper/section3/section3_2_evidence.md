# Section 3.2 — Technological substitutability: evidence audit

## Provenance
Archived original run #42463803820, commit `c614b86d9192a57fb402b4772b3c3bb6bf80b79f`, seed 11; Section 3.1 baseline. No simulation rerun or economic-model changes.

## Observed results
Paired unit: one of 100 synthetic technology profiles, identical profile IDs across three sigma conditions. 200 rounds per policy trajectory. A = cost_adjusted + profit_based; B = productivity + profit_based.

| Sigma | Mean profit A | Mean profit B | Mean D=A−B | Median D | SD D | D>0 | D<0 | Descriptive 95% interval |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 0.5 | 149.141 | 90.482 | 58.659 | 45.480 | 79.262 | 80 | 20 | [43.124, 74.195] |
| 1 | 151.840 | 92.011 | 59.829 | 38.715 | 85.526 | 77 | 23 | [43.066, 76.592] |
| 2 | 119.040 | 120.907 | -1.867 | 2.007 | 55.612 | 52 | 48 | [-12.767, 9.033] |

## Within-profile sigma contrasts

- D_1_minus_D_0.5: mean 1.1698; median 3.4350; SD 32.4164; positive 69/100; negative 31/100; 95% descriptive [-5.1838, 7.5234].
- D_2_minus_D_1: mean -61.6962; median -33.2850; SD 71.1572; positive 11/100; negative 89/100; 95% descriptive [-75.6430, -47.7494].
- D_2_minus_D_0.5: mean -60.5264; median -43.3673; SD 58.5184; positive 6/100; negative 94/100; 95% descriptive [-71.9960, -49.0568].

## Accounting and data availability
Archived round fields: profile ID, sigma, round, policy, action, output, market price, realized profit, cumulative profit, adopted task count and active AI task count. Revenue is computed exactly as P×q. **Total cost is only an algebraic residual** P×q−profit, NOT an independent cost measurement. Variable input cost, adjustment cost, adoption cost, K, L, task-level allocation and task-level normalized activities are absent. No independent component-level profit reconciliation is possible.

AI active task count measures **actual use**, not eligible task count; adopted_count is cumulative history, not currently active modes. Share of eligible tasks automated is unavailable. Action-budget category is observed, but does not measure actual capacity utilization. Changes in adopted_count can describe first-time adoption events, not reversals of mode or total switching frequency.

## Technology comparability
Original generator calls approved_profiles() and uses technology_for_profile(firm,sigma). The A5 reference_for_profile(firm) is fixed from each profile's labor productivities and labor endowment, independent of sigma. Sigma changes the CES aggregator, not the stored task productivity coefficients. The same profile IDs occur across sigma. Endogenous choices, prices and learning paths may nevertheless differ.

## Figure captions
**Figure 3.4.** Panels (a)–(c) show mean realized output per round, mean **algebraically implied** total cost per round (Pq−profit), and mean 200-round cumulative realized profit, respectively, for the two profit-based automation policies at sigma 0.5, 1 and 2. Means are across 100 matched synthetic technology profiles per condition, seed 11. Colors identify allocation policy. Panel (b) is not an independent component-cost measurement; no causal cost mechanism is established.

**Figure 3.5.** Evidence-availability panel. The archived original experiment does not include normalized activity or resource allocation for any of the 20 tasks. Accordingly no task distribution is displayed. Reconstructing task rankings from aggregate output would be invalid. A verified baseline-matched instrumented reproduction is required before this figure can become a task-level plot.

**Figure 3.6.** Panels (a) and (b) explicitly indicate unavailable capital and labor utilization. Panel (c) plots the mean number of tasks actively using AI per firm-round for both policies and all three sigma conditions. Values are averages over 100 synthetic technology profiles and 200 rounds; counts (0–20) do not represent eligibility, adoption history, or capital stock. No uncertainty interval is inferred from missing K/L measurements.

## Mechanism-consistent patterns
Any co-movement of observed output, AI task use and profit across sigma is descriptive and may be consistent with alternative production-allocation mechanisms. It cannot independently identify task concentration, cost channels or price causation.

## Unresolved mechanisms and validation status
To test task-level concentration and component costs, instrument the original engine observationally (task activity, task K/L, eligible task count, new adoptions, switching, variable/adjustment/adoption costs, actual capacity). A rerun may be called a reproduction only after matching original per-profile/sigma/policy cumulative profits and rankings at documented numerical tolerances. Existing cross-workflow numerical solver discrepancies make this a substantive gate, not a formality. Single-seed synthetic outcomes are not externally calibrated; no global optimum or causal identification is claimed. `research_validated=false`.

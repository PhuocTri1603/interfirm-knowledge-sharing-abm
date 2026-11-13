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


## 2026-11-13 — Figures 3.4–3.8 artifact-backed QA update

**Important:** This addendum supersedes only the earlier evidence-availability statements for Figures 3.6 and proposed additional figures; it does not change the original Section 3.1 or the archived Section 3.2 baseline.

- **Figure 3.4 PASS (100 profiles, seed 11):** Direct audit of original 540,000-row archive artifact **13618500797**, frozen commit `c614b86d9192a57fb402b4772b3c3bb6bf80b79f`. Focal A/B trajectories are 120,000 player-rounds. Output and `Pq-profit` implied total cost are mean per round, first within profile, then over 100 profiles; cumulative profit is 200-round sum averaged over profiles. Original Section 3.1 comparison remains unchanged. Implied cost is NOT an independent cost-component measurement.
- **Figure 3.5 PENDING:** Verified dynamic-audit ZIPs contain `firm_dynamics.csv`, `market_dynamics.csv`, `dynamic_gate.json`, `audit_report.json` only. No independently gate-passed task-level `task_id` allocation / productivity / eligibility / activity / capital-by-task file was established from these 12 artifacts. Do not show a 20-task allocation plot or claim full task-level mechanism validation.
- **Figure 3.6 PASS (four-profile observational scope):** The twelve cases in run [#43363627323](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/43363627323) have `audit_vs_prior_fixed_simd_pass=true`, 1,800 firm-round records each, and exact `Pq - variable_cost - adjustment_cost - adoption_cost = profit` within 1e-8. Mean `capital_used`, `labor_used` and `active_ai_count` for A/B were plotted for F011/F021/F071/F091 and σ=.5,1,2. Capital/labor figures show **absolute utilized inputs per round**, not capital stock or endowment-utilization ratios. AI is **active task count**, not AI capital expenditure or cumulative adoption. No task-level AI-capital allocation was measured.
- **Proposed Figure 3.7 PASS (four profiles):** 2,400 market-rounds (4×3×200) from the same twelve dynamic artifacts. Exact check `P=max(0,2-Q/9)`, max absolute residual **4.440892098500626e-16**. Plots show per-round `quantity` and `price` without interpolation.
- **Proposed Figure 3.8 PASS (100 profiles):** Full-sample revaluation/ranking artifact **14015257527**, workflow [#43378220484](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/43378220484). σ=1→2 totals (full precision): reference-price quantity **+39820.182457077586**, cost contribution **−12863.74929060052**, target-quantity price revaluation **−33631.65745222476**, observed delta profit **−6675.224285747697**; identity residual **9.094947017729282e-13**. Fixed-price change = **+26956.433166477066**. The exact components explain the apparent 0.01 discrepancy from independently rounded display values. The 100-profile archive supplies `C=Pq-profit` implied costs, not independent task cost breakdowns. The repricing is ex-post accounting, NOT a causal price intervention.
- **Numbering governance:** 3.7 and 3.8 are **provisional identifiers** until Paper Agent verifies no conflict with Section 3.3. Section 3.3 remains untouched. Figures 3.1–3.3 remain untouched.
- **Validation limits:** Historical strict archive equivalence has unresolved cases; single seed 11 is not multi-seed robustness; `research_validated=false`.

**English captions for manuscript:**

**Figure 3.4. Production and profitability across technological substitutability.** Panels report (a) mean realized output per round, (b) mean algebraically implied total cost per round (market revenue minus realized profit), and (c) mean cumulative realized profit over 200 rounds, for cost-adjusted/profit-based (A) and productivity/profit-based (B) strategies across 100 matched synthetic technology profiles at σ=0.5, 1, and 2 (seed 11). Costs in panel (b) are not independently measured input-cost components.

**Figure 3.5. Task-level allocation across technologies (pending).** No task-level figure is released because the available validated dynamic artifacts do not report independently verified allocations for all 20 tasks. Aggregate output and AI-task counts cannot identify task-level allocation.

**Figure 3.6. Capital, labor, and active AI-task use in validated dynamic cases.** Mean capital and labor inputs utilized per round and the mean number of tasks actively using AI are compared for strategies A and B across σ=0.5, 1, and 2 in profiles F011, F021, F071, and F091 (200 rounds per profile–σ; seed 11). Capital and labor are flow input quantities, not capital stocks or utilization ratios; active AI tasks are not AI capital use or cumulative adoption. Results are limited to these four profiles.

**Proposed Figure 3.7. Aggregate supply and endogenous settlement prices.** Round-level aggregate market supply and settlement price are plotted for F011, F021, F071, and F091 under σ=0.5, 1, and 2 (200 rounds per scenario; seed 11). Prices obey the existing settlement rule `P=max(0,2-Q/9)`; the trajectories describe four validated simulation configurations, not a population-wide causal response.

**Proposed Figure 3.8. Ex-post fixed-price profit decomposition across 100 configurations.** The σ=1→2 change in aggregate realized profit is decomposed into output changes evaluated at σ=1 prices, negative changes in algebraically implied total costs, and repricing of σ=2 output at observed σ=2 rather than σ=1 market prices. Totals cover 100 synthetic technology profiles, nine strategies, and 200 rounds (seed 11). This is an exact accounting identity conditional on observed choices, not a new equilibrium or identified causal mediation effect.

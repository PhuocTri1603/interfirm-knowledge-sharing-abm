# Game 1 — Normalized Economic Specification

**Status:** Draft — Pending Researcher Approval  
**Date:** 2026-11-06  
**Scope:** 100 configurations × 256 strategies × 20 tasks × 200 rounds.

This document records proposed economic units and equations. It does not change executable code or approve parameters.

## Dimensions

| Variable | Economic meaning | Units |
|---|---|---|
| K | Capital services allocated | capital-service units/period |
| L | Labor allocated | labor hours/period |
| q_j | Activity of task j | task-j units/period |
| aK_j | Capital task productivity | task-j units/capital-service unit |
| aL_j | Labor task productivity | task-j units/labor hour |
| Y | Final output | final-product units/period |
| P | Output price | monetary units/final-product unit |
| w | Labor unit cost | monetary units/labor hour |
| r | Capital-service unit cost | monetary units/capital-service unit |
| C | Total period cost | monetary units/period |
| pi | Period profit | monetary units/period |

Monetary units are abstract; capital stocks must not be confused with per-period capital services. Normalization does not mean setting all variables equal to one.

## Proposed production specification

Each task uses labor or eligible capital, subject to aggregate K/L constraints. For task j: q_j = aL_j L_j (labor mode) or q_j = aK_j K_j (eligible capital mode).

Normalize task activity by positive reference q0_j: x_j=q_j/q0_j. Candidate CES final output:

Y = Y0 [sum_j omega_j x_j^rho]^(1/rho), rho=(sigma-1)/sigma, sigma>0, omega_j>0, sum_j omega_j=1.

At sigma=1: Y = Y0 product_j (q_j/q0_j)^omega_j.

The ratios are dimensionless; Y has the units of Y0. The references, weights, elasticity and handling of zero activity are pending approval. Equal weights and sigma=1 are diagnostic, not validated.

## Cost and automation

C = w sum_j L_j + r sum_j K_j + F + C_AI + C_adj.

For activity q>0, benchmark labor and capital task costs are w*q/aL and r*q/aK. Eligible automation may incur an additional adoption cost f_AI. This is a comparison benchmark, not an assumption that strategies choose optimally. Investment in owned capital requires a separate stock transition to avoid double counting rental and purchase costs.

## Market and profits

Diagnostic inverse demand: P(Q)=max(0,A-BQ). A has units money/output; B has money/output squared for quantities per fixed period.

Actual sales satisfy 0<=S_i<=Y_i. Revenue R_i=P_tr,i*S_i; profit pi_i=R_i-C_i; cumulative payoff Pi_i=sum over 200 rounds of pi_i.

Separate price expectations, posted offers/reserves and actual transaction prices. The current diagnostic market does not establish a validated Cournot or price-setting equilibrium.

## Information and timing

Each strategy observes permitted lagged information, forms expectations, selects task modes and K/L allocations, produces, trades, receives realized profit and updates its learning state. No current-round clearing price may be used before market clearing. L3–L6 strategies need not know the globally optimal allocation.

## Validation gates

Test dimensional invariance under labor, capital, output and monetary-unit changes (including transforming payoff-scale Softmax temperature); invariance under consistent task-reference changes; accounting identities; resource feasibility; zero output and fixed costs; no price look-ahead; and correct handling of profit ties.

Within a configuration, compare raw cumulative profit. An optional cross-configuration score (Pi - median(Pi))/IQR(Pi) is undefined when IQR=0 and must not replace raw profit.

**Not yet approved:** normalized reference quantities, CES parameters, input prices, AI costs, investment dynamics, transaction mechanism, outside option and optional normalized score.

**Current diagnostic assumptions:** pure-mode tasks, geometric-mean aggregation, w=r=1, linear inverse demand, heuristic L4 thresholds and first-period expected price 2.0.

**Do not tune parameters to force positive profits or artificial differences. Keep research_validated: false.**

## Literature

- Varian, H. R. (1992). *Microeconomic Analysis* (3rd ed.).
- Acemoglu, D., & Restrepo, P. (2019). Automation and New Tasks. *Journal of Economic Perspectives*, 33(2), 3–30. https://doi.org/10.1257/jep.33.2.3
- Acemoglu, D., & Restrepo, P. (2022). Tasks, Automation, and the Rise in U.S. Wage Inequality. *Econometrica*, 90(5), 1973–2016. https://doi.org/10.3982/ECTA19815

The specific 20-task and 256-strategy formulation is a proposed project model, not a verbatim reproduction of these papers.


## Research decision register — completing the 12-item checklist (2026-11-06)

**Authority:** principal researcher decides economic assumptions. This register is a specification and decision proposal, not approval or a change to executable simulation. Preserve the existing sections above and the canonical Game 1 design file.

| Item | Status | Proposed completion / acceptance criterion |
|---|---|---|
| 100 configurations × 256 strategies × 200 rounds | Retain | For every configuration, reset 256 players; run 200 rounds; keep config, strategy and round IDs in all outputs. |
| 20 tasks per configuration | Retain | Each configuration supplies exactly 20 shared task definitions; test IDs, eligibility, productivity and allocation constraints. |
| Acemoglu–Restrepo task-based direction | Retain | Automation changes the feasible task execution set; do not relabel an aggregate TFP multiplier as task automation. The discrete simulation is not claimed to be a full A–R equilibrium. |
| Pure-mode execution | Provisional / theoretical review | Within task, either labor or eligible capital supplies activity. Test feasibility. Compare later with mixed-mode extension as a separately identified sensitivity scenario; do not switch without approval. |
| Normalized money and input units | Proposed convention | Declare one production/accounting period, labor hours, capital-service units, task-specific activity units, final-product units, abstract money units. Distinguish capital stock and service flow. Test rescaling invariance. |
| Normalized CES with q0_j and Y0 | Proposed | Use dimensionless x_j=q_j/q0_j and output scale Y0; preserve actual output under consistent reference transformation. Must specify reference construction and zero-activity behavior before adoption. |
| sigma=1, equal task weights | Existing diagnostic, not approved | Report as benchmark only. Compare other sigma and task-weight cases only as clearly labeled sensitivity experiments after defining their economic meaning. |
| r=1, w=1 | Existing diagnostic, not calibrated | Interpret as candidate normalized input-service prices, not empirical prices. Cost of used resources vs endowed idle resources, wage/rental numeraire and ownership require decision. |
| Linear inverse demand | Existing diagnostic, not approved | Define P(Q)=max(0,A-BQ) with dimensioned A,B; clarify whether Q is offered or sold quantity, demand intercept, market capacity and price-taking vs strategic quantities. |
| AI adoption and adjustment costs | Pending design | Distinguish one-off adoption charge, recurring AI operating charge, adjustment cost and capital investment expenditure. Track whether task eligibility changes and when charges are incurred. Do not invent numerical coefficients. |
| Price matching and demand allocation | Pending design | Specify offers/reserve prices, acceptance condition, quantity sold, rationing, realized price, and market clearing; require revenue uses realized transaction price and quantity sold. Separate actual market rule from L5 beliefs. |
| Cumulative profit as Game 1 payoff | Retain | pi_it=realized transaction revenue minus period economic costs; Pi_i=sum_{t=1}^{200} pi_it. Report ties; do not replace with relative scores or discounting without approval. |

### Dimensional equations and accounting identities

For each configuration c, strategy i, task j and period t, capital and labor service allocations are nonnegative and bounded by the configuration-specific available services. Under the **provisional pure-mode** rule, task activity is either aL_cj times labor service or aK_cj times capital service if automation eligible. Task productivity has task-units per input-service-unit dimensions.

Define x_icjt=q_icjt/q0_cj, q0_cj>0. The **candidate**, not yet approved, normalized CES is:
Y_ict=Y0_c*(sum_j omega_j*x_icjt^rho)^(1/rho), rho=(sigma-1)/sigma; sigma>0; omega_j>0; sum_j omega_j=1.
For sigma=1, use Y_ict=Y0_c*product_j(x_icjt^omega_j).
The x values are dimensionless and Y has final-product units. Changing the reference q0 alone while holding Y0 and the representation fixed is **not** generally an invariant transformation; compensate Y0/other parameters as required to represent the same physical production function.

Period accounting is C_ict=w_t*sum_j L_icjt+r_t*sum_j K_icjt+F_ict+C_AI,ict+C_adj,ict; R_ict=P_tr,ict*S_ict; pi_ict=R_ict-C_ict; Pi_ic=sum_t pi_ict. Capital rental rK is not automatically a purchase investment expense. All costs and revenues are in monetary units for the same period.

For a **candidate** inverse-demand benchmark, P_t(Q)=max(0,A_t-B_t*Q), with A in money/output unit and B in money/(output unit)^2 when Q is a quantity per fixed period. If time-rate units are used instead, explicitly carry period duration. Define 0<=S_ict<=Y_ict. The model must choose how total sales and clearing price are jointly determined; do not assume all offered output is sold as an identity without a market rule.

### Timing and information contract

At the start of round t, a player may observe its own endowments, technology as allowed, own past actions and outcomes, and explicitly permitted lagged public/peer signals. It forms expectations, chooses an action, then production occurs. Market demand is settled after all relevant decisions; the transaction price and sales become available only afterward. Profit and learning state update last. Distinguish L5 market expectations from the **actual** market settlement. No look-ahead or unapproved global optimization.

### Minimum verification gates before approving an economic implementation

- Population: 100 configurations, 256 strategy identities per configuration, 20 tasks, 200 rounds.
- Accounting: revenue = transaction price × quantity sold; profit = revenue − all applicable costs; all components in the same monetary unit and period.
- Feasibility: nonnegative inputs, shared K/L limits, automation eligibility, treatment of zero task activity.
- Unit invariance: labor, capital, output and monetary units rescaled with corresponding productivity, prices, inverse-demand coefficients and payoff-dependent learning parameters; compare physical outcomes and decisions.
- Market: quantity sold bounded by produced quantity; consistent clearing and rationing; posted prices have specified economic effects if included.
- Behavior: no current-round price leakage; actions may differ by information and learning; same realized allocation, price and costs imply same profit.
- Analysis: record raw profits, ties and distribution by configuration; sensitivity and Monte Carlo checks precede substantive claims.

### Research approvals still required

1. Do 20 tasks represent indispensable complements (supporting geometric mean), or are some substitutable? Specify zero-task behavior and reference activity q0.
2. Are K and L paid per *used service* or as precommitted endowments? What is the outside option and the cost of idle capacity?
3. Does automation require a one-off cost, recurring cost, capital stock transition, or some combination? How does eligibility evolve?
4. Is Game 1 a single uniform-price quantity-clearing market with heterogeneous *beliefs*, or a market where posted prices genuinely affect matching and realized sales? This choice governs the interpretation of L5.
5. Are linear inverse demand and equal task weights retained only as baseline diagnostic scenarios, or accepted as the main theoretical specification?

**No economic parameter or implementation is modified by this register.** Continue to label research_validated: false.


## Research decision C — configuration-specific task substitution (approved 2026-11-06)

**Approved research choice:** Substitutability among the 20 tasks is heterogeneous across the 100 technological configurations. Each configuration c has its own **across-task** substitution elasticity sigma_c > 0, held common to all 256 strategy identities in that configuration. This decision supersedes the earlier universal sigma=1 interpretation. It does **not** approve numerical sigma_c values, the distribution or assignment algorithm, task weights, reference activities, changes to the 100 existing technology profiles, or a code deployment.

### Mathematical technology specification

For c in {1,...,100}, i in {1,...,256}, j in {1,...,20}, t in {1,...,200}, define normalized activity x_icjt=q_icjt/q0_cj with q0_cj>0. Candidate across-task CES:

Y_ict = Y0_c * (sum_{j=1}^{20} omega_cj * x_icjt^rho_c)^(1/rho_c),
rho_c = (sigma_c-1)/sigma_c,
sigma_c>0, omega_cj>0, sum_j omega_cj=1, Y0_c>0.

For sigma_c=1 use the continuous geometric-mean limit Y_ict=Y0_c*product_j x_icjt^omega_cj. The x terms are dimensionless; Y has final-output units. The elasticity is **between task activities**, not automatically the elasticity between capital and labor within a task. Pure-mode within-task technology and automation eligibility remain separate provisional rules.

### Economic interpretation and zero-task cases

- 0<sigma_c<1: relatively complementary task activities; with any x_j=0, Y=0 in this CES form.
- sigma_c=1: Cobb–Douglas across tasks; any x_j=0 implies Y=0.
- sigma_c>1: more substitutable tasks; with some x_j=0, Y can remain positive if at least one other task has positive activity. All x_j=0 implies Y=0.
- sigma_c approaches zero from above: minimum normalized task activity (Leontief limit under positive weights); sigma_c tends to infinity: weighted arithmetic aggregate of normalized activities (perfect-substitutes limit). These are mathematical limiting cases, not approved finite parameter values.
- For fixed sigma_c, CES is homogeneous of degree one in x. With q0_cj and Y0_c fixed, doubling every task activity doubles final output. This does not by itself establish returns to scale in owned capital stock or investment.
- A zero-task rule is economically consequential: sigma_c>1 permits production without some tasks. If all 20 tasks must be indispensable, the research design must address that contradiction before assigning high-sigma configurations.

### Construction of 100 configurations: design controls, not fabricated values

Preserve the 100 existing F001–F100 task capability profiles, endowments, and automation eligibility. Add a separate, auditable mapping from configuration ID C000–C099 to sigma_c, referencing the existing F profile. Within each configuration, all strategies face the same sigma_c, weights and reference scales. A change in sigma_c changes the final-output aggregation function, **not** task-specific capital or labor productivity coefficients or AI eligibility.

For a clean causal analysis of substitution effects, simply assigning different sigma_c values to the 100 already heterogeneous profiles is **not sufficient**: differences in endowments, task productivity and eligibility will confound sigma comparisons. Pre-specify at least one controlled counterfactual/sensitivity design holding each base profile fixed while varying sigma; this would be additional scenario runs, not a redefinition of the 100 primary configurations. Record base profile, sigma, weights, references and random seed in every output.

### Reference-scale comparability

A proposed calibration convention is to choose positive q0_cj and Y0_c so that at x_j=1 for every task, Y=Y0_c for every sigma_c. This anchors the same reference bundle, but **does not guarantee identical production for nonreference bundles**. Any additional equal-output or equal-cost benchmark normalization must be declared and tested, not assumed. Do not change q0 independently of Y0/technology and claim invariance.

### Numerical and research verification

1. Validate exactly 20 unique task IDs, strictly positive finite sigma_c, q0_cj, Y0_c and omega_cj, weights summing to one, nonnegative finite q_j.
2. At sigma_c=1, compare with the weighted geometric mean; at sigma_c near one, test numerical continuity (use a stable log-sum-exp or equivalent algorithm).
3. Check Y=Y0_c when all x_j=1, Y>=0, monotonicity in task activity, and degree-one homogeneity.
4. Check zero-task behavior separately for sigma<1, sigma=1 and sigma>1; compare near-Leontief and near-linear limits.
5. Check dimensional invariance under consistent rescaling of task units and references, and compare all 256 players under a common configuration technology.
6. Record sigma_c in market/player/ranking results; run controlled counterfactuals holding the same task profiles and endowments fixed before interpreting substitution effects.
7. Re-run A1–A6 accounting, market and behavioral checks after any approved implementation. Do not interpret existing full-sample profits/rankings as results of configuration-specific sigma.

### Implementation boundary and unresolved decisions

The current executable `task_multi_action_diagnostic.py` still sets `TASK_WEIGHTS=1/20` and `sigma=1.0` for every configuration. `task_aggregators.py` already accepts a sigma parameter but does not apply the proposed q0/Y0 normalization. No executable files are modified by this decision record.

Pending researcher decisions: (a) sigma_c sampling/assignment (fixed grid, empirical calibration, or structured scenario design), (b) whether weights remain equal across tasks, (c) construction of q0_cj and Y0_c, (d) whether high-sigma task omission is economically acceptable, and (e) whether any additional nested CES or mixed within-task capital/labor substitution is needed. **research_validated: false.**


## Research decision B — stratified sigma assignment and paired counterfactuals (approved 2026-11-06)

**Decision approved:** Use technology groups and controlled counterfactual tests for across-task substitution elasticity. This specifies experimental architecture only. Numeric elasticity levels, group sizes, assignment to C000–C099, weighting, and task reference calibration are **not yet approved**. No simulation code or data files change.

### Main experiment: 100 configurations

Maintain the canonical one-to-one mapping C000–C099 to existing F001–F100 task technology profiles, endowments, and automation eligibility. Each configuration has one shared sigma_c across all 256 strategy identities for all 200 rounds. Group labels:

- G1 complementary: 0 < sigma_c < 1.
- G2 Cobb–Douglas benchmark: sigma_c = 1.
- G3 relatively substitutable: sigma_c > 1.

These are **theoretical strata**, not yet numeric bins with assigned counts. Do not fabricate sigma values or assume 100 is divisible into equal-sized groups. To ensure all three groups are represented, an assignment plan must explicitly state counts and values and be approved before implementation. The baseline 100 configurations remain 100, not 100 multiplied by the number of sigma scenarios.

### Controlled paired counterfactuals (separate experiment)

For each selected base configuration c, run the **same** initial technology profile, K/L endowments, task eligibility, weights, task references, demand parameters, learning parameters, strategy roster, and accounting rules under at least two pre-specified sigma conditions. For any strategy s, define DeltaPi_cs(a,b)=Pi_cs(sigma_b)-Pi_cs(sigma_a), with Pi cumulative realized profit over 200 rounds. The paired comparison is a model-based intervention on across-task substitutability, **not an empirical causal estimate**.

Use common random-number streams / paired seeds where feasible, preserving the same exogenous stochastic draws across scenarios. The **endogenous** K/L choices, market price, sales, profits, beliefs, and learning must be allowed to change in response to sigma; fixing them would block the economic mechanisms being studied. When simulation paths consume random draws differently, document the randomization coupling and conduct additional independent-seed robustness checks.

A controlled sigma comparison is not obtained by comparing a G1 configuration against a different G3 configuration: those also differ in initial endowments, task productivity and eligibility. Main-experiment group contrasts are descriptive unless further identified by a controlled design.

### Data contract for a future mapping (not created yet)

For each primary configuration, a future mapping table should include:
config_id, original_profile_id, sigma_group, sigma_value, sigma_assignment_rule, task_weight_scheme, task_reference_scheme, output_reference_scheme, source_or_rationale, approval_status.

For each counterfactual scenario, additionally include:
base_config_id, scenario_id, counterfactual_sigma, paired_seed_id, fixed_parameters_fingerprint, changed_parameters, and output artifact IDs.

The mapping should be auditable, deterministic after approval, and independent of observed strategy payoffs. Do not choose sigma assignments by maximizing simulated profits or creating desired winners.

### Candidate estimands and analysis plan

1. Within-configuration strategy comparison: Pi_cs(sigma_c) and rank with ties, not only a single winner.
2. Paired sigma effect for a fixed base technology: DeltaPi_cs(a,b) above.
3. Heterogeneous paired effect by strategy layer L3/L4/L5/L6, while accounting for the 256 strategy identities' interactions in a shared market.
4. Market-level paired differences: total output, price, quantity sold, aggregate profit, and distributional measures. Since strategies interact in a common market, outcomes are **not independent observations across players**; aggregate or cluster uncertainty at the market-run/configuration level.
5. Multiple random seeds, sensitivity to selected sigma levels, and checks that the reference bundle remains anchored consistently.
6. Do not treat 200 periods within a run or 256 strategies sharing one market as 51,200 independent experimental replications.

### Acceptance and numerical verification

- Validate all sigma_c are finite and >0, and each is common to the 256 players in its configuration.
- Validate the group membership inequalities; benchmark group has sigma=1 exactly.
- Preserve 100 primary configurations, 20 tasks, 256 strategies, 200 periods; counterfactual runs must be labeled separately, not mixed into primary 5.12m observations.
- CES reference anchor: when x_j=1 for all j, Y=Y0 for all sigma. Test continuity near sigma=1, limits, monotonicity, homogeneity and sigma-dependent zero-task behavior.
- Keep common task technology and K/L constraints fixed in each paired comparison; record all permitted changes and seed coupling.
- Report market-level and strategy-level outcomes, ties, confidence intervals over independent runs/configurations when justified, and robustness to alternative group boundaries and sigma levels.
- Verify no simultaneous alteration of cost, market clearing, or L3–L6 learning rules in a sigma-only counterfactual.

### Remaining approvals before implementation

A. Choose sigma values or a justified generation rule inside G1/G2/G3, and group counts/assignment for the 100 existing profiles.
B. Choose task weights omega_cj (equal or heterogeneous), task references q0_cj, and output reference Y0_c.
C. Confirm that in G3 some tasks may be skipped while still producing positive final output; this is an implication of the proposed CES with sigma>1.
D. Define the number of base configurations and independent seeds in the counterfactual experiment.
E. Decide whether the 100 main configurations should be balanced across groups or intentionally reflect a documented distribution.

**Current code remains a diagnostic universal sigma=1 benchmark. No code modifications or new simulation results were made. research_validated: false.**


## Research decision — technology-stratified sigma assignment (approved 2026-11-06)

**Approved:** Assign the 100 existing base technology configurations to sigma groups using pre-simulation stratification on initial K/L, task productivity and automation capability. This supersedes an unstratified or purely random assignment. **Not approved:** any numeric sigma values, group counts, concrete C000–C099 assignments, new data or code changes.

### 1. Pre-treatment profile and data provenance

Use the existing 100 F001–F100 records in `data/firms/task_based_100_firms_profiles.csv` and `data/firms/task_based_100_firms_tasks.csv`. Each original profile maps to exactly one primary configuration. Derive covariates using **only original initial attributes**, never simulated profits, winning strategy, post-adoption choices or endogenous prices.

For base profile c define:

- Capital/labor intensity: `KL_c = Kbar_c/Lbar_c` if Lbar>0. For robust comparisons with zero endowments, retain separate `log1p(Kbar)` and `log1p(Lbar)` and an explicit zero-endowment flag; do not silently divide by zero. Because K and L have different units, the ratio requires a stated capital-service/labor unit convention.
- Labor task productivity summary: `muL_c = (1/20) sum_j log(aL_cj)`; capital productivity summary: `muK_c = (1/20) sum_j log(aK_cj)`. The logs require a declared positive reference unit; alternatively use log of dimensionless productivity relative to common reference coefficients. Record task-level dispersion (standard deviation of those logs), not just their means.
- Automation eligibility share: `E_c = (1/20) sum_j 1[e_cj=1]`. This is an eligibility indicator, **not** the realized automation rate.
- Potential relative task efficiency: summarize `log((aK_cj/aK_ref)/(aL_cj/aL_ref))` only after specifying consistent reference input units. Do not compare raw capital and labor productivity numerically as if their units were identical.

These variables represent **stratification covariates**, not additional production inputs. Keep the original 20 task records unchanged.

### 2. Assignment procedure (to be executed only after researcher approves group counts)

1. Freeze and fingerprint the 100 original profiles and derived covariate table.
2. Pre-register the primary covariates: capital/labor intensity or separate endowment logs, mean task productivity for labor and capital, and automation eligibility share. Dispersion and relative efficiency are diagnostics/optional secondary covariates.
3. Standardize covariates over the 100 base profiles, recording the centering and scaling constants. For constant covariates, omit from the balance objective and report the reason.
4. Construct a reproducible stratified allocation to G1 (sigma<1), G2 (sigma=1), G3 (sigma>1). Candidate algorithm: constrained minimization of between-group standardized mean differences, subject to pre-approved group capacities, with deterministic seed and documented tie-breaking. A blocked assignment or seeded optimization is acceptable; it must not use any simulation outcome.
5. Preserve all 100 unique profile IDs exactly once. The same original profile is not reassigned across groups in the primary experiment. Record each group assignment and its reproducible algorithm version.
6. Only **after** group assignment is frozen, map approved numerical sigma values or an approved within-group sampling rule to each configuration. The sigma values must satisfy the group inequalities and be identical for all 256 strategy players within each configuration.
7. Publish a balance report before running any new economic simulation. Reject or flag unacceptable imbalance by a pre-registered criterion; do not reassign based on payoff outcomes.

This design balances **observable initial covariates**, not necessarily all task-level technology differences. It does not itself identify the effect of sigma across distinct configurations.

### 3. Balance metrics and acceptance protocol

For each covariate z and group pair (g,h), compute standardized mean difference:
`SMD_gh(z) = (mean_g(z)-mean_h(z))/sd_all(z)`, with sd_all(z)>0. Report all three pairwise comparisons G1/G2, G1/G3, G2/G3, the maximum absolute SMD, and group means/SDs. Inspect distribution overlap, range, quantiles, and imbalance in automation share and productivity dispersion. Any numeric SMD threshold is a **proposed research tolerance** requiring approval; it is not an automatic proof of balance. Group sizes and optimization objective/weights also require approval.

### 4. Paired counterfactual identification

The primary grouped experiment describes strategy performance under heterogeneous technology; the **paired counterfactual** isolates sigma within the same original profile. For selected c and approved levels sigma_a,sigma_b:
`DeltaPi_cs(a,b) = Pi_cs(sigma_b; F_c, seed)-Pi_cs(sigma_a; F_c, seed)`.
Hold fixed F_c (K/L, 20 task productivities, eligibility), omega, q0, Y0, exogenous demand/cost rules, roster and initial learning states; couple exogenous random draws using documented common random numbers. Allow endogenous task allocations, output, clearing prices, sales, beliefs and learning to respond to changed sigma. Label these as **additional scenarios**, never replace or mix them into the 100 primary configurations.

Because 256 strategies interact in one market, do not treat strategy-round outcomes as independent replications. For uncertainty, use independent simulation seeds and/or base-profile clusters and report the unit of replication. Keep any comparisons between G1/G2/G3 in the primary run descriptive unless supported by the within-profile design.

### 5. Required mapping and audit fields

Planned (not created) mapping columns: `config_id, original_profile_id, Kbar, Lbar, KL_defined, logK, logL, mean_log_aL, mean_log_aK, sd_log_aL, sd_log_aK, eligibility_share, sigma_group, sigma_value, assignment_seed, assignment_algorithm, covariate_version, source_fingerprint, approval_status`.

Planned balance output: `covariate, group, n, mean, sd, min, p25, median, p75, max` and `covariate, group_pair, SMD`.

Planned counterfactual output: `base_config_id, strategy_id, sigma_scenario, seed, 200_round_cumulative_profit, market_output, realized_price, total_sales, total_cost, total_profit, parameter_fingerprint`.

### 6. Explicit unresolved research choices

- Group capacities: equal/nearly equal versus justified unequal proportions; no 34/33/33 choice is implied by this approval.
- Numeric sigma levels or range/sampling method inside G1 and G3; G2 remains exactly 1.
- Relative weights of balancing covariates, SMD tolerance and randomization/optimization procedure.
- Task reference q0_cj, final output reference Y0_c, task weights omega_cj and the high-sigma zero-task implication.
- Number of paired profiles, counterfactual sigma levels and independent seeds.

**Implementation boundary:** No source code, CSV input, sigma assignment table, workflow or model output changed by this documentation update. Existing runs use sigma=1 for all configurations. `research_validated: false`.


## Research decision — unequal sigma-group proportions: evidence review before assignment (2026-11-06)

**Approved direction:** Investigate unequal G1/G2/G3 proportions using the original technology profiles and/or credible literature **before** deciding counts. **No group counts, assignments, sigma values or simulation code changes are approved.**

### Audit of current original population

Read from `data/firms/task_based_100_firms_profiles.csv` (100 records) and `data/firms/task_based_100_firms_tasks.csv` (2,000 task records), branch `game1-economic-policy-interface`, source blob SHAs `54cc888a4594b81fa91984073d18d2807163f37a` and `43c0689a0fa9204512672d8fa81c1922bea2fd54`.

- Original resource orientation: 34 capital-oriented, 32 balanced, 34 labor-oriented.
- K: min 18.73, median 56.24, max 134.72.
- L: min 19.75, median 51.50, max 119.22.
- Original K/L: min 0.331, median 1.0395, max 3.325.
- Automation eligibility share: min 0.10, median 0.30, max 0.60.
- Profile mean labor productivity: min 0.914, median 1.001, max 1.106.
- Profile mean potential capital productivity: min 0.898, median 0.9975, max 1.108.

These are **illustrative/pending-approval** original profiles, not a representative empirical distribution. The 34/32/34 orientation breakdown is **not** evidence for 34/32/34 sigma-group counts.

### Identification limitation

K/L, mean task productivity, dispersion and automation eligibility do not identify the CES **between-task** elasticity sigma. Capital/labor substitution within tasks is a different elasticity. The A–R task framework motivates task allocation and automation but does not, by itself, provide a population distribution of the proposed 20-task sigma_c. Therefore, **do not infer sigma-group frequencies from the existing K/L or automation shares**. A cluster analysis of those features is not an estimate of sigma.

### Literature evidence requirements

Before any evidence-based unequal proportions are approved, require a study to (i) measure substitutability between comparable task outputs, not just K versus L; (ii) state its production aggregation, industry and task definition; (iii) report the sample frame and distribution/uncertainty of elasticities; (iv) justify mapping the empirical tasks to this simulation's 20 tasks; (v) justify mapping its industry composition to the synthetic 100 configurations. Distinguish calibration from externally chosen stress-test scenarios.

Relevant conceptual anchors (not claimed to provide the required group frequencies): Varian, *Microeconomic Analysis*; Acemoglu & Restrepo (2019), JEP 33(2), 3–30; Acemoglu & Restrepo (2022), Econometrica 90(5), 1973–2016.

### Recommended staged design

1. Preserve the original 100 technology profiles; freeze and audit pre-treatment features.
2. Search and critically evaluate empirical studies that estimate **across-task** substitution or comparable production-stage substitution. If credible transferable evidence exists, document mapping and use it as a calibration **proposal**, subject to researcher approval.
3. If no transferable evidence exists, do **not** claim a data-derived unequal group distribution. Treat group proportions as an explicit **experimental design factor** and compare multiple pre-specified allocation scenarios; do not designate any as empirically representative.
4. For any proposed counts (n1,n2,n3), require n1+n2+n3=100 and each group nonempty; then use constrained stratification to balance K/L, task productivity and automation eligibility **conditional on those counts**.
5. For each scenario publish pairwise SMD and overlap diagnostics. A balance algorithm cannot determine the economically correct group proportions.
6. Keep paired within-profile sigma counterfactuals as the main identification strategy; group contrasts alone remain descriptive.

### Research decisions still open

- Empirical target population/industry for any calibration.
- Whether literature offers transferable estimates of between-task sigma.
- If not, which alternative unequal proportions should be treated as scenario analyses, without claiming prevalence.
- Actual sigma values/ranges, weights, q0 and Y0, and zero-task interpretation.

**Status: evidence assessment and baseline audit completed; no allocation selected. No executable files modified; research_validated: false.**


## A5 — technology specification closure and evidence checklist (2026-11-06)

**Scope:** Close the A5 *theoretical specification and audit criteria*, not claim implementation or research validation. Researcher has approved heterogeneous across-task sigma and technology-stratified assignment in principle, but has **not** approved numeric sigma/group shares, task weights, q0/Y0, zero-task economic interpretation, or executable changes. The official A5 gate remains **OPEN** until these are resolved and tests run.

### A5.1 Economic object and theoretical justification

A configuration c maps to one of the original 100 F profiles. Twenty task activities q_cj are produced from feasible allocations of labor or eligible capital. The proposed two-level technology is: (1) task execution/assignment; (2) aggregation of normalized task outputs into final output. The **between-task** CES elasticity sigma_c is distinct from within-task capital/labor substitution or automation eligibility. The CES task aggregator is motivated by Acemoglu & Restrepo (2018), *The Race between Man and Machine*, AER 108(6), 1488–1542, doi:10.1257/aer.20160696; the discrete 20-task and heterogeneous-sigma design is this project's own extension. This is not a replication of their full equilibrium model.

### A5.2 Proposed production and feasibility contract

For each c,i,j,t, choose nonnegative labor l_icjt or capital services k_icjt, subject to sum_j l_icjt <= Lbar_c and sum_j k_icjt <= Kbar_c. Pure-mode is the current **provisional** task assignment rule: labor mode q=aL_cj*l, or capital mode q=aK_cj*k if task j is eligible. A task with no capital eligibility may still be performed by labor. Unused inputs are allowed. Automation *eligibility* is not actual adoption; AI shock, adoption timing, and adoption cost remain A4/other gates, not implicitly solved by A5.

For normalized x=q/q0 with q0_cj>0 and Y0_c>0, proposed final output:
`Y_ict=Y0_c*[sum_j omega_cj*x_icjt^rho_c]^(1/rho_c)`,
`rho_c=(sigma_c-1)/sigma_c`, sigma_c>0, omega_cj>0, sum_j omega_cj=1.
At sigma_c=1 use `Y_ict=Y0_c*prod_j x_icjt^omega_cj`. The aggregator is degree-one homogeneous in q for fixed references, and monotone in each q. At the reference bundle q=q0, Y=Y0 independent of sigma. This anchors a benchmark, **not** output/cost equivalence for other task bundles.

**Critical economic fork:** for sigma<=1, zero activity in any positively weighted task gives zero final output; for sigma>1, a task may be zero while final output stays positive. Researcher must approve whether 20 tasks are substitutable production activities rather than 20 indispensable sequential stages. If all stages must be essential, a single CES with sigma>1 is not an admissible representation; consider nested essential stages with substitutable alternatives *within* stages, subject to separate approval. Do not conceal this issue through epsilon-clipping zero activities.

### A5.3 Relation to earlier production families

The original Cobb–Douglas, Leontief, Linear and CES families describe *properties/functional forms of aggregation*, not four empirically identified within-task technologies. The proposed CES family includes Cobb–Douglas as sigma=1 and approaches Leontief (sigma->0+) and linear aggregation (sigma->infinity) as limits; finite sigma is not exactly either limiting form. If the previously approved Game 1 design requires four **exact** families or multiple L1/L2 technology cells, heterogeneous finite-sigma CES alone does **not** fulfill that requirement. Before declaring A5 closed, reconcile this design with `docs/games/game1/design.md` and the theoretical charter; do not silently drop L1/L2 commitments.

### A5.4 Reference and unit discipline

Task activities q_j may have distinct physical units, so raw summation is invalid without declared common conversion. The ratios x_j=q_j/q0_j are dimensionless. q0_j and Y0 must be derived by an explicit, pre-specified rule independent of strategy winners, profits or post-treatment outcomes. Equal omega=1/20 is a diagnostic benchmark only. A simultaneous change of q units and q0 in the same units leaves x unchanged. A standalone q0 change generally changes the represented technology and must not be called unit invariance.

Check nonnegative finite q; strictly positive finite sigma, q0, Y0, omega; exact 20 task IDs; resource feasibility and eligibility; no fabricated productivity coefficients. Numerical evaluation must be stable near sigma=1 and at zeros. The current `task_ces` implementation is an unnormalized candidate; `task_multi_action_diagnostic.py` still fixes sigma=1.

### A5.5 Sigma design and identification

Approved direction: each of 100 original profiles is mapped once to one of G1 (0<sigma<1), G2 (sigma=1), G3 (sigma>1), with stratification on pre-treatment K/L, task productivity and automation eligibility. Group sizes may be unequal but are **not** identified by those covariates; they require defensible external calibration or explicit sensitivity scenarios. No proportions or sigma numbers have been approved. Preserve within-configuration common technology for all 256 strategies. To identify sigma effects, compare multiple sigma values **within the same base profile**, holding exogenous conditions fixed and allowing endogenous behavior and market outcomes to change.

### A5.6 Executable verification requirements (not yet run for proposed technology)

- T1 population integrity: 100 distinct F profiles, 20 tasks/profile, mapping C000–C099; 256 strategies per configuration.
- T2 task execution: pure-mode feasibility, capital eligibility, shared K/L resource bounds, unused input and zero allocation.
- T3 CES mathematics: sigma<1, sigma=1, sigma>1, continuity near 1, sigma limit checks, reference anchor Y(q0)=Y0, monotonicity, homogeneity and zero-task cases.
- T4 unit consistency: task-specific q and q0 rescale together; output-unit rescaling transforms Y0 and any downstream price/demand parameters; no phantom production changes.
- T5 shared configuration: all 256 players face identical base task coefficients, eligibility, endowments, weights, references and sigma; no unapproved between-player technology variation.
- T6 paired counterfactuals: same base profile and exogenous conditions, different approved sigma; no simultaneous unapproved demand/cost/learning changes.
- T7 regression and integration: production Y is passed consistently to valuation, offers, sales, cost/revenue accounting; A1/A2/A4/A6 remain separate gates.
- T8 governance: preserve historic diagnostic results as sigma=1 only; report test artifacts, seeds, CI links and failures; never set research_validated true based only on unit tests.

### A5 completion criteria

**Specification draft:** complete with equations, interpretation, alternatives, references and test plan (this section).
**Researcher approvals pending:** essential-versus-substitutable tasks; reconciliation with four exact production families/L1–L2; q0/Y0 construction; omega; sigma values and group allocation or explicit sensitivity-only design; pure-mode as final baseline.
**Implementation pending:** approved mapping, normalization, aggregator integration, full validation suite and evidence.
**Gate:** A5 = OPEN / SPECIFIED BUT NOT SCIENTIFICALLY VALIDATED; `research_validated: false`. No simulation code or data modified.


## A5 researcher approval — 20 substitutable production activities (2026-11-06)

**APPROVED:** The 20 tasks represent **production activities**, not 20 indispensable sequential production stages. Their ability to substitute for one another varies with the configuration-specific **between-task** CES elasticity sigma_c. This explicitly resolves the earlier A5 essential-versus-substitutable task interpretation in favor of substitutable activities. It does **not** approve a numerical sigma distribution, group proportions, task weights, q0/Y0 references, pure-mode as final, or code changes.

### Consequences of the approved interpretation

1. Each activity q_j >= 0 contributes to a common final-output index through the proposed CES aggregator. A zero-activity task is an economically admissible **choice/constraint**, not automatically a data error or a forced epsilon replacement.
2. For 0<sigma_c<1 and sigma_c=1, a positively weighted zero task implies Y=0 in the proposed CES; for sigma_c>1, positive output can arise from a strict subset of tasks. This is an implication of the functional form and does not imply that omitting tasks is always privately optimal.
3. The word *substitutable* describes the economic activity set across different sigma regimes; it does **not** imply perfect substitution, nor that all sigma values permit nonzero output with missing activities.
4. Eligibility for capital execution of a task remains separate from substitutability **between** task activities. An automation-ineligible activity can still be performed with labor; dropping a task and automating a task are different decisions.
5. Preserve 20 task identities and original F001–F100 productivity, K/L and eligibility data. No task is deleted from the technology merely because a strategy allocates zero resources to it.
6. Since the output aggregation is CES, sigma=1 is Cobb–Douglas and sigma approaches zero/positive infinity yield Leontief/linear limits. **Finite** sigma in G1/G3 is not exactly Leontief/linear. Earlier exact four-family or L1/L2 technology commitments still need explicit reconciliation, rather than being silently replaced by one CES family.

### Mathematical and behavioral checks to add after implementation approval

- All-zero task activities -> zero output for every finite sigma>0.
- Exactly one zero task with other tasks positive -> zero output for sigma<=1; positive output for sigma>1.
- Strictly positive task activities -> finite positive output; nonnegative activity never decreases output.
- At q=q0, Y=Y0 for all sigma; q0_j and Y0 remain pre-specified reference scales, not fit to winning strategies.
- Feasible zero allocation to an activity must respect the same K/L resource constraints; task choice, cost and final-output effects must be reflected consistently in action valuation and realized production.
- Compare sigma regimes under identical base technology in paired counterfactuals; avoid attributing between-profile differences to sigma.
- No epsilon-clipping or imputation of missing task activity merely to force positive output.
- Record zero-task count and its association with output, costs, profitability and sigma, without treating it as an ex ante desirable outcome.

### Remaining A5 closure gates

The task-essentiality question is now **CLOSED (approved B)**. Still open: (1) reconcile the earlier exact production families/L1–L2 design with the proposed task CES; (2) approve task weights omega_cj and reference construction q0_cj/Y0_c; (3) select numerical sigma levels and an evidence-based or scenario-based allocation design for 100 configurations; (4) approve whether within-task pure-mode is the official baseline; (5) implement and execute T1–T8 after explicit approval.

**A5 status: theoretical interpretation approved, full A5 gate remains OPEN. No executable code or data changed. research_validated: false.**


## A5 researcher approval — equal structural weights for 20 tasks (2026-11-06)

**APPROVED:** For the primary Game 1 production specification, all twenty production activities have equal CES aggregation weights `omega_cj = 1/20 = 0.05` for every original technology configuration c and task j. This is a **research design assumption**, not an empirical estimate or an assertion that each task accounts for 5% of realized output. The 20 weights sum to one and are held constant across configurations, strategies, rounds and paired sigma counterfactuals. Unequal-weight sensitivity is **not** currently approved and must not be silently added.

For sigma_c != 1:
`Y_ict = Y0_c * [(1/20) * sum_{j=1}^{20} (q_icjt/q0_cj)^((sigma_c-1)/sigma_c)]^(sigma_c/(sigma_c-1))`.
For sigma_c = 1:
`Y_ict = Y0_c * prod_{j=1}^{20} (q_icjt/q0_cj)^(1/20)`.

Consequences:
- Equal structural weights do not imply equal realized output contributions, equal task marginal products, equal costs or equal optimal task allocations.
- In the normalized specification, with x_j>0 and sigma!=1, `partial Y/partial q_j = (Y0_c/q0_cj)*(1/20)*[mean_k x_k^rho]^(1/rho-1)*x_j^(rho-1)`; task-specific q0 and x cause heterogeneous marginal products despite equal weights.
- At x_j=1 for every task, Y=Y0 for all sigma; this is the normalization anchor, not a calibration of Y0 or q0.
- At sigma>1, zero activity in some tasks may be consistent with positive final output; sigma<=1 with any zero gives zero final output.
- The equality constraint must be tested to numerical tolerance and must not be replaced by data-driven weights or realized-output shares.

**A5 remaining researcher approvals:** q0_cj and Y0_c reference construction; numeric sigma levels, unequal group capacities and assignments or pre-registered scenario design; exact-family/L1–L2 reconciliation; pure-mode baseline approval. **Implementation:** not authorized; do not change simulation source or input CSVs. **Status:** A5 open; research_validated: false.


## A5 researcher approval — configuration-relative initial-capability normalization (2026-11-06)

**APPROVED:** Each of the 100 original technology configurations is normalized **relative to its own initial production capability**, rather than using a common absolute production reference across all configurations. The same frozen reference bundle is used for all 256 strategies and all 200 rounds within a configuration, and for paired sigma counterfactuals on that profile. This is a research decision about the reference **principle**, not approval of a numerical construction algorithm or a universal Y0=1.

For each original profile c, define a strictly positive, pre-treatment, feasible reference activity bundle `q0_c=(q0_c1,...,q0_c20)`, computed only from the profile's initial K/L endowments, task productivities, capital eligibility and a **pre-specified reference allocation policy**. Then `x_icjt=q_icjt/q0_cj` is dimensionless. With the already approved equal weights omega_cj=1/20, define `Y_ict=Y0_c*CES_sigma_c(x_ict)` where `Y0_c>0` is a configuration-specific final-output reference. At `q=q0_c`, `Y=Y0_c` for all sigma.

**No endogenous normalization:** The reference allocation must not depend on winners, strategy identity, simulated prices, profits, post-shock AI adoption, post-treatment decisions or future outcomes. Freeze it before experiments. Use identical q0_c/Y0_c for all sigma variants of the same profile to avoid changing the technology anchor in the sigma-only comparison.

**Economic caveat:** Setting `Y0_c=1` for every c would express outputs in configuration-relative index units and is *not* automatically comparable to physical quantities in a common market demand or monetary revenue equation. A configuration-specific conversion to final-product units, and consistent demand and price scaling, would be needed for cross-configuration or market comparisons. Likewise, choosing q0_cj from an arbitrary positive allocation defines the benchmark; it does not empirically identify the production function. The 100 configurations must not be presented as equal absolute productive capacity.

**Remaining implementation-critical decisions:** (i) the deterministic, feasible, strictly positive reference allocation across all 20 tasks (including capital-ineligible tasks, zero endowment contingencies, and non-use of outcome data); (ii) Y0_c units and conversion to final output; (iii) reconciliation with exact technology families/L1–L2 and pure-mode execution; (iv) numerical sigma values and group allocation. No executable code/data changes authorized. **A5 OPEN; research_validated: false.**


## A5 researcher approval — equal-labor reference bundle (2026-11-06)

**APPROVED:** For every base configuration c, define its task-reference activity by allocating its *initial labor endowment* equally to all 20 tasks, using only initial task labor productivities. Explicitly, `l0_cj = Lbar_c/20`, `k0_cj = 0`, `q0_cj = aL_cj * Lbar_c/20`, for j=1,...,20. This reference uses all available initial labor, no capital, and does not prescribe agents' actual choices.

**Conditions and audit:** Require Lbar_c>0 and every aL_cj>0 for this rule; if a future profile violates either condition, stop and request a new approved reference rule rather than substituting epsilon or fabricating activity. Preserve each original profile and all 20 task IDs. The reference is fixed across all 256 strategies, 200 rounds and within-profile sigma counterfactuals. Verify sum_j l0_cj=Lbar_c, k0=0, all q0 finite and positive, and q0 reproducible from source fingerprints. Since reference q0 does not depend on Kbar_c, the resulting relative output index does not itself measure absolute capital-enabled productive capacity.

**Important separation:** Equal *labor allocations* do not imply equal q0 across tasks; task productivity remains heterogeneous. Capital can be used in actual production where eligible; capital eligibility does not constrain the labor-only reference. A firm with zero task allocation can have q_j=0; never silently replace it with q0 or epsilon.

**Still undecided:** Y0_c in common final-product units versus a configuration-relative output index; whether and how the older exact four-family/L1–L2 design is preserved; official pure-mode rule; numerical sigma/group proportions. The reference q0 rule is approved, but it does not resolve these separate economic decisions. No executable code or CSV changed. **A5 remains OPEN; research_validated: false.**


## A5 researcher approval — unit reference output index Y0_c=1 (2026-11-06)

**APPROVED:** Set `Y0_c=1` for every base configuration c as a **dimensionless configuration-relative production index**. This is not a claim of equal physical output or productive capacity across the 100 configurations. The output index equals 1 at each configuration's approved initial equal-labor reference activity bundle.

Combining all approved A5 normalization decisions: `q0_cj=aL_cj*Lbar_c/20`, `omega_cj=1/20`, `Y0_c=1`, `rho_c=(sigma_c-1)/sigma_c`. For `sigma_c != 1`, `Y_index,ict=[(1/20)*sum_j(q_icjt/q0_cj)^rho_c]^(1/rho_c)`. For `sigma_c=1`, `Y_index,ict=prod_j(q_icjt/q0_cj)^(1/20)`. Require Lbar_c>0 and all aL_cj>0; zero task activities remain zero (no epsilon imputation).

**Market-unit constraint:** This index cannot silently replace physical final-product units in a common inverse-demand schedule, sales accounting or revenue/profit equation. If each configuration is simulated as its own separate market, an explicit configuration-specific physical conversion `Q_physical,ict=s_c*Y_index,ict` with `s_c>0`, or an explicitly index-denominated market and consistent price/cost units, must be chosen and justified before A6 implementation. Setting `s_c=1` for all c is a separate economic assumption, **not** implied by `Y0_c=1`. Do not reinterpret previously computed diagnostic profits as validated economic profits.

**Approval boundary:** Researcher approved the index normalization only; not any physical conversion, demand rescaling, market-clearing rule, numerical sigma assignment or code modification. All 256 strategies share a frozen q0 reference within each configuration and its sigma counterfactuals. Cross-configuration raw index levels do not measure absolute physical productivity.

**A5 status:** Reference scale Y0 decision closed. Pending: numerical sigma and strata design; exact-family/L1–L2 reconciliation; pure-mode execution approval; executable tests T1–T8. **A6 dependency:** reconcile market units before interpreting monetary profits. No source code or CSV modifications. `research_validated: false`.


## A5 researcher approval — pure-mode task execution (2026-11-06)

**APPROVED:** Each of the 20 task activities in a strategy-round is executed using **either labor services OR capital services**, never a contemporaneous mixture of the two within the same task. Across different tasks, a player may allocate both labor and capital. This is the official Game 1 baseline rule, superseding earlier labels of pure-mode as provisional.

For c,i,j,t let m_icjt in {L,K}. If m=L: q_icjt=aL_cj*l_icjt, k_icjt=0. If m=K: q_icjt=aK_cj*k_icjt, l_icjt=0, and task j must be eligible for capital execution at that time. Nonnegative activity and allocations; sum_j l_icjt<=Lbar_c and sum_j k_icjt<=Kbar_c. Zero allocation/activity is permitted. Unused resources need not be spent or allocated merely to meet a reference benchmark. Do not interpret an eligible task as necessarily automated: eligibility and actual selection of capital mode are distinct.

The reference bundle remains labor-only with l0_cj=Lbar_c/20, q0_cj=aL_cj*l0_cj, k0_cj=0. This **reference normalization** does not constrain strategy allocations to equal labor or prohibit capital execution. Across-task sigma describes substitution between production activities, not mixing capital and labor within a task.

**Implementation checks required after authorization:** exactly one execution mode per task/round; capital mode only for eligible tasks; no positive labor in capital mode and vice versa; shared resource caps; zero task activity behavior under sigma<=1 and sigma>1; fixed technology across 256 strategy players within a configuration; consistent reference construction. No simulation code or CSV changes authorized in this approval. **A5 remains OPEN** pending sigma assignment, legacy technology-family/L1–L2 reconciliation and executable validation. `research_validated: false`.


## A5 — compatibility audit of legacy four families, L1/L2 and approved task CES (2026-11-06)

**Status: analytical reconciliation proposed; researcher approval required before any architecture change.** This section is not an approval to modify 256 strategy identities, code, or original 100 profiles.

### Mathematical mapping on approved normalized task activities

Let `x_j=q_j/q0_cj`, `omega_j=1/20`, and `Y0_c=1`. The equal-weight generalized mean `M_rho(x)=[(1/20)sum_j x_j^rho]^(1/rho)`, with `rho=(sigma-1)/sigma`, has the following exact/limiting cases:

- Cobb–Douglas: `sigma=1` (`rho=0`), `Y=prod_j x_j^(1/20)`, exact continuous limit.
- Leontief: `sigma -> 0+` (`rho -> -infinity`), `Y=min_j x_j`, limiting case.
- Linear: `sigma -> +infinity` (`rho -> 1-`), `Y=(1/20)sum_j x_j`, limiting case.
- Finite positive sigma other than 1: genuine CES, not exact Leontief or linear. The original candidate `weighted_leontief=min(q_j/omega_j)` is **not** automatically equivalent to the normalized CES limit `min(q_j/q0_j)`; reference units and coefficients must be reconciled.

**Zero task nuance:** at finite sigma<=1, a zero positively weighted task gives zero output; for sigma>1, some zero tasks can coexist with positive output. At the Leontief limit, zero of any task gives zero output; at the linear limit, only all-zero activity forces zero output.

### Architectural conflict identified from canonical design.md

The historical strategy design explicitly assigns L1/D1 to **within-task technology** (Assignment, CES, Leontief, Hybrid) and L2/D2 to **cross-task aggregation** (Linear, Leontief, CES). Subsequent architecture reinterprets strategy IDs as market players facing the **same initial configuration**. The approved A5 baseline now fixes **pure-mode** within tasks and **configuration-specific cross-task CES** (including sigma=1) for all 256 players in each configuration.

Thus the older interpretation of L1/L2 as firm-selected production functions cannot be retained *unchanged* alongside the A5 common-technology rule. In particular, L1's mixed CES/Leontief/Hybrid task technologies conflict with the approved pure-mode task execution, while L2's firm-selected aggregators conflict with a common configuration-level CES. Treating these as independent strategy choices would confound technology differences with behavioral strategy differences.

### Recommended resolution — **not yet approved**

Separate **exogenous technology** from **endogenous decision policy**. Within a configuration c, fix task coefficients, K/L constraints, eligibility, approved pure-mode execution, reference bundle and common CES aggregator sigma_c. Compare behavioral strategies on this common production possibility set. Keep the original four functional families as mathematical benchmark/limiting representations and, only if separately approved, as **distinct technology-regime counterfactual experiments**, not as strategy-specific technology switches within the same controlled comparison.

**Governance caveat:** This resolution requires an explicit researcher-approved migration plan for L1/L2 labels and the existing 256 strategy registry; do not silently delete, relabel or count duplicate strategies as independent economic behaviors. If maintaining all four exact technology families as concurrent strategy alternatives is mandatory, the above common-technology resolution cannot be adopted without revisiting A5. Any 256-strategy comparison must document what actually differs between strategies.

**A5 closure:** mathematical relationship **explained**, architecture compatibility **not yet approved**. Pending researcher choice between (a) common configuration-level technology and remapping legacy L1/L2 or (b) retaining legacy firm-specific technology families and revisiting common-technology interpretation. No code/data modified. `research_validated: false`.

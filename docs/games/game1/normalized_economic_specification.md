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


## A5 researcher approval — common technology per configuration; four families as counterfactuals (2026-11-06)

**APPROVED (architecture principle):** Within each of the 100 initial configurations, all 256 strategy players face the **same** task technology: the same 20 task definitions, task productivities, initial K/L resources, automation eligibility, approved pure-mode execution, equal task weights (1/20), labor-only reference bundle `q0_cj=aL_cj*Lbar_c/20`, relative output anchor `Y0_c=1`, and a common configuration-specific cross-task CES elasticity `sigma_c`. Strategies differ in their decisions, information, learning and allocations, **not** by silently selecting different production functions. This is a researcher-approved change to the intended architecture, **not** authorization to alter the existing strategy registry or simulation code.

**Four-family reconciliation:** Cobb–Douglas is the exact sigma=1 CES case. Leontief and Linear are the respective sigma->0+ and sigma->infinity limiting aggregation technologies (normalized `min_j x_j` and `mean_j x_j`). Retain these as explicitly labeled **technology counterfactuals**, holding the base configuration and other exogenous conditions constant, subject to separately approved experiment design. A finite CES sigma must not be called exact Leontief or Linear. The legacy `min(q_j/omega_j)` candidate is not the same normalized Leontief benchmark unless its normalization is revised explicitly.

**Legacy L1/L2 audit and migration boundary:**
- Legacy L1/D1 labels: Assignment, within-task CES, within-task Leontief, Hybrid. Under approved common pure-mode technology, these cannot continue to function as **player-specific technology choices** in the main A5 experiment.
- Legacy L2/D2 labels: cross-task Linear, Leontief, CES. Under common configuration-specific CES, these cannot continue as **player-specific aggregator choices** in the main A5 experiment.
- **Do not** erase, silently relabel or duplicate old strategy IDs; preserve historical registry/outputs and map legacy IDs to a versioned new economic-policy registry only after a separate researcher-approved mapping.
- The historical design also mentions 12,288 L1–L7 nominal combinations and 3,072 L1–L6 policy IDs, whereas the later diagnostic experiment uses 256 strategies. These are different historical scopes, **not interchangeable counts**. Before implementing a revised 256-player experiment, inspect the actual registry and identify which 256 identities are behaviorally distinct once technology-only L1/L2 labels are removed. If two players have identical decision rules under common technology, they must be flagged as duplicate policies, not asserted to be independent strategies.
- Keep the 100 initial F profiles as configuration inputs; do not revert to 100 fixed firms or replace 256 players with the legacy 12,288 count by accident.
- Preserve explicit technology-regime IDs for CES, Cobb–Douglas, Leontief-limit, and Linear-limit **counterfactual runs**, separate from strategy IDs. Within a counterfactual run, all players share the same counterfactual technology.

**A5 approval boundary:** Common technology and counterfactual role of four families are **approved**. Exact L1/L2-to-behavior mapping, resulting strategy count/identity, sigma numerical values/group allocation and counterfactual execution protocol are **not yet approved**. No code, tests or CSVs changed. **A5 remains OPEN; research_validated: false.**


## A5 — verified actual 256-strategy registry and L1/L2 behavioral contribution (2026-11-06)

**Read-only source audit on branch `game1-economic-policy-interface`:**
- `src/interfirm_abm/task_layer_registry.py`: historical 7-layer catalog L1=4 within-task technologies, L2=3 cross-task aggregators, L3=4, L4=4, L5=4, L6=4, L7=4 market designs; 12,288 nominal full combinations.
- `src/interfirm_abm/task_experiment_dimensions.py`: `STRATEGY_LAYERS` filters explicitly to L3–L6; `strategy_player_ids()` forms 4^4=256 IDs; L1/L2 do **not** enter those IDs; L7 is separate market design.
- `src/interfirm_abm/task_strategy_engine.py`: `StrategyIdentity` fields are exactly L3,L4,L5,L6; `strategy_roster()` produces 256 nominal distinct policy IDs; L6 selects optimization, trial_error, softmax or imitation.
- `src/interfirm_abm/task_strategy_actions.py`: L3 alters task allocation weights/mode switches; L4 sets capital-mode thresholds; L5 changes valuation or reserve-price behavior. The action generator contains four effort candidates per player.
- `src/interfirm_abm/task_multi_action_diagnostic.py`: all 256 strategies in one configuration receive the same original F profile technology and diagnostic 20-task sigma=1 aggregator.

**Verified dimensional accounting:** L1 contributes **four technology options**, L2 **three aggregation options** to the *historical* catalog (12 L1×L2 combinations), but **zero independent technology dimensions and zero player-behavior dimensions** to the current 256-player roster, which is entirely L3×L4×L5×L6. Therefore the approved common-technology architecture does **not** require deleting/relabeling any of the currently generated 256 player IDs. The earlier unresolved migration concern is **resolved for the 256-player identity registry**. Historical L1/L2 catalog entries must remain available as technology counterfactual metadata, not be misreported as behavioral player IDs.

**Important qualification:** 256 unique IDs and four different branches in each layer do **not** prove 256 globally distinct decision functions or 256 distinct realized actions/payoffs in every configuration. For some technology profiles, L4 thresholds may produce identical mode allocations; L5 price offers may be nonbinding; L6 stochastic choices may coincide. A separate behavioral-equivalence audit must compare candidate allocations, valuations, selected actions and realized payoffs across profiles, rounds, seeds and observational histories. A one-round or one-seed coincidence is not proof of global equivalence. No such executable audit is claimed here.

**Scientific status:** The current L3–L6 implementation is diagnostic, not calibrated: L3 investment does not accumulate capital; L4 productivity thresholds are illustrative; L5 Cournot is a heuristic and price offers may be nonbinding; L6 imitation uses lagged action IDs, not exact rival allocations. Existing runner fixes sigma=1 and has not implemented approved q0 reference and heterogeneous sigma. These are separate economic validation gates.

**No code or data changes.** Next research decisions: sigma numerical levels/strata and counterfactual plan; then, with authorization, behavioral-equivalence tests and normalized CES integration. `research_validated: false`.


## A5 — empirical observational behavior equivalence audit of existing diagnostic artifact (2026-11-06)

**Source:** Existing GitHub Actions diagnostic artifact ID `13429476261`, available as `github-actions-artifact-13429476261.zip`, 100 `C000..C099/player_trajectory.csv` files; each has 256 players × 200 rounds, 5,120,000 player-round records in total. All files were read successfully and each configuration has exactly 256 players × 200 rows. This was **read-only analysis** of an existing diagnostic artifact; no model rerun, code modification or new scientific validation.

**Method:** For each player and each configuration, hash the 200-round ordered sequence of `(action_id, offered_price, capital_used, labor_used)` using exact serialized CSV values. Two players are in the same *observed-action-summary* equivalence class only if these 200-round sequences match in **all 100 configurations**. Output and profit are excluded from the decision signature; these are realized outcomes, not decisions. In each configuration, also count distinct full signatures, action-ID-only sequences, and round-1 signatures. Store audit output separately as `game1_behavioral_equivalence_audit.json` in the analysis working directory.

**Results:**
- 256 unique strategy IDs produce **194 distinct observed-action-summary sequence classes across all 100 configurations**.
- 159 singleton classes, 8 classes of size 2, 27 classes of size 3. Thus 97 strategy IDs belong to 35 non-singleton classes, with 62 IDs beyond one representative per class.
- Within a single configuration: minimum 66 distinct sequences, maximum 122, mean 83.87, median 81.0, out of 256 players.
- Example of globally coincident sequences in this diagnostic artifact: `L3=flexible|L4=eligibility|L6=optimization` combined with `L5=competitive`, `L5=cournot` or `L5=adaptive`.

**Interpretation boundary (critical):** These data do **not** contain the 20-task allocation vector for each chosen action, so equality of `capital_used` and `labor_used` totals cannot establish identical task-level allocations. Equality of these four observed fields is therefore **coarse observational equivalence**, not proof of full decision equivalence, theoretical policy equivalence, equal payoff or economic redundancy. Conversely, different observed sequences demonstrate differences under at least one recorded context but do not isolate the causal role of a layer because players interact in the same market and have potentially different lagged histories and random streams. The artifact uses the older diagnostic sigma=1 production and unapproved market assumptions, not the now-approved normalized A5 heterogeneous-sigma model.

**Next required test before strategy deduplication:** instrument or locally compute full per-task allocation vectors and action scores/selected actions under **identical controlled firm states, market observations, own histories, peer histories and random draws**, across all 256 policies and multiple representative configurations/seeds; distinguish observational equality, decision-function equality and payoff equality. Do not delete or merge strategy IDs based on this coarse 194-class result. `research_validated: false`.


## A5 literature-based sigma calibration — research direction B (2026-11-06)

**Researcher choice:** Prefer external literature and empirical estimates of **between-task CES elasticity**, rather than approving convenient numerical scenarios (such as 0.5/1/2). This is an approved **research method**, not approval of any numerical sigma assignment or code changes.

**Primary empirical candidate — Anders Humlum (2019), _Robot Adoption and Labor Market Dynamics_, Princeton job market paper**, https://economics.yale.edu/sites/default/files/humlumjmp_111419.pdf, section 4.1, Table 3: GMM estimate of **elasticity between production-worker, tech-worker and other-worker task categories** sigma=**0.493**, standard error **0.092**, Danish matched employer-employee data **1995–2015**. Simple normal-approximation 95% interval ~[0.313, 0.673] (our calculation, not claimed as an author-reported confidence interval). Source estimates task complementarity, but its task categories and Danish manufacturing/robot context do **not** identify a population distribution across our 100 synthetic 20-task configurations.

**Other task-elasticity evidence:** Baek & Jeong (2023), _Factors Influencing Labor Share: Automation, Task Innovation, and Elasticity of Substitution_, MPRA 118730, https://mpra.ub.uni-muenchen.de/118730/, abstract reports between-task elasticity of **one**; inspect its full model, estimation and uncertainty before considering comparability or calibration. Althoff & Reichardt (2026), CESifo WP 12403, https://www.ifo.de/DocDL/cesifo1_wp12403.pdf, calibrates task substitution at **0.49**, **citing Humlum**; not an independent estimate.

**Theory/mapping:** Acemoglu & Restrepo (2022), _Tasks, Automation, and the Rise in U.S. Wage Inequality_, Econometrica, DOI 10.3982/ECTA19815, uses a CES task aggregator and distinguishes between-task elasticity from endogenous aggregate capital-labor substitution. Acemoglu & Restrepo (2019), JEP DOI 10.1257/jep.33.2.3, motivates factor assignment to tasks. Do **not** import capital-labor, AI-human-composite, occupation-to-occupation or industry-to-industry elasticities as if they directly estimate our between-task sigma.

**Calibration gate still open:** Before setting numerical sigma values, extract model equations, task definitions, sample/sector, point estimate/SE/CI, identification and robustness from primary papers; assess external validity for 20 substitutable activities and heterogeneous AI eligibility; decide whether empirical evidence supports only a benchmark or a defensible distribution of sigma across the 100 profiles. No empirical assignment or G1/G2/G3 shares approved. `research_validated: false`. No code/CSV changes.


## A5 deep reading — Humlum (2019) vs Baek–Jeong (2023), verified primary PDFs (2026-11-06)

**Sources:** Humlum, _Robot Adoption and Labor Market Dynamics_ (2019 JMP), https://economics.yale.edu/sites/default/files/humlumjmp_111419.pdf, §4.1 Table 3 and Appendix B.1/C.1. Baek & Jeong, _Factors Influencing Labor Share: Automation, Task Innovation, and Elasticity of Substitution_ (2023 MPRA 118730), https://mpra.ub.uni-muenchen.de/118730/1/MPRA_paper_118730.pdf, equations (1)–(4), (Zeta), Table 2 and p.22 sensitivity discussion. **Version caveat:** MPRA page lists later versions; this audit covers specifically October 2023 version, not an assumed latest paper.

**CES parameter mapping:** Humlum sigma is between-task substitution (continuum task aggregator), and is conceptually aligned with A5 sigma_c, subject to task taxonomy/aggregation differences. Baek–Jeong's **zeta**, not their **sigma**, is between-task elasticity; their sigma is substitution between task composite T and non-robot capital K. Their within-task labor/robot relationship is linear and robot eligibility segmented. A5 uses 20 normalized activities and pure-mode task execution; numerical estimates do not identify sigma for our synthetic configurations automatically.

**Humlum identification:** Cost-minimization factor-demand FOC, log relative labor demand on relative wage and relative productivity. Wage/productivity simultaneity handled using rational-expectations GMM and lagged factor decisions/prices under a Markov productivity process; sample of robot nonadopters, two-step GMM. Table 3 sigma=0.493, SE=0.092, approximate Wald 95% interval [0.313,0.673]. Appendix C.1 derives moments and lagged instrument functions. This audit has **not verified** sigma-specific overidentification/weak-IV tests or a robustness table; do not assert those were passed.

**Baek–Jeong identification:** Nested CES task aggregate `T=(integral t_j^((zeta-1)/zeta))^(zeta/(zeta-1))`; final `Y=(T^((sigma-1)/sigma)+K^((sigma-1)/sigma))^(sigma/(sigma-1))`. Estimate labor-share response coefficients across aggregate data using OLS/NLS/GMM/quantile specifications, then back out task elasticity via `zeta=1-alpha3+alpha4*S_L^T/(1-S_L^T)`. Reported zeta=1.051 with S_L^T=0.979. Their sensitivity intervals (one-standard-error coefficient perturbations, **not** 95% CI for zeta): labor-price coefficient [1.038,1.063], robot-price coefficient [0.364,1.137], both [0.352,1.149]. They fail to reject `1-zeta=0` at 5%; non-rejection is not proof of exact Cobb–Douglas. The wide range is driven substantially by weak precision of robot-price coefficient.

**Inference for A5:** Independent task-elasticity studies support materially different points (0.493 vs 1.051), with different task definitions, countries, levels of aggregation and identification. They do not identify 100 profile-specific sigma_c values, population shares in G1/G2/G3, or a justified sigma>1 population fraction. Do not pool point estimates, sample 100 sigma values from an invented distribution, or use Baek–Jeong's nested outer sigma as A5 task sigma. Before calibration, verify later Baek–Jeong version and its changes, read replication/supplementary details, then present researcher with explicitly separated empirical anchor, structural scenario, and robustness envelope. **No numeric assignment approved; no code/CSV modified; A5 OPEN; research_validated: false.**


## A5 — updated Baek–Jeong version audit (2026-11-06)

**Verified current MPRA latest version:** Jeong, Baek & Peri (2024), _Automation, Human Task Innovation, and Labor Share: Unveiling the Role of Elasticity of Substitution_, MPRA 122119, dated 11 September 2024, deposited 23 September 2024. https://mpra.ub.uni-muenchen.de/122119/1/MPRA_paper_122119.pdf (47 pp.). MPRA version history https://mpra.ub.uni-muenchen.de/122119/. The older 2023 Baek–Jeong MPRA 118730 is **superseded for primary calibration**. Author manuscript points to a replication/latest-version GitHub URL `https://github.com/jayjeo/public/blob/main/Laborshare/readme.md`; link returned 404 during this audit, so replication data/code **not verified**.

**Changed task elasticity:** Original Oct 2023 task `zeta=1.051`; latest Sep 2024 task `zeta=1.118`, an increase of 0.067 (~6.4%). Outer CES `sigma=0.412` in 2024 is **aggregate-task vs nonrobot-capital**, not A5 between-task elasticity. Latest §5.4 p.21 reports **90% CI for zeta [-0.196,2.432]** while Appendix F p.38 reports **[-0.449,2.685]**: internal CI discrepancy requiring author/code clarification. Both span unity and negative (economically inadmissible for our CES), so they cannot be used naively as a sigma sampling range. The latest paper itself says no definitive conclusion about zeta.

**Method changes:** Adds coauthor Giovanni Peri, US-patent/IFR-robot and O*NET cognitive-task-based shift-share proxies for robot/human innovation, country/industry panel (N=473 in Table 1), and restriction `alpha3+alpha4+alpha5=0` in baseline regressions. Authors explicitly state **factor prices (wages, robot price, nonrobot capital price) are endogenous and not instrumented**, even though RI/HI use shift-share IV-type constructed measures. The paper says unconstrained-vs-constrained regression restriction test is rejected at 5%, signaling model-data tension; robot-price coefficient is imprecise. Robot share within task costs estimated 2.813% vs alternate 2.104%, another sensitivity source.

**Implication:** Humlum (2019) 0.493 and latest Jeong–Baek–Peri (2024) 1.118 are two distinct **point anchors** with sharply different identification and task definitions, not independent draws from a known distribution of 100 synthetic configurations. Do not interpret 2024 outer sigma=0.412 or 2026 Jeong solo labor/nonrobot-capital elasticity 0.552 as between-task sigma. No 100-profile sigma assignments or group shares approved. **A5 OPEN; research_validated:false; no code/CSV changes.**


## A5 researcher approval — scenario-based sigma design A (2026-11-06)

**APPROVED by researcher:** Switch from empirical-only calibration B to original scenario design A, after Q1/A* literature screen did not establish an admissible directly transferable distribution of between-task elasticity. Primary sigma scenarios: **0.5, 1.0, 2.0**, labeled respectively G1 low substitutability/complementarity, G2 Cobb–Douglas, G3 greater substitutability. These are **transparent simulation assumptions**, **not empirically estimated or representative population shares**. Do not label any of these values 'calibrated from Q1 evidence'.

**Design:** Fully crossed **within-profile paired counterfactuals**: run each of the 100 original profiles under each of three sigma values, all 256 strategy IDs and 200 rounds per profile–sigma scenario. Expected 100×3×256×200=**15,360,000 player-round observations** (not yet executed). Freeze original profile endowments, 20 task coefficients and eligibility, reference q0, task weights, strategy definitions and common exogenous market conditions across sigma variants; paired random seeds and reproducible stochastic streams where applicable. Report outcomes by sigma and within-profile contrasts, avoiding claims of population prevalence or causal effects beyond modeled interventions.

**Allocation interpretation:** G1/G2/G3 are **three counterfactual treatments per configuration**, not mutually exclusive assignments to disjoint subsets of the 100 profiles. Thus each sigma group has 100 configuration runs, not an arbitrary one-third split. Historical diagnostic 5.12m rows at sigma=1 remain separate and are **not** a validated run of the normalized new model.

**Sensitivity still to pre-specify:** Additional near-one and tail sigma values, stability of ranking and market outcomes, stochastic seeds/CI, and exact limiting-family counterfactuals. The three approved main scenarios do not imply these supplementary numerical values are approved.

**Governance:** No source code, CSVs or simulations changed by this approval. A5 theory sigma-choice gate **CLOSED**; implementation, T1–T8, and A6 unit-consistent market remain OPEN; `research_validated: false`.


## A5 initial code implementation and T1–T8 verification gate tracking (2026-11-06)

**New code (committed):** `src/interfirm_abm/task_a5_normalized.py` implements reference `q0_cj=aL_cj*Lbar_c/20`, 20 normalized activity ratios, dimensionless CES output, approved sigma scenarios (0.5,1,2), pure-mode allocation evaluation via existing `TaskBasedFirm.evaluate_allocation`, and same-profile paired technologies. It does **not** alter the legacy diagnostic runner, the 256 strategy roster, market demand, price, profits, or source CSVs. **New tests:** `tests/test_task_a5_normalized.py` exercises formulas and constraints but are not yet confirmed executed on CI.

**Canonical T1–T8 status, distinguishing unit tests from full gates:**
- **T1 PARTIAL:** fixture validates 20 task IDs/reference, but full 100 F profiles, C000–C099 mapping and 256 roster population check not yet run under new A5.
- **T2 PARTIAL:** existing firm feasibility plus new tests for pure-mode, capital eligibility and labor caps; full real-profile coverage not run.
- **T3 TESTS AUTHORED / NOT EXECUTED:** anchor, sigma regimes, zero cases, homogeneity, monotonicity, sigma near 1, limiting behavior, input validation.
- **T4 PARTIAL:** task-level simultaneous q/q0 rescaling invariance test authored; final-output physical units and downstream price/demand rescaling explicitly depend on A6 and are not implemented.
- **T5 PARTIAL:** same reference across sigma variants tested by fixture; 256-player shared-technology runtime integration not yet implemented.
- **T6 PARTIAL:** 3 paired technology objects from one base profile, identical frozen references; actual common-seed 100-profile market runs not implemented.
- **T7 OPEN:** production index not yet wired to policy valuation, offers, sales and cost/revenue. Legacy diagnostic uses unnormalized sigma=1; must not imply normalized A5 integration.
- **T8 PARTIAL:** scenario values and absence of market-money fields checked; actual CI run artifacts, seeds, preservation verification and failure reports pending.

**Test command (to be executed in environment with repo installed):** `PYTHONPATH=src python -m unittest discover -s tests -p 'test_task_a5_normalized.py' -v`. No passing result is claimed here. **Do not set research_validated true.** Closing full T4/T7 requires a separately approved A6 conversion of the dimensionless production index into market quantity, or a deliberately index-denominated market with compatible price/demand/cost units. No arbitrary scale factors introduced. Existing 5.12m-row diagnostic remains historical and does not count as a completed normalized 15.36m-run.


## A5 execution follow-up — exhaustive profile test and diagnostic integration (2026-11-06)

**Implementation committed on branch `game1-economic-policy-interface`:**
- `tests/test_task_a5_normalized.py` now includes a full 100-profile CSV loader test: unique F001–F100, 20 tasks each, 256 unique L3–L6 strategy IDs, and the feasible labor-only reference yielding normalized output index 1 under all three sigma treatments.
- `src/interfirm_abm/task_a5_diagnostic_runner.py` injects approved normalized CES into both strategy action valuation and the `MixedMarket` output aggregator, preserving the existing 256 strategy IDs and market clearing for **diagnostic-only** runs. Paired stochastic policy seeds are based on `config_id|strategy_id|a5-paired` and are sigma-invariant. The runner does **not** change the legacy full-sample code or assert economic comparability of money payoffs.
- `tests/test_task_a5_normalized.py` also includes a 256-player one-round smoke test for C000 under each approved sigma.
- `.github/workflows/a5-normalized-tests.yml` runs the A5 test module on branch pushes and manual dispatch.

**Execution evidence boundary:** GitHub commits for code and workflow are verified, but **no successful workflow run/log or local complete test result was observed in this audit**. Authored tests are not marked passing. User should inspect `https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/workflows/a5-normalized-tests.yml` for run and errors. If the workflow has not started, dispatch manually; do not claim T1–T8 passed.

**A5 validation:** T1/T2/T3/T4/T5/T6/T7 now have at least partial code/test coverage, but T5 and T6 still require full 100×3 paired execution, and T7 monetary interpretation remains blocked by A6 index-to-market-units convention. T8 requires successful CI logs and seed/report artifacts. Keep `research_validated: false`; do not conflate the 15,360,000 intended player-round observations with completed execution.


## A5 verified GitHub Actions run and defect resolution — 2026-11-06

**Verified result:** Workflow `A5 normalized technology checks`, run [#42186866398](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/42186866398), commit `35278244b461bb54977c1ec984b121d4d79ae7a9`: **success, 10/10 tests, 0 failures** (observed job log: `Ran 10 tests in 0.261s; OK`).

**Defect findings:** Initial run #42186082634 failed T3 because code incorrectly sent `sigma=1.000001` to geometric mean using a near-1 tolerance, erroneously yielding zero for an input vector containing a zero task. Commit `e0e20822c778b89967d9bca646005485178938cc` fixed the model branch to use geometric aggregation **only when sigma exactly 1**. Subsequent run #42186730565 still failed at a strict `>0` assertion for `sigma=1.000001`: the mathematically positive CES result is below IEEE-754 representable magnitude and numerically underflows to zero. Commit `35278244b461bb54977c1ec984b121d4d79ae7a9` updated the test to require nonnegativity near 1 and strict positivity at sigma>=2. This is a numerical underflow limitation, not a license to epsilon-smooth a zero task. All three main approved sigma scenarios (0.5, 1, 2) retain their intended mathematical zero handling.

**Interpretation of pass:** T1 exhaustive fixture reads all 100 real F profiles, checks 20 tasks and 256 strategy IDs, verifies normalized labor reference under three sigma values. T7 integration is a one-round smoke run of 256 players for C000 at sigma 0.5,1,2. Other T2/T3/T4/T5/T6/T8 unit checks passed. **NOT tested:** running a full 100×3×256×200 simulation, fully shared per-player runtime technology across all profiles, CI across stochastic seeds, market economic validation A6. Thus T1–T8 research-level gates are not all closed. `research_validated: false` remains required.


## A6 approval gate — normalized composite commodity (researcher decision, 2026-11-06)

**APPROVED (A6 option A):** Each configuration is a separate simulated market whose tradable output is a **normalized composite commodity**. The approved A5 dimensionless CES production index is denominated as the quantity of that configuration's composite good, with its own market price expressed in abstract money per normalized composite-good unit. This is a **model numeraire and within-market unit convention**, not an empirical conversion to a common physical product and not a claim that quantities or price levels are directly comparable across different configurations. All 256 strategies in a given configuration trade the same composite good and use the same frozen technology reference under paired sigma interventions.

**Explicitly NOT approved by this decision:** inverse demand functional form or coefficients; market-clearing, rationing or price-setting rule; wage and capital-service rental levels; sunk/fixed/AI adoption/adjustment costs; idle endowment charges; outside option; discounting; market demand shocks; equilibrium concept; learning/payoff scaling. Existing `w=r=1`, `P=max(0,(A-Q)/B)`, strategy reserve prices, `expected_price=2`, and effort/adoption heuristics remain diagnostics. Do not retrofit positive profits or interpret prior 15.36m diagnostic player-round outcomes as A6-validated economic results.

**Accounting and unit contracts to validate after remaining approval:**
- For configuration c, round t: `Q^s_ict=Y^index_ict` normalized composite-good units; `0<=S_ict<=Q^s_ict`; `Q^sold_ct=sum_i S_ict`.
- `P^tr_ict` abstract monetary units / normalized composite-good unit; `R_ict=P^tr_ict*S_ict` monetary units / round.
- `w_ct` money/labor-service unit; `r_ct` money/capital-service unit. Candidate `C_ict=w_ct*L_used+r_ct*K_used+F_ict+C_AI,ict+C_adjust,ict`; the cost incidence and extra terms require researcher approval.
- `pi_ict=R_ict-C_ict`, `Pi_ic=sum_{t=1}^{200}pi_ict`. These are identities, not sufficient conditions for economic equilibrium.
- For any inverse-demand `P_ct(Q)`, declare the unit of Q, monetary scale, demand capacity and whether Q means offered supply or realized sold quantity. A genuine clearing rule must reconcile Q, price and eligibility/reserve constraints rather than using a provisional price based on rejected supply.
- Cross-configuration results should prioritize within-profile paired sigma contrasts; do not directly interpret relative index outputs across configurations as physical productivity differences.

**Researcher decision requests before coding A6:** (D1) inverse demand family and demand normalization across configurations; (D2) price/quantity clearing and whether L5 reserve bids bind; (D3) labor and capital-service cost incidence/numeraire, including idle capacity; (D4) AI adoption, adjustment and fixed cost policy; (D5) outside option and losses/exit; (D6) validation and robustness design. Maintain `research_validated: false` until approved implementation, CI and economic tests. This is a documentation-only approval record; no A6 simulation code changed.


## A6 D1–D2 researcher decisions — 2026-11-06

**Approved D1:** Linear inverse demand within each separate configuration-specific normalized-composite-good market: `P_ct(Q)=max(0,a_ct-b_ct Q)`, with `a_ct>0, b_ct>0`. The numerical values, whether demand varies across profiles/time, and the information agents have about these parameters are **not approved**.

**Approved D2:** Behavioral Cournot-style simultaneous quantity competition with a single uniform transaction price; not a claim that agents solve Nash equilibrium. Each strategy chooses a feasible K/L/task allocation before the current-round price is known, producing `Y_ict` units of its configuration's normalized composite commodity. `Q_ct=sum_i Y_ict`, `P_ct=max(0,a_ct-b_ct Q_ct)`, `S_ict=Y_ict`, `R_ict=P_ct Y_ict`, `pi_ict=R_ict-C_ict`. No inventory or quantity rationing in the baseline. When `Q_ct>=a_ct/b_ct`, `P_ct=0`, all production is **accounted as transacted at zero price**, revenue is zero, and profit is negative production cost (or zero if cost is zero). This is an explicit extension/convention for zero-price excess supply, not an empirical market-clearing assertion.

**Approved D2.2:** Reinterpret L5's former `price` mechanism as `target-price`, a quantity-selection behavioral rule seeking a target *predicted market price*; it must **not** directly set a transaction price or create reserve-price exclusion. Other L5 categories: `competitive` treats price as locally invariant in candidate evaluation; `cournot` anticipates own quantity's impact on aggregate price; `adaptive` updates expectations from lagged observed outcomes. Preserve historic strategy IDs/results and document any prospective registry semantic changes. Still **pending approval**: target-price target formation, competitor quantity forecast, candidate scoring/tie-breaking, and exactly which lagged market/peer signals each L5 type may observe. Distinguish a target-price *behavior* from the actual market price equation.

**D2 invariants for subsequent implementation/tests:** all 256 players see the same realized transaction price per round; sales equal nonnegative output; `Q_ct=sum_i S_ict`; `P_ct=P_ct(Q_ct)`; revenue identity; price never negative; no current-round price leakage into actions; zero-price revenue exactly zero; all players' market impact is included; sigma-only counterfactuals hold demand/cost primitives fixed within a configuration. Cost assumptions remain D3, and economic validation remains **false**.

**D3 next researcher decision:** whether factor charges apply to *used* labor and capital services only or to *endowed/committed* capacities regardless of utilization, and whether factor prices `w,r` are exogenous market prices or endogenous. The existing `w=r=1` and zero extra cost are **not approved**. No simulation code changes authorized by these decisions.


## A6 D3.1 approval — used factor-service cost (2026-11-06)

**Researcher approved D3.1 option A:** baseline variable production cost charges **actual utilized** labor and capital services only: `C_variable,ict=w_ct * sum_j l_icjt + r_ct * sum_j k_icjt`. Idle portions of `Lbar_c` and `Kbar_c` are not charged *variable* factor-service costs. Nonnegative finite allocations and the existing per-configuration endowment constraints still apply. `r` is a per-round **capital-service rental price**, not the purchase price of owned capital; no depreciation or capital acquisition is implied. `w` is the per-round labor-service price. Both factor-price levels, exogeneity/endogeneity, across-profile equality, and time variation remain **D3.2 pending**. Additional fixed, AI adoption/operation, adjustment and other costs remain unapproved and must not be silently set to zero as a research conclusion. This approval does not change code, prior A5 diagnostic results or `research_validated: false`.

**D3.2 choices for researcher:** (A) common fixed exogenous `w,r` (baseline factor-price-taking market); (B) pre-specified exogenous time paths `w_ct,r_ct`; (C) endogenous factor prices determined by labor and capital-service supply. In all cases the ratio `w/r` has meaning only with declared factor units, and `w=r=1` is an unapproved diagnostic normalization. Under sigma-paired comparisons, hold the approved factor-price primitives fixed unless intentionally testing a separate treatment.


## A6 D6 — Researcher-approved minimal-model directive (2026-11-06)

**Status:** Researcher-approved decisions recorded; D6 simplification is a governing design direction, not authorization to change simulation code or claim scientific validation. `research_validated: false`.

### Primary research question and design priority
Compare realized cumulative profits of 256 strategy players over 200 rounds in each of 100 separate, shared-technology market configurations, including how outcomes change under technological substitutability scenarios. **Keep the economic model as simple as possible.** Introduce extra states, parameters, learning stages, and exceptional-case mechanisms only when indispensable to the research question, accounting consistency, or information validity. Implementation details should not become researcher-level approval gates unless they change economic behavior, assumptions, or interpretation. Do not erase prior decision history; mark unimplemented elaborate proposals as proposals, not approved baseline requirements.

### D6 approvals (specification only)
- D6.1 B: strategy-specific evaluation. Competitive/Cournot/Adaptive prioritize expected profit; Target-price prioritizes price-target distance then profit. Final outcome measure is realized cumulative profit, not internal learning score.
- D6.2.1 A: update learned outcomes only for the action actually chosen; no realized counterfactual payoffs for unchosen actions.
- D6.2.2 A: Target-price realized feedback for positive-output chosen action is lexicographic `(-abs(realized_price - chosen_action_target_price), realized_profit)`; no arbitrary distance-profit weighting.
- D6.2.3 A: shutdown produces q=cost=profit=0, retains public market observations and ability to reenter; shutdown has no defined target-price distance. Reentry is permitted, not necessarily selected every round.
- D6.3.1 A: preserve D5.1 public-information boundary; Imitation cannot observe individual rivals' actions or payoffs.
- D6.3.2a A: rank-based Softmax for Target-price production-action ordering, preserving lexicographic preference without weighting distance against profit.
- D6.3.2b A: conceptually two-stage participation (produce vs shutdown) and, conditional on producing, production-action choice. **Implement minimally; no separate elaborate participation-learning system is approved.**
- D6.3.2c A: Imitation follows lagged aggregate output trend, not a specific rival or proof of rival success.
- D6.3.3a A: exponential recency-weighted update from the chosen action's observed outcome; Target-price keeps distinct distance and profit feedback as needed. No updates of unchosen actions from realized payoffs.
- D6.3.3b A: Optimization no mandatory random exploration; Trial-and-Error uses epsilon exploration; Softmax uses temperature.
- D6.3.3c A: Imitation follows aggregate output trend probabilistically, otherwise own evaluation, with a possible exploration route to reentry.

### Registry and minimal operational loop
Keep existing L6 identifiers `optimization`, `trial_error`, `softmax`, `imitation` (L5 `adaptive` is not an L6 option). Each round: (1) observe permitted lagged information; (2) L5 evaluates feasible production actions, L6 decides participation and action; (3) market clears and records own realized payoff plus public P,Q; (4) update only permitted own learning and L5 beliefs once per respective state. Preserve simultaneous decisions and no current-price lookahead. Never conflate L5-Adaptive price expectation updates with L6 action learning. Profit is counted exactly once in cumulative payoff.

### Not approved; simplify before implementation
Numerical `eta`, `epsilon`, Softmax temperatures, `phi`, additional imitation exploration rate, monetary normalization `M_c`, separate participation value states and their learning rates, prior initialization formulas, specific tie-break tolerances, and detailed cold-start/fallback mechanisms from the D6.3.4 proposal **remain unapproved**. Earlier multi-state participation-learning equations and elaborate three-branch imitation are proposals only, not mandatory baseline. Select the smallest coherent operational rules and a compact sensitivity plan when implementation is authorized; explicitly flag any researcher-significant tradeoff. Preserve the existing D1–D5 and D6 approvals unless a proposed simplification requires explicit amendment.

### Governance and next steps
Single canonical file: `docs/games/game1/normalized_economic_specification.md` on branch `game1-economic-policy-interface`. Update this file in place; use Git history rather than version-suffixed copies. This documentation-only change does not authorize simulation code edits, reruns, or a claim of completed research validation.


## A6 — Consolidated minimal baseline and consistency audit (2026-11-06)

**Authority and scope:** This is the current consolidated *design status*, superseding earlier historical "pending" labels where a later explicit approval exists. Earlier sections remain as decision history. This section does not silently approve numerical values or amend the user's research choices. Documentation update only; do not edit simulation code or claim validation. `research_validated: false`.

### 1. Minimal A6 baseline — approved economic commitments

- **Research unit:** 100 independent initial market configurations; each configuration contains 256 strategy players (actual L3×L4×L5×L6 roster) over 200 rounds. All players within a configuration share the same task production technology and initial configuration conditions. 20 production activities, pure labor-or-capital execution within each task, equal structural task weights, normalized reference output 1. Three *scenario* substitution elasticities: sigma=0.5, 1, 2; not empirically calibrated prevalence. Compare cumulative **realized** profit and sigma-paired outcomes. Additional exact Leontief/linear technology limits are optional separately labeled counterfactuals, not part of the minimal main run.
- **Commodity/market:** each configuration trades its own normalized composite good. Actual inverse demand is `P_ct=max(0,a_ct-b_ct Q_ct)`, `a_ct,b_ct>0`. Simultaneous quantity choice; `Q_ct=sum_i q_ict`; one actual price for all players; all produced output is accounted as sold at that price (including zero price), no inventory/rationing. This is behavioral quantity competition, not a Nash-equilibrium claim. Agents do not know the true demand equation or parameters.
- **Costs and outside option:** `C_ict=w sum_j L_icjt+r sum_j K_icjt` using **utilized** services only; idle resources uncharged. Baseline cost convention previously approved: exogenous common `r=1`, `w/r=1`; robustness `w/r=0.5,2`. No baseline fixed, AI adoption, or adjustment charges; do not interpret absence as empirical evidence. `pi_ict=P_ct q_ict-C_ict`. Optional shutdown `q=C=pi=0`; no forced exit, no reentry delay/cost, all players remain for 200 rounds. Profit is counted exactly once.
- **Information:** before round t only public `(P,Q)` through t-1 and private own history/technology/allocations; no individual rivals' actions, profits or cost data; no current-round clearing information. L5 computes *predictions*, not observed counterfactual realized payoffs. D5 approved market-belief baseline: 20-round local rolling OLS using valid P>0 observations (at least 8 and CV(Q)>=5%); negative finite slope required, else use the prior, not a stale estimate. Price-zero history is retained but excluded from OLS. Prior `p0=1`, `b0c=0.5*p0/Qref_c` with public preannounced `Qref_c=sum_i qbar_ic`; first-round rival quantity forecast `Qref_c-qbar_ic`, later `Q_{t-1}-q_{i,t-1}`. The exact construction of feasible `qbar_ic` still needs a reproducible minimal implementation rule. Rolling-window robustness h=10,50; prior kappa=0.25,1.
- **L5 strategy meaning:** `competitive` treats candidate price as locally invariant; `cournot` incorporates own quantity in predicted market price; `target-price` ranks positive-output candidates by smallest predicted-vs-target price distance `Pstar=(1+mu)C/q` (`mu=0.1`, robustness 0,0.25), predicted profit breaks distance ties; `adaptive` updates own expected price by `phat_next=(1-lambda)phat+lambda*P_observed` (`lambda=0.5`, robustness 0.2,0.8). L5 only evaluates; L6 selects. The old diagnostic L5 `price` bid is not a binding transaction-price offer.
- **L6 registry and approved behavior:** `optimization`, `trial_error`, `softmax`, `imitation`. Strategy-specific evaluation: profit priority for competitive/cournot/adaptive, lexicographic price distance then profit for target-price. Only chosen actions receive realized learning feedback, using exponential recency weighting; target-price retains separate observed distance and profit feedback for the chosen positive-output action. Rank-based Softmax preserves the target-price lexicographic ranking among *production* candidates. Imitation follows **lagged aggregate quantity trend**, never individual peer outcomes. Optimization has no mandatory random exploration; trial_error uses epsilon; Softmax uses temperature; imitation probabilistically follows aggregate trend with an exploration route. Participation is conceptually choose produce vs shutdown, then (if produce) choose a production action; **do not implement a second elaborate learning system unless independently justified and approved**. Shutdown target-price distance is undefined, not zero; shutdown observers retain public market history and can reenter.

### 2. Complexity explicitly excluded from baseline

Do not add a separate participation-reinforcement value engine, duplicated reward accumulation, multi-branch imitation score system, arbitrary weighted target-price utility, unobservable peer imitation, causal claims about inferred demand slope, hidden opponent state, AI adoption costs, inventory/rationing, or extra technology regimes in the main run. Prior elaborate D6.3.4 equations are *proposals*, not approvals. The numerical learning choices `eta`, `epsilon`, temperature, imitation-follow probability `phi`, any separate reentry exploration rate, score normalization, initial priors and tie tolerance are still **unapproved**. Use the fewest parameters possible; publish baseline and a limited sensitivity check once the researcher approves behaviorally meaningful choices.

### 3. Consistency audit — blocking issues before code

1. **Legacy implementation mismatch (BLOCKER):** `task_strategy_actions.py` still uses L5 `price` offers, hardcoded candidate valuations and heuristic Cournot; the approved L5 `target-price` is a quantity-selection rule. Replace *only after code authorization*, retaining historical diagnostic interpretation.
2. **Information leakage (BLOCKER):** `task_strategy_engine.py` imitation can read lagged individual peer action/payoff via `peer_provider`; this conflicts with D5.1/D6.3.1 A. New baseline must consume only public lagged P,Q and private own history. Existing diagnostic is not an approved A6 result.
3. **Double-learning ambiguity (BLOCKER):** old L5-adaptive action valuation averages own realized payoffs, while new L5-adaptive is *price-expectation updating*. Keep L5 beliefs distinct from L6 action reinforcement. Update each state at most once per observed round; add realized profit to cumulative payoff once only.
4. **Shutdown and lexicographic ordering (NEEDS MINIMAL RULE):** a shutdown action has zero payoff and undefined target-price distance, so it cannot be inserted as `d=0` in production rank-based Softmax. Use the approved conceptual participation-first separation with the simplest rule consistent with optional shutdown and exploration/reentry; avoid inventing participation learning values. This specific decision rule still needs researcher signoff if it changes incentives.
5. **Prior/scale and cold start (NEEDS REPRODUCIBLE CONVENTION):** `Qref` and `qbar` need explicit feasible reference construction; positive monetary Softmax temperature must scale with payoff units or use a preannounced reference scale. Neither is license to add new behavioral states. Distinguish initial predictions from observed rewards.
6. **Task/strategy identity (VERIFY):** four effort candidates and 256 IDs exist in diagnostic code; same IDs do not guarantee distinct behavior. Preserve identities and test decisions under controlled histories. Exact production units must match demand and cost units.
7. **Versioned status conflicts (DOCUMENTATION):** earlier chronological paragraphs say D1/D2/D3.2 or A5 sigma are pending. Later approvals supersede these where explicitly recorded (A5 sigma 0.5/1/2; A6 D1–D5 discussion and D6 decisions). Do not treat historical 'pending' as current state. The D3.2 and D5 detailed approvals were discussed and accepted in the research conversation; this consolidation records them without claiming code implementation. Keep exact values and unapproved engineering rules distinguishable.
8. **Identification (INTERPRETATION):** 256 players share a market and their profits are interdependent. Treat market/configuration runs as comparison units; do not claim independent player-round observations or empirical causal identification. Sigma interventions are simulation counterfactuals.

### 4. Minimal next-step gate

- **Completed now:** collect researcher-approved A5/A6 decisions into one authoritative current-state summary; remove proposed extra learning states from baseline; audit assumptions against current diagnostic code.
- **Before code:** settle only the economically consequential shutdown-vs-production rule, a reproducible feasible reference quantity, and dimensionally coherent Softmax scale/initialization. Choose a minimal numeric learning baseline as implementation assumptions with transparent sensitivity; do not reopen the entire design.
- **After explicit code authorization:** integrate A5 CES, A6 market/costs, L5 evaluation and L6 choice into one runner; run focused accounting, information-leakage, no-double-update, shutdown/reentry, sigma and 16 Adaptive×Imitation interaction tests. Then run paired 100×3×256×200 scenarios with seed sensitivity, analyze cumulative realized profits and only then publish validated charts. Earlier diagnostic runs are not final A6 evidence.

**Current research status:** A5 core mathematics and basic tests partly implemented; A6 design consolidated but **not** implemented and **not** scientifically validated. `research_validated: false`.


## A6 — Current decision ledger and implementation blockers (consolidation audit, 2026-11-06)

**Status:** This is the authoritative *current-state index* for D1–D6, read together with the preceding approved decisions. It supersedes historical “pending” labels only where an explicit later approval is recorded. It does not create new researcher approvals, choose remaining parameters, authorize code changes, or claim scientific validation. `research_validated: false`.

| Decision | Current approved baseline | Still open / qualification |
| --- | --- | --- |
| **D1 — Demand** | Each configuration is a separate normalized-composite-good market; `P=max(0,a-bQ)`, `a,b>0`. | Numeric demand intercept/slope, scaling to 256 players and 100 profile-specific normalized goods, time variation, and sensitivity. True `a,b` are not observed by agents. |
| **D2 — Quantity and price** | Simultaneous feasible quantity decisions; one uniform realized price from aggregate output; all output counted sold even at zero price; no inventory/rationing. L5 `price` becomes nonbinding behavioral `target-price`. | Implement candidate scoring and forecasts consistently; no Nash-equilibrium or market-clearing welfare claim. |
| **D3 — Factor costs** | Only utilized labor/capital services charged; idle endowments uncharged. Consolidated baseline: exogenous common `r=1`, `w/r=1`, with `w/r=0.5,2` sensitivity. | Clarify units and whether baseline `r=1,w=1` are per-configuration normalized prices; do not confuse capital rental with investment. No empirical calibration claimed. |
| **D4 — Extra costs** | Consolidated *minimal baseline* excludes fixed, AI adoption and adjustment charges. | This is a deliberately restricted experimental environment, **not** evidence such costs are zero in reality; no endogenous AI investment stock or separately costed adoption mechanism is approved. |
| **D5 — Information and outside option** | Public lagged market `P,Q`, private own history and technology; no individual rivals' actions/payoffs. Optional shutdown has `q=C=pi=0`, no forced exit or reentry delay. Rolling OLS and priors are recorded in the consolidated baseline (§ A6 — Consolidated minimal baseline). | Operational construction of feasible `qbar` and `Qref`, and exact participation-vs-production choice are still needed; no current-round price or unchosen realized payoff leakage. |
| **D6 — Learning and comparison** | 256 L3×L4×L5×L6 IDs, 200 rounds; L5 evaluates, L6 chooses. `optimization`, `trial_error`, `softmax`, `imitation` retained. Only chosen action updates learned outcomes; Target-price lexicographic distance/profit, rank-based Softmax, lagged-aggregate-trend imitation; compare **realized cumulative profit**. | Numeric `eta`, `epsilon`, temperature, `phi`, exploration/reentry convention, learning-score normalization, priors/ties; reproducible stochastic seeds, confidence intervals, robustness and economic gate tests. |

### Apparent contradictions resolved by chronology

1. **A5 sigma:** older unassigned G1/G2/G3 strata and empirical-calibration-first proposals are superseded by approved fully crossed scenarios `sigma=0.5,1,2` **for each** of the 100 original profiles (300 profile-sigma markets, 15,360,000 player-round observations per seed). Do not assign only one sigma to each original profile in this primary experiment or claim representative prevalence.
2. **A5 units:** earlier warning that dimensionless output cannot be sold is resolved by approval of a *configuration-specific normalized composite commodity*. It does **not** justify comparing physical output levels across configurations or reusing legacy diagnostic money values.
3. **A5 L1/L2:** historical technology-choice catalogs remain historical; the active 256-player roster is L3–L6 and common technology per configuration. The approved four-family relationship is a separate technology-counterfactual interpretation, not 12 extra player strategies.
4. **D1/D2/D3:** older “pending” headings describe the state *before* later approvals. The consolidated D3 factor-price baseline supersedes earlier `w=r=1` **diagnostic-only** labels for the *new intended baseline*, but does not validate old diagnostic runs.
5. **L5 `price` versus `target-price`:** old reserve-price bids/heuristic Cournot must not be treated as approved transaction institutions. One realized price is set solely by the actual inverse-demand equation.
6. **Imitation and adaptive:** legacy peer-level imitation and L5-adaptive own-payoff scoring conflict with the approved public-information boundary and separate L5 price-belief/L6 action-learning roles. Historical code behavior is not an approved A6 implementation.
7. **Shutdown:** a zero-output option has no defined target-price distance; it cannot be ranked as a perfect zero-distance production candidate. Participation is conceptually decided before production-action ranking; a minimal executable rule still requires signoff.

### Smallest outstanding decision set before A6 coding

- **Economic scale:** choose reproducible `a_c,b_c` (and whether fixed across time) so 256 simultaneous offers, reference `Qref_c` and abstract money/factor units are internally coherent. This is **not yet an approved numerical demand calibration**.
- **Reference forecast:** specify a feasible, frozen `qbar_ic` derived only from approved pre-round technology/endowments; set `Qref_c=sum_i qbar_ic`; avoid realized-price lookahead.
- **Participation:** define one minimal rule comparing shutdown to producing, preserving Target-price lexicographic ordering *conditional on production* and an explicit feasible reentry path.
- **Learning numerics:** select and pre-register only essential `eta`, `epsilon`, positive Softmax temperature or rank-only choice convention, `phi`, cold-start initialization and deterministic ties. If these affect incentives, request researcher approval rather than silently inserting defaults.
- **Experiment protocol:** specify independent seeds, paired random streams across sigma, independent market-run inference unit, parameter sensitivity and stop/go tests for no leakage, accounting identities, no double updating, zero-price losses, shutdown/reentry and all 16 L5-adaptive × L6-imitation policy intersections.

### Implementation acceptance boundary

The verified A5 Actions run #42186866398 passed **10 unit/smoke tests**, not the A6 economic integration or 300 full market runs. Old 5.12m diagnostic observations are historical; no final 15.36m A6 experiment, profit rankings, equilibrium or welfare claims are established here. The current five-item Game 1 completion checklist remains **0/5** until the outstanding economically meaningful choices are approved, code is integrated, CI and robustness pass, and outputs are reviewed.


## A6 — Minimal executable-model contract and pre-code consistency gate (2026-11-06)

**Research governance:** This section consolidates existing approvals; it is not an approval of missing economic parameters. Preserve the full historical decision log above. Do not modify the legacy diagnostic or present it as an approved experiment. `research_validated: false`.

### A. State, production, market, and payoff (approved)

For each original profile c=1..100 and each paired scenario sigma in {0.5,1,2}, reset one market with 256 immutable L3×L4×L5×L6 strategy identities and run 200 simultaneous rounds. Each strategy faces the same 20 task coefficients, initial K/L endowments and automation eligibility within a profile-sigma market. In each task use **one** execution mode: labor q_j=aL_j*l_j, k_j=0, or eligible capital q_j=aK_j*k_j, l_j=0. Enforce nonnegative allocations and total labor/capital caps. Freeze q0_j=aL_j*Lbar/20 and equal weights 1/20. Output is the normalized composite-good quantity

`y_i = CES_sigma(q_ij/q0_j; omega_j=1/20)`, `Y0=1`.

No productivity multiplier A change is introduced. For each round, all strategies choose without knowing the current clearing price. Total quantity `Q=sum_i y_i`; actual price `P=max(0,a_c-b_c*Q)`, with `a_c,b_c>0`; sold quantity equals output even if P=0. Utilized-service cost `C_i=w*sum_j l_ij+r*sum_j k_ij`; approved minimal baseline `r=1,w/r=1` and sensitivity `w/r=0.5,2`. No extra fixed/adoption/adjustment charge in the baseline. Realized profit `pi_i=P*y_i-C_i`; final comparison `Pi_i=sum_t pi_it`. Shutdown is a feasible zero-allocation choice with y=C=pi=0; no forced exit, no reentry cost/delay.

**Unit caveat:** y and Q are configuration-specific normalized-composite-good quantities, not directly comparable physical goods across profiles. Demand intercept/slope and factor prices must be defined in matching abstract-money units. The absence of extra costs is a deliberate model restriction, not a claim about real-world firms.

### B. Minimal information and behavior (approved concepts, not yet fully numeric)

Before round t, players see only lagged public P,Q and their own private actions/outcomes and own technology; no individual peer action/payoff or current-round P. L5 is an **evaluation/belief layer**, not a second learner: competitive assumes locally invariant predicted price; cournot incorporates predicted own-quantity price impact; target-price ranks positive-output candidates lexicographically by predicted-price distance from the approved markup-cost target, then predicted profit; adaptive updates its price expectation from lagged observed P. L6 is the **sole action-selection/feedback layer**: optimization, epsilon trial-and-error, temperature Softmax, or imitation of lagged aggregate output trend. Realized chosen-action outcomes update only that action, once; no unchosen realized payoff updates. Rank-based Softmax preserves lexicographic production-candidate ordering. Shutdown is outside the target-price distance ranking. Reentry remains possible. Preserve all 256 IDs; audit observational or functional equivalence rather than deleting IDs.

**Do not introduce:** separate participation reinforcement, second payoff ledger, individual-rival imitation, reserve-price rationing, inventory, investment stocks, adoption/adjustment costs, forced convergence, global Nash-equilibrium solver, or any unapproved learning states. Earlier elaborate D6.3.4 proposals are explicitly excluded from the baseline.

### C. Contradiction audit

| Issue | Finding | Required resolution |
| --- | --- | --- |
| Demand scale versus 256 normalized producers | **OPEN ECONOMIC PARAMETER**: `a_c,b_c` are not numerically approved; arbitrary legacy intercepts may force P=0 or render learning comparisons meaningless. | Specify a pre-treatment demand normalization and a compact sensitivity grid before A6 market runs. |
| Reference market quantity | **OPEN OPERATIONAL CONVENTION**: `qbar_i` and `Qref` lack a reproducible feasible construction. | Specify a fixed reference feasible plan independent of realized strategies/outcomes; ensure consistent dimensions and no price lookahead. |
| Target-price versus shutdown | **OPEN BEHAVIORAL RULE**: shutdown has undefined price distance; a lexicographic production score cannot directly compare to zero-profit shutdown. | Approve one minimal participation rule that uses predicted net benefit without adding a second learning engine; keep production ranking conditional on participation. |
| Learning numeric scale | **OPEN BEHAVIORAL PARAMETERS**: eta, epsilon, temperature, phi, initial scores, tie rule and possible reentry exploration are not approved. | Pre-register a minimal set, use rank-only sampling when possible to avoid arbitrary monetary scaling, and run a small sensitivity grid. |
| Public-only information versus legacy imitation | **CODE CONFLICT**: existing `peer_provider` can supply private individual peer actions/payoffs. | Replace with lagged aggregate P,Q trend; test all 16 L5-adaptive × L6-imitation intersections and forbid hidden peer fields. |
| L5 adaptive versus L6 learning | **CODE CONFLICT**: legacy adaptive valuation uses own payoff history as a substitute for price belief updating. | Separate price-belief state from chosen-action feedback; one update each and one realized profit accumulation. |
| L5 target-price versus legacy price offers | **CODE CONFLICT**: existing `price` L5 sets offered reserve prices. | Preserve historical IDs/results, implement target-price only in the new economic runner, and assert one actual uniform transaction price. |
| A5 normalized CES versus diagnostic output | **CODE INTEGRATION GAP**: approved normalized technology is not yet the full A6 market runner. | Wire normalized y consistently into candidate prediction, actual Q, revenue, and profits; do not reuse historical diagnostic payoffs. |
| 256 strategy IDs versus 256 distinct economic functions | **EMPIRICAL/SEMANTIC TEST NEEDED**: unique IDs need not yield unique decisions. | Compare complete task allocations and selected actions under controlled identical states; do not silently deduplicate. |
| Three sigma scenarios versus historic sigma groups | **RESOLVED**: fully crossed 100×3 markets, not one group per original profile. | Couple random streams across sigma, keep original profiles frozen and separate old diagnostic runs. |

### D. Pre-code release gate

**Specification consistent at the level of approved accounting identities, production rules and information boundaries. NOT READY for a scientifically interpretable full A6 run:** unresolved demand scale, feasible market reference, shutdown choice and learning numeric rules materially change incentives/outcomes. They must be explicitly decided or authorized as transparent scenario assumptions before implementation. Engineering details that do not change economic behavior need not be separately approved.

**After the four substantive gates close:** implement a new A6-specific runner without overwriting historical diagnostics; first run one-round accounting/no-leakage/zero-price/shutdown tests, then all 16 adaptive×imitation policy cases and reproducibility checks, then one-profile three-sigma smoke test, then 100×3×256×200 per seed with paired random streams. Report price/output/profit identities, cumulative-profit ranking, profile-paired sigma differences and independent-run uncertainty. CI success alone does not set `research_validated: true`.


## A6 implementation staging note — 2026-11-06

Researcher requested implementing the three compact operational conventions and staged tests. The new isolated module `src/interfirm_abm/task_a6_market.py` implements: (i) shutdown when the maximum forecast production profit is nonpositive, re-evaluated each round; (ii) a feasible 20-task equal-labor A5 reference with `qbar_i=1` and `Qref=256` for the full roster; and (iii) rank-based Softmax with temperature applied to ordinal ranks, not money-valued scores. `tests/test_task_a6_market.py` and `.github/workflows/a6-staged-checks.yml` were added.

**Important implementation limitations:** The runner requires the caller to inject actual demand intercept/slope, epsilon, temperature, imitation probability and seed. Test fixtures use **illustrative numbers only**, not approved demand calibration. The current implementation records chosen-action feedback but **does not yet use exponential recency-weighted reinforcement for L6 decisions**, does not implement the approved rolling-OLS D5 market-belief fallback, and uses a simplified Cournot/target-price forecast and simplified adaptive belief update. It also reuses diagnostic L3/L4 action proposals, so their substantive behavioral semantics require a separate audit. Therefore it is an **integration scaffold**, not a complete D1–D6 implementation; passing its invariant tests would not close A6 or authorize a 15.36m-row economic-results claim.

The new CI workflow is configured for push/manual dispatch; successful execution logs have **not yet been verified**. Next required gates: (1) review demand scale and numerics; (2) complete D5 belief estimation and D6 chosen-action reinforcement without adding a second learning layer; (3) test 16 adaptive×imitation intersections, no leakage and shutdown/reentry; (4) full 256-player × 200-round smoke across 3 sigma; (5) 100×3 markets per seed, robustness and paired inference. Preserve `research_validated: false` until those checks pass.


## A6 checklist step 2 — L3/L4 semantic and code audit (2026-11-06)

**Scope:** Audit only. No behavioral mechanism, new cost, technology shock, or numerical parameter is approved by this section; no simulation code modified. Keep all 256 L3×L4×L5×L6 IDs and historical diagnostic code. `research_validated: false`.

**Sources examined:** `src/interfirm_abm/task_layer_registry.py`, `src/interfirm_abm/task_strategy_actions.py`, `src/interfirm_abm/task_strategy_engine.py`, `src/interfirm_abm/task_a6_market.py`, `src/interfirm_abm/task_a5_normalized.py`, `docs/games/game1/strategy_layers_literature.md`, and this canonical A5/A6 decision history.

### L3 mapping: labels versus actual behavior

| L3 ID | Historical literature meaning | Current diagnostic action rule | A6 audit |
| --- | --- | --- | --- |
| `flexible` | Freely reallocate K/L within endowments | Equal task weights; capital execution for eligible tasks varies with action index | Feasible candidate generator, not proof of global flexible optimization |
| `capacity` | Binding installed capacity constraint | Weight tasks by max feasible labor/capital productivity | **Semantic mismatch:** productivity priority is not a distinct installed-capacity constraint; common K/L caps already bind all players |
| `adjustment` | Intertemporal reallocation friction/cost | Shift priority and capital task subset with `len(own_history)` | **Semantic mismatch:** arbitrary history-count cycle, no adjustment-cost/state equation |
| `investment` | Expand capacity through investment | Upweight automation-eligible tasks; mode varies by effort index | **Semantic mismatch:** no investment decision, budget, capital accumulation or capacity expansion |

### L4 mapping: labels versus actual behavior

| L4 ID | Historical literature meaning | Current diagnostic action rule | A6 audit |
| --- | --- | --- | --- |
| `eligibility` | AI extends capital-executable task set | Use capital for all already-eligible tasks | **Partial:** respects eligibility but does not change it |
| `efficiency` | AI increases capital task productivity | Choose capital if `aK>aL` | **Semantic mismatch:** a selection threshold is not a technology productivity shock; raw aK/aL comparison is not factor-price-adjusted |
| `adoption_cost` | Fixed/sunk adoption cost | Choose capital if `aK>1.25*aL` | **Semantic mismatch:** no adoption payment or state; 1.25 is an unapproved diagnostic hurdle |
| `combined` | Eligibility + efficiency + adoption cost | Choose capital if `aK>1.10*aL` | **Semantic mismatch:** 1.10 is an unapproved diagnostic hurdle, not combined economic channels |

**Shared action-generation caveats:** `INTENSITIES=(0.30,0.48,0.66,0.84)` are unapproved diagnostic effort levels. Every generated candidate is constrained by the firm's initial K/L caps and pure-mode task execution, but economic distinctness across all 256 labels has not been established. A6's `_candidate_plans` currently calls `build_actions` and discards the legacy L5 reserve-price offer; therefore L3/L4 diagnostic heuristics already affect A6 scaffold outcomes. Do not present scaffold rankings as evidence of the named economic mechanisms.

### Conflict with current approved minimal A6

A6 deliberately excludes endogenous investment stocks, adjustment costs, adoption costs and additional AI technology shocks. Accordingly the historical literal interpretations of `L3.adjustment`, `L3.investment`, `L4.efficiency`, `L4.adoption_cost` and `L4.combined` cannot all be claimed as implemented **without** violating the minimal A6 restriction. The only safe immediate conclusion is that the current four-by-four labels are preserved but their causal/economic meanings remain unresolved.

**Economically relevant researcher decision required (one choice, not a parameter survey):** Decide whether (A) retain all 256 IDs but explicitly reinterpret L3 as four *static resource-allocation heuristics* and L4 as four *static task-mode selection heuristics*, with names/labels mapped transparently and no investment/adoption/adjustment claims; or (B) retain the literal investment, adjustment and automation mechanisms, which requires reopening the minimal A6 design and approving additional dynamic states/costs/technology transitions. Neither option is approved by this audit.

**Recommendation for simplicity:** Option A, provided the researcher explicitly accepts that Game 1 then compares decision heuristics under fixed technology, not endogenous AI investment/adoption. Do not silently rename the strategy IDs: preserve historical IDs, use separate display descriptions/aliases only after approval.

**Next engineering gate after decision:** Unit-test L3×L4 for feasibility, factor-price-aware task-mode logic where relevant, controlled behavioral differences, stable candidate identities, absence of unapproved thresholds and no hidden information. Then audit L5/L6 and D5 before interpreting 200-round or full-sample outcomes. **Step 2 audit completed; economic-semantic decision OPEN; code integration NOT AUTHORIZED by this document.**


## A6 step 2 — Researcher approval: L3/L4 option B (2026-11-06)

**APPROVED BY PRINCIPAL RESEARCHER:** Preserve the literal economic meaning of L3/L4 instead of relabeling their existing diagnostic heuristics as the scientific mechanisms. Keep all 256 L3×L4×L5×L6 player identities, including every intersection. This **supersedes the preceding audit's recommendation A**, not the factual audit. Continue checklist work, but **do not add unapproved economic assumptions or numerical parameters**. `research_validated: false`.

### Binding semantic requirements (mechanisms, not yet parameterized)

- **L3 flexible:** Reallocation of K/L subject to resource feasibility; distinguish from other mechanisms by the feasible intertemporal action set.
- **L3 capacity:** Explicit installed-capacity/endowment constraint rather than simply weighting high-productivity tasks. Specify how it differs from the common K/L endowment caps before implementation.
- **L3 adjustment:** Real reallocation friction/cost or adjustment constraint that depends on a prior allocation. Arbitrary history-count rotation does not satisfy this label.
- **L3 investment:** Explicit investment decision and capital/capacity law of motion, including economic resource/budget consequences and any irreversibility if claimed. Prioritizing automation-eligible tasks alone does not satisfy this label.
- **L4 eligibility:** Actual transition in task capital eligibility, not simply selecting from already eligible tasks.
- **L4 efficiency:** Actual productivity change for capital-executable tasks, not a raw aK>aL rule.
- **L4 adoption_cost:** Explicit adoption payment/state or a researcher-approved equivalent economic cost mechanism, not arbitrary productivity thresholds.
- **L4 combined:** Coherent combination of the above channels, with explicit accounting and no double counting.

**Design consequence:** Option B requires revisiting the former minimal A6 exclusion of investment stock, adjustment/adoption charges and technology transitions **only to the extent needed to implement the approved literal L3/L4 meanings**. This is a conflict to resolve, not permission to invent cost functions, depreciation rates, investment returns, technology shocks, adoption schedules or new learning layers. Maintain A5 normalized CES and the D1–D6 accounting/information rules unless the researcher explicitly amends them. Separate resource investment from AI technology changes; do not silently reintroduce multiplicative A or infer AI raises productivity when a different channel is approved.

### Checklist and release gates

1. **Completed:** Audit L3/L4 diagnostic implementation; identify mislabeling and semantic conflicts; record explicit approval of B.
2. **NEXT — minimal mechanism contract (specification only):** For each of eight L3/L4 options, state the smallest economically valid state variable, action, transition, feasible constraint and accounting effect; show interactions and identify shared states to avoid duplicates. Mark any equation or magnitude not already approved as **OPEN**.
3. **NEXT — contradiction gate:** Reconcile L3/L4 with D4 no-extra-cost baseline and the fixed shared-technology assumption; distinguish within-market common exogenous technology from player-specific endogenous technology states, and preserve the approved profile-sigma paired comparisons. If literal mechanisms cannot be implemented under existing assumptions, seek explicit amendment rather than coding a substitute heuristic.
4. **After approval of the necessary economic equations and parameters:** Refactor the A6-specific action generator and market runner, retain historical diagnostics, and add controlled mechanism-distinctness, feasibility, accounting and no-double-count tests.
5. **Later:** D5 and L5/L6 completion, 200-round verification, 100×3×256×200 per seed and robustness; no full sample or ranking until gates close.

**Current status:** B approved at the semantic level. Its dynamic economic implementation and any relaxation of D4 or technology restrictions are **NOT YET APPROVED**. No source code or CI changes authorized by this approval alone. `research_validated: false`.


### Step 2B — Minimal state/action contract (audit draft, not approved economics)

| Mechanism | Minimum observable state | Action and transition needed | Accounting/feasibility gate |
| --- | --- | --- | --- |
| L3 flexible | Current K/L allocation and endowments | Reallocate within endowments each round | No added adjustment friction |
| L3 capacity | Installed task/aggregate capacity beyond shared resource endowments, if distinct | Choose production within that binding capacity | **OPEN:** what distinct capacity object exists? |
| L3 adjustment | Previous K/L allocation | Choose new allocation; impose adjustment constraint or charge | **OPEN:** adjustment technology and charge/constraint |
| L3 investment | Productive capacity/capital stock and previous investment | Choose investment and update stock over time | **OPEN:** resource budget, stock law, timing, depreciation if any |
| L4 eligibility | Current task-level automation eligibility | Adopt/enable tasks and update eligibility | **OPEN:** which tasks, timing, reversibility, costs |
| L4 efficiency | Task-level capital productivity state | Apply AI-driven efficiency transition | **OPEN:** shock size, affected tasks, persistence |
| L4 adoption_cost | Adoption state | Choose adoption and incur its cost when applicable | **OPEN:** fixed/sunk cost and whether repeated |
| L4 combined | Shared eligibility, efficiency and adoption states | Combine transitions without duplicate charges | **OPEN:** ordering and interaction |

**State-sharing principle:** L3 investment and L4 efficiency/eligibility must not create duplicate capital or technology ledgers. L3 adjustment references previous allocations; L4 adoption_cost and combined reference one shared adoption ledger. This is a data-model design constraint, not a newly approved economic law.

**Contradiction gate (OPEN):** Existing A6 D4 excludes investment/adoption/adjustment charges and dynamic stocks, while approved B requires economically literal mechanisms. Likewise A5 technology is common and frozen across all 256 players within each market, whereas endogenous L4 eligibility/efficiency may change a player's effective task technology. The principal researcher must explicitly resolve these contradictions before implementation. Do not claim a common technology after players adopt different technologies; alternatively treat a common pre-adoption technology as the initial shared baseline, with player-specific endogenous states clearly labeled. No assumption is approved here.

**Single consolidated researcher decision to request next:** whether to authorize the **minimal necessary exception** to D4 and frozen-technology restrictions for literal L3/L4, retaining fixed common initial technology and a single shared accounting framework, while leaving all magnitudes/equations OPEN for subsequent specification. Without that decision, step 2B cannot advance to economic equations or executable code. `research_validated: false`.


## A6 step 2B — Researcher approval of minimal L3/L4 exception (2026-11-06)

**APPROVED:** Principal researcher explicitly authorizes the smallest necessary exceptions to the former frozen-technology/no-extra-cost A6 restriction so the literal L3/L4 mechanisms approved under option B can be modeled. The approval covers **scope only**, not economic equations, numeric magnitudes, or specific transition assumptions.

**Binding scope:**
1. Retain all 256 L3×L4×L5×L6 strategy identities and a common *initial* 20-task technology/endowment profile for all players in each profile–sigma market.
2. Allow economically necessary state transitions for L3 capital/capacity investment and adjustment, and L4 task eligibility, capital-task efficiency, and adoption, with the minimum corresponding resource/accounting effects.
3. Player-specific technology/capacity may diverge **after** decisions; do not describe the entire trajectory as common frozen technology.
4. Retain approved D1–D3 common-market quantity clearing and utilized-factor-service costs; distinguish capital investment expenditure from capital-service rental and do not charge the same resource twice.
5. Keep a single shared state/accounting framework, a single L6 action-feedback layer, public-only lagged P,Q and own private history; do not introduce extra learning layers, peer-level observability, unapproved shocks, or new player identities.
6. Preserve the A5 normalized initial reference and sigma comparisons; endogenous task technology requires an explicit rule for whether the normalization anchor remains frozen at the original pre-treatment q0 (OPEN, not yet decided).

**Explicitly NOT approved:** functional forms for investment/adjustment/adoption costs, capital accumulation/depreciation, eligibility transition/irreversibility, efficiency shock magnitudes or persistence, per-task capacity, timing/order of simultaneous decisions, financial budgets/borrowing, or demand calibration. The previous D4 zero-extra-cost baseline is superseded **only for the minimum costs necessary for literal L3/L4**; it remains the comparison benchmark, not a claim that all costs are zero.

### Next checklist gate — specify minimal economic equations, no code yet

Draft one parsimonious shared state vector and round timeline, then propose equations for (i) resource allocation and capacity, (ii) adjustment/investment stock law and expenditure, (iii) eligibility/efficiency/adoption and their payment timing, and (iv) production/cost/profit identities. Flag every new assumption and numeric parameter as PROPOSED until separately approved. Explicitly test dimensional consistency and potential duplicate charging. Only after the researcher approves equations/assumptions may the A6 runner be refactored and tested.

**Status:** Step 2 L3/L4 semantic choice B approved; minimal scope exception approved; equations and parameters still OPEN. No simulation code change, no full-sample run, and `research_validated: false`.


## A6 step 2C — Proposed single shared dynamic economic system for literal L3/L4 (2026-11-06)

**PROPOSAL ONLY; NOT RESEARCHER-APPROVED EQUATIONS.** This is a parsimonious common state/transition/accounting contract for all 16 L3×L4 pairs, not eight separate economic models. Preserve all 256 L3×L4×L5×L6 player IDs, common initial technology per profile–sigma, lagged public information only, and A5 normalized 20-task CES. All parameters, timing and state transition choices marked OPEN require principal-researcher approval. No simulation code changes. `research_validated: false`.

### Shared state, actions and feasible production

For player i, task j=1..20 and period t, define shared state `S_it=(K_it, x_i,t-1, e_ijt, aK_ijt, z_ijt)`, where K is productive capital capacity, x is previous task K/L allocation, e is binary task capital eligibility, aK is task capital productivity, and z is adoption status. Baseline task labor productivity aL_ij and labor endowment Lbar_i remain fixed. Initial states are identical for all players within the same profile–sigma market. **OPEN:** whether adoption status z is required separately from e (remove if redundant).

Choose `d_it=(l_ijt,k_ijt,I_it,u_ijt)` with nonnegative task allocations, investment I and adoption decisions u. Feasibility: `sum_j l_ijt <= Lbar_i`, `sum_j k_ijt <= K_it`, and capital execution requires e_ijt=1 at the moment of production. Each task uses labor OR capital, not both. Task output is `q_ijt=aL_ij*l_ijt` in labor mode or `q_ijt=aK_ijt*k_ijt` in eligible capital mode.

Normalized output is `Y_it=CES_sigma(q_ijt/q0_ij; weights 1/20)` with `q0_ij=aL_ij*Lbar_i/20`, frozen at the initial reference. Sigma=1 uses the continuous Cobb–Douglas limit. **OPEN:** freeze q0 across endogenous adoption/investment transitions (recommended for comparability; not yet approved).

### Minimal common transition and accounting equations (proposals)

- Capital: `K_i,t+1=(1-delta)*K_it+I_it`. **OPEN:** delta, investment units, whether I becomes usable only at t+1, and investment financing/budget. Avoid charging both full investment principal and an overlapping rental user cost if r already represents the same capital financing/depreciation service.
- Eligibility: `e_ij,t+1=max(e_ijt, uE_ijt)`, where uE is an eligibility-adoption decision. **OPEN:** irreversible versus reversible, which tasks can transition, whether all are potentially eligible, and activation timing.
- Efficiency: `aK_ij,t+1=aK_ijt*(1+g_ijt*uG_ijt)` as a simple candidate law. **OPEN:** g, whether upgrades are one-off, caps and persistence; no productivity multiplier A shock.
- Adoption: one common ledger `z_ij,t+1=max(z_ijt,uE_ijt,uG_ijt)` and one payment event per newly adopted task, e.g. `C_adopt_it=f*sum_j max(0,z_ij,t+1-z_ijt)`. **OPEN:** whether adoption is per task or firm, cost f, and eligibility/efficiency payment separation. L4 combined must not duplicate payments.
- Adjustment: `C_adj_it=(gamma/2)*||x_it-x_i,t-1||^2` is a **candidate functional form only**. **OPEN:** gamma, scaling of K versus L, and whether adjustment is a cost or a feasibility limit. Previous allocations are required only if this channel is active.
- Investment expenditure: `C_inv_it=pI*I_it` is a **candidate cash-flow convention**, not automatically an economic profit cost if rented capital services `r*sum k` already internalize financing. **OPEN:** whether the outcome is operating profit, cash flow or discounted economic value; choose exactly one coherent capital accounting treatment.

### Unified market accounting (preserve approved D1–D3)

All players choose simultaneously using only lagged public P,Q and private own state/history. `Q_t=sum_i Y_it`, `P_t=max(0,a_c-b_c*Q_t)`; revenue `R_it=P_t*Y_it`. Baseline operating cost `C_oper_it=w*sum_j l_ijt+r*sum_j k_ijt`. A general cash-flow identity, **not yet approved as the tournament objective**, is `CF_it=R_it-C_oper_it-C_adj_it-C_adopt_it-C_inv_it`. **OPEN:** investment/rental consistency, whether stock value/salvage is needed, and whether final ranking uses cash flow or economic profit. Shutdown of production does not necessarily imply zero investment/adoption expense if those actions are allowed; the original D5 zero-payoff shutdown outside option must be reconciled explicitly.

### L3/L4 are action-set and transition switches, not independent models

| Layer | Option | Shared-model interpretation | Economic gap still OPEN |
| --- | --- | --- | --- |
| L3 | flexible | Reallocate l,k within endowments | Difference from common constraints |
| L3 | capacity | Bind task/installed capacity in addition to common K cap | Exact capacity object and law |
| L3 | adjustment | Activate previous-allocation adjustment channel | Cost versus constraint, scaling |
| L3 | investment | Activate I and capital transition | Budget, timing, capital accounting |
| L4 | eligibility | Activate eligibility transitions uE | Eligibility set, persistence, adoption cost |
| L4 | efficiency | Activate productivity transition uG | Gain magnitude, persistence, payment |
| L4 | adoption_cost | Activate adoption/payment channel | What adoption enables without duplicating eligibility/efficiency |
| L4 | combined | Combine applicable eligibility, efficiency and adoption channels | Single shared adoption ledger; no double payment |

**Semantic blocker:** `L4.adoption_cost` cannot be economically distinct merely by adding a cost to an otherwise identical non-adoption action. Specify what technology/service adoption buys. `L3.capacity` likewise needs a constraint different from the K/L endowment already shared by every player.

### Contradiction / double-count checklist

1. Fixed initial technology **versus** endogenous post-decision player-specific technology: compare paired sigma scenarios using the same initial profile and common exogenous settings; report realized heterogeneity.
2. Capital expenditure `pI I` **versus** rental `r sum k`: identify economic interpretation and ensure no double charge; optionally track cash flow and operating profit separately, but choose tournament ranking explicitly.
3. L3 adjustment and investment: a change in capacity and a change in utilization are not the same action; count their charges only where applicable.
4. L4 eligibility/efficiency/adoption_cost/combined: shared adoption state, one payment per event; no cost-only strategy with no corresponding benefit.
5. Zero-profit shutdown/reentry: clarify whether no-production firms may still invest/adopt, and whether zero-payoff outside option means **no action**.
6. CES normalization: retain initial q0 to avoid endogenous rebasing; verify nonnegative and finite output for sigma<1 and zero tasks.
7. No future leakage: transitions at t+1 are not observable as current market information to other players; chosen-action realized feedback updates once.

**Decision status:** The principal researcher approved literal L3/L4 meanings and the minimal exception scope, but **has not approved any of the proposed equations, state variables, timing or parameters in this section**. Next step: resolve capital accounting, L3 capacity and L4 adoption_cost semantics before selecting numeric calibration. Do not implement the proposed equations without approval.


## A6 step 2D — Three economic conflicts: capacity, adoption, capital accounting (2026-11-06)

**STATUS: PROPOSED RESOLUTIONS FOR RESEARCHER APPROVAL; NOT APPROVED EQUATIONS.** No new numerical values, model code or experiments are authorized here. All 256 strategy identities and the single shared L3/L4 state framework remain unchanged. `research_validated: false`.

### D1. L3 capacity distinct from flexible

Common resource caps `sum_j k_ijt <= K_it` and `sum_j l_ijt <= Lbar_i` apply to *every* L3 option, so they cannot by themselves distinguish capacity from flexible. **Proposal:** For L3.capacity alone impose an installed task-throughput limit `q_ijt <= h_ij` for each task, in addition to the common caps; L3.flexible does not have this additional task-specific bound. h is a physical/task-capacity state, not the productivity weight used in legacy `task_strategy_actions.py`. **OPEN:** how h is initialized from pre-treatment information, whether h can change through investment, and how a positive binding constraint is guaranteed without an arbitrary ratio. No new cost is needed just to impose a constraint.

### D2. L4 adoption_cost must buy a real technological opportunity

One shared technology state `(e_ijt,aK_ijt,z_ijt)` and a single adoption event ledger can support eligibility and efficiency transitions without duplicating costs. **Proposal:** Charge adoption once only when a previously unavailable capability becomes active, `C_adopt_it=f*sum_j 1[z_ijt=0 and z_ij,t+1=1]`, with f>=0. **OPEN:** whether the paid opportunity is task eligibility, efficiency enhancement or both; whether free versions of eligibility/efficiency exist in other L4 options; how adoption_cost is distinct from combined; whether a separate z state is necessary. A cost-only rule with no access to a benefit is economically invalid for the intended label. Do not assume costless adoption or a specific f without approval.

### D3. Capital services versus investment cash flow

Preserve baseline operating-accounting identity `pi_oper_it=P_t*Y_it-w*sum l_ijt-r*sum k_ijt` for comparability, but **do not** assume the same r charge is a cash payment for owned capital. **Proposal:** Report a distinct investment cash-flow measure `CF_it=P_t*Y_it-w*sum l_ijt-C_adj_it-C_adopt_it-pI*I_it` under an owned-capital convention; in that convention r is a shadow/user cost for operating-profit analysis, not an additional cash charge. If r is a true rental paid to an external owner, a different financing/ownership model is needed; do not subtract both r*k and pI*I without an explicit non-overlapping interpretation. **OPEN:** tournament payoff definition (economic profit versus cash flow), capital terminal value after 200 rounds, depreciation, discounting and whether L3.investment can finance I. No ranking of investment strategies until one consistent intertemporal objective is approved.

### Release gate

These proposals isolate the minimal economic choices without introducing arbitrary numerical parameters. Principal researcher must approve (i) task-specific capacity bound and its initialization, (ii) what the adoption fee buys and its distinction from combined, and (iii) capital ownership/payoff accounting before dynamic L3/L4 equations can be finalized. Do not convert these proposals into A6 code or mark the checklist closed on the basis of documentation alone. `research_validated: false`.


## A6 step 2D — Researcher approval: L3 Capacity A (2026-11-06)

**APPROVED:** L3 `capacity` imposes an additional task-specific **output/throughput cap** `0 <= q_ijt <= h_ij`, alongside the common total labor/capital endowment constraints. L3 `flexible` has no such additional task-specific output cap. This replaces the alternative task-specific K/L input caps (option B), which are **not approved**. Keep the full 256 strategy identities.

**Still OPEN:** How `h_ij` is determined from the common pre-treatment configuration without arbitrary calibration; whether it is constant or can change through L3 investment; whether capacity is defined in task-output units before CES normalization; how to ensure a nontrivial binding case without inventing an h ratio. Do not choose any h value or equation until researcher approval. A constraint is not itself a new operating cost.

### Next economic decision — L4 adoption_cost

The researcher has **not yet approved** what payment buys. Economically meaningful alternatives to present for decision:

- **A (single capability activation):** An adoption payment unlocks an otherwise unavailable *task-level capital eligibility* option. Once activated, it remains available subject to an approved persistence rule. Must distinguish from L4 eligibility (potentially free activation) and combined.
- **B (efficiency upgrade):** An adoption payment unlocks a *task-level capital productivity upgrade*. Must distinguish from L4 efficiency (potentially free upgrade) and combined.
- **C (shared activation for both):** A single payment unlocks a specified combination of eligibility and efficiency at the task level, using one adoption ledger and no duplicate charging. Must distinguish from combined, potentially by policy timing/action set or explicit restrictions, without inventing them.

These are **decision alternatives, not approvals**. No fee `f`, efficiency gain `g`, adoption timing, persistence, eligibility scope, or adoption cost function is approved. The original L4 `combined` label must remain coherent under whichever alternative is chosen; require a strategy-distinctness test before claiming 256 economically distinct behaviors.

**Status:** Capacity A approved and documented; adoption semantics and capital accounting still OPEN; no code or test changed; `research_validated: false`.


## A6 step 2E — Researcher approval: L4 adoption_cost A; combined and capital accounting audit (2026-11-06)

**APPROVED:** L4 `adoption_cost` means a player incurs a real adoption payment in exchange for **unlocking capital eligibility in a previously labor-only task**. This selects alternative A and rejects efficiency-only (B) and joint eligibility-plus-efficiency (C) as the defining benefit of `adoption_cost`. Preserve all 256 L3×L4×L5×L6 identities, shared initial profile and the approved L3.capacity output bound `0<=q_ijt<=h_ij`. **NOT APPROVED:** amount or functional form of payment, per-task vs bundled charging, exact activation timing, reversibility, task subset, eligibility transition dynamics, or whether `combined` incurs identical payment. No code change; `research_validated: false`.

### L4 combined: non-equivalence gate

- `eligibility`: changes task capital eligibility (the payment convention remains OPEN).
- `efficiency`: changes capital-task productivity, not eligibility.
- `adoption_cost`: changes eligibility **and charges an explicit adoption payment** (approved semantic distinction from eligibility).
- `combined`: must permit **both eligibility and efficiency changes**; how its adoption payment applies must be separately specified, and a single eligibility-unlock event must never be charged twice.

**Key finding:** Under otherwise identical eligibility transitions, `eligibility` and `adoption_cost` may choose identical allocations but have different net payoffs because of adoption expense; this is an economically valid distinction if payment timing is consistent. `combined` is not identical to `adoption_cost` only if its additional efficiency channel is genuinely available/activated. In states where no efficiency upgrade is feasible, observational equivalence is possible and must be reported rather than hidden. Do not invent an extra benefit solely to force distinctness.

### Capital accounting: candidate coherent conventions (OPEN)

**Ownership/investment cash-flow convention (candidate A):** A firm owns its productive capital stock `K_it`; `I_it` is purchased capital that enters `K_i,t+1` according to an approved stock law. Net period cash flow may be defined `CF_it=P_t Y_it - w sum l_ijt - C_adj_it - C_adopt_it - pI I_it - C_othercash_it`, where `C_othercash` includes only separately justified real cash expenses. Do not subtract a hypothetical rental charge `r sum k` again from this cash flow if r is merely the imputed opportunity cost of owned capital. An economic objective needs an explicit treatment of financing/opportunity cost and terminal residual stock value; cash-flow rankings alone may penalize investment with delayed returns.

**Rented-capital operating convention (candidate B):** The player rents utilized capital services at `r sum k`, so period operating profit is `pi=P_t Y_it-w sum l_ijt-r sum k_ijt-C_adj_it-C_adopt_it`. Under this convention an additional `pI I` investment purchase is **not** automatically meaningful unless a separate owned-capacity right/asset and its financing, rental returns and salvage are defined. If investment expands owned capacity while capital services are rented, distinguish the two assets and do not reuse one `K` ledger ambiguously.

**Important qualification:** Paying `pI I` and a capital-service charge `r k` is not *intrinsically* double counting if they represent nonoverlapping capital goods, depreciation, financing or service flows. It is **unjustified** to add both without an explicit ownership and accounting interpretation. In either convention, distinguish period accounting from the intertemporal tournament objective, treatment of investment at t=200, and shutdown with no production but possible investment.

**Researcher decision requested next:** Choose **A** owned productive capital + investment cash-flow accounting, or **B** rented capital services + separately defined investment-capacity asset. Neither is approved by this section; no rental, discount, depreciation, financing or terminal-value parameters are set. Preserve baseline `r=1,w=1` as a historical operating benchmark but do not assume it is a cash cost in A.

**Checklist:** L3 capacity semantics approved; L4 adoption_cost unlock benefit approved; L4 combined differentiated at the mechanism level, payment rule OPEN; capital accounting convention OPEN; final equations and numerical parameters OPEN; code unchanged; `research_validated: false`.


## A6 step 2F — Researcher approval: owned-capital accounting A (2026-11-06)

**APPROVED BY PRINCIPAL RESEARCHER:** A6 uses **firm-owned productive capital**, and L3 `investment` purchases additions to that owned capital stock. Investment expenditure is recognized in cash flow; do **not** automatically subtract a second hypothetical capital rental payment for the same owned capital services. This supersedes candidate B (rented capital with separately defined capacity asset) for the dynamic A6 L3/L4 model. Preserve all 256 player identities and the approved literal L3/L4 mechanism meanings, L3 capacity task-output cap and L4 adoption_cost paid eligibility unlock. **This approval selects an accounting convention, not its unresolved equations or parameter values.** No code changes; `research_validated: false`.

### Accounting identities: approved principle versus proposed formulas

The previously approved static D3 operating benchmark `C_oper=w*sum l+r*sum k` remains useful as an **imputed capital-service economic-cost diagnostic**, but the `r sum k` term must **not** also be charged as a cash payment for the same owned capital in A6's owned-capital cash-flow ledger. Distinguish clearly between:
- **Gross operating cash surplus before investment and adoption/adjustment payments (candidate identity):** `OCS_it=P_t Y_it-w*sum_j l_ijt`, assuming labor is paid per unit utilized; whether additional genuine cash operating charges exist is OPEN.
- **Net period cash flow (candidate identity):** `CF_it=OCS_it-C_adj_it-C_adopt_it-pI*I_it`. This is a cash-flow accounting proposal, not yet an approved tournament payoff; cost functions and payment timing remain OPEN.
- **Imputed operating economic profit (diagnostic only):** `pi_imputed_it=P_t Y_it-w*sum_j l_ijt-r*sum_j k_ijt`, where r is an opportunity/user-cost proxy, not an additional cash expense. This measure must not be conflated with CF or used to assert that investment was already paid for.

**Critical distinction:** Omitting an imputed capital rental from cash flow does not make owned capital economically free. Initial endowment ownership, financing/opportunity cost, depreciation, discounting, and terminal residual value may matter for cross-strategy welfare and investment rankings. Do not mix period CF and imputed economic profit in one cumulative score or double-charge pI and an overlapping user cost.

### Minimal remaining equations and researcher approvals — not yet selected

| Topic | Candidate equation / decision point | OPEN assumption or parameter |
| --- | --- | --- |
| Capital stock | `K_i,t+1=(1-delta)K_it+I_it` | Depreciation delta, purchase-price units pI, I feasibility/financing, investment activation at t+1, whether non-investment L3 choices have I=0 |
| Investment objective | `V_i=sum_{t=1}^{200} beta^(t-1) CF_it+beta^200 V_T(K_i,201,technology_i,201)` | Discount beta, terminal asset valuation V_T, initial asset value/cost baseline, whether rank uses V versus undiscounted CF; no numeric values approved |
| Task throughput | `q_ijt<=h_ij` for L3.capacity | Ex ante h initialization, units, persistence and any interaction with L3.investment |
| Adjustment | `C_adj=G(x_it,x_i,t-1)` | Whether monetary friction or adjustment-feasibility constraint, cost form, scaling and first-round previous allocation |
| Adoption | `e_ij,t+1=max(e_ijt,uE_ijt)`, paid eligibility unlock | Payment event and price, per-task versus bundle, activation timing, persistence, eligible set, single-charge ledger |
| Efficiency | `aK_ij,t+1=H(aK_ijt,uG_ijt)` | Productivity gain rule, upgrade timing, repeatability and cost treatment in L4.combined |
| CES normalization | `q0_ij=aL_ij*Lbar_i/20` initially | Explicitly freeze q0 across investment/adoption or approve a different fixed comparison convention |
| Shutdown/reentry | `l=k=I=u=0` as no-action option | Whether shutdown forbids investment/adoption in the same round; avoid asserting zero payoff for zero production if expenditures are allowed |
| Tournament metric | Compare cumulative net cash flows or intertemporal asset-adjusted values | Treatment of terminal investment and discounting; do not rank investment strategies on arbitrary horizon accounting |
| Demand and learning | Existing D1 inverse demand and D5/L6 approval ledger | Demand a,b; rolling OLS implementation; minimal L6 numerics, without new learning layer |

### Economic consistency gate

1. Same initial owned-capital endowment and task technology across 256 players per profile–sigma; subsequent divergence arises only from modeled decisions. Capital cannot be simultaneously represented as an externally rented service and a purchased owned asset without a separately approved interpretation.
2. Production at t cannot use capital purchased for t+1 unless the researcher explicitly approves immediate installation.
3. A paid eligibility-unlock event must be booked exactly once and cannot be silently charged again by L4.combined.
4. The cost of changing an allocation (adjustment) and the purchase of a new productive capital asset (investment) are distinct economic events.
5. A shutdown outside option has zero cash flow only if the player also undertakes no investment/adoption/adjustment expenditures.
6. Avoid terminal-horizon bias: a final-round capital purchase cannot be treated as worthless solely because no future rounds remain unless a terminal-value rule is explicitly approved.
7. Retain the 256 identities even if some options are behaviorally equivalent in certain states; test differences in designed states rather than inventing shocks or deleting strategies.

**Next checklist action:** Obtain approval for a *single minimal intertemporal payoff convention*, particularly treatment of terminal owned capital and discounting, then finalize the common stock/cost/technology equations and run a purely mathematical consistency review. **No code implementation or numerical calibration is authorized yet.** `research_validated: false`.


## A6 step 2G — Approved terminal-capital-inclusive ranking and minimal equation closure (2026-11-06)

**RESEARCHER APPROVAL:** Choose ranking convention **A**, which includes the cash flows earned during 200 rounds **plus the remaining value of owned productive capital at the end of round 200**. The principal researcher did **not** approve a numerical salvage value, depreciation, discount factor, investment price, or any other parameter. Preserve 256 identities and the shared-state L3/L4 economic mechanisms. No code change; `research_validated: false`.

### Approved principle; mathematical identity proposed for precise timing

Define `CF_it` as the owned-capital net cash flow with no imputed rental payment for the same owned capital. Define `K_i,201` as the capital stock after the last round's investment and depreciation transitions. A **candidate no-discount bookkeeping representation**, conditional on separate approval of no discounting, is:

`Score_i = sum_{t=1}^{200} CF_it + V_T(K_i,201)`.

More generally, `Score_i = sum_{t=1}^{200} d_t CF_it + d_T V_T(K_i,201)`, where discount weights `d_t,d_T` are **OPEN**. The approved content is *inclusion of terminal owned-capital value*, not the weights. **OPEN:** whether terminal valuation is gross asset value or incremental value above a common initial-endowment benchmark, whether the terminal value also includes any independently valuable adopted technology, and how to prevent residual-value double counting with investment expenditure. In paired initial states, subtracting a common initial asset baseline does not affect within-market ranks, but this does not settle cross-market comparisons.

### One common economic system — candidate equations and missing choices

| Object | Parsimonious candidate | Unapproved decision required |
| --- | --- | --- |
| Initial reference | `q0_ij=aL_ij*Lbar_i/20`, `Y=CES_sigma(q_ij/q0_ij)` | Freeze pre-treatment q0 throughout (recommended), including after upgrades |
| Task capacity (L3.capacity) | `0<=q_ijt<=h_ij` | Initialize h in task-output units; fixed vs upgradable |
| Capital (L3.investment) | `K_i,t+1=(1-delta)K_it+I_it` | delta, investment timing, resource financing and any investment limits |
| Adjustment (L3.adjustment) | `C_adj_it=G(x_it,x_i,t-1)` | Monetary cost versus hard feasibility constraint; first-round baseline x_i0 |
| Eligibility (L4.eligibility and adoption_cost) | `e_ij,t+1=max(e_ijt,uE_ijt)` | Eligibility scope, persistence, activation timing; only adoption_cost payment benefit (eligibility unlock) is approved |
| Efficiency (L4.efficiency and combined) | `aK_ij,t+1=H(aK_ijt,uG_ijt)` | Magnitude, repeatability, persistence, whether there is a resource payment |
| Paid adoption (L4.adoption_cost) | `C_adopt_it=F(eligible newly unlocked tasks)` | F, per-task vs bundle, payment event, single-charge ledger in combined |
| Owned-capital net cash flow | `CF_it=P_tY_it-w sum l_ijt-C_adj_it-C_adopt_it-pI I_it` | Adjustment/adoption cost forms, pI units, any additional real cash costs |
| Terminal stock and valuation | `K_i,201` and `V_T(K_i,201)` | Terminal value functional form, depreciation, discount weights, whether residual technology has separate value |
| Shutdown/reentry | `d_it=(l,k,I,u)=0` for a pure zero-cash-flow outside option | Whether no-production investment/adoption is also feasible as a distinct action; no-action outside option itself remains zero |
| Demand and learning | `P=max(0,a_c-b_c Q)`; D5/L6 approved concepts | Numerical a,b; rolling-OLS implementation; minimal learning parameter choices |

### Non-negotiable economic consistency checks

1. `V_T` must value **remaining** productive capital, not reimburse the full historical investment cost regardless of depreciation or usage. If purchased capital has a residual market price, terminal valuation and capital purchase price must use coherent units.
2. An investment at t cannot contribute to current-period production if it only enters K at t+1; terminal K_i,201 must include the final transition if final-round purchases are allowed.
3. Capital is owned: `pI I` is a cash expenditure, while `r sum k` remains an optional **separate imputed diagnostic**, never a second cash deduction for the same asset.
4. For L3.capacity, `h_ij` is an additional throughput constraint, not a productivity weighting or duplicate endowment cap. Do not infer an arbitrary h scale from the four diagnostic effort intensities.
5. L4.adoption_cost payment unlocks eligibility only; `combined` can also upgrade efficiency. Record each eligibility unlock once and explicitly define whether combined pays the same charge.
6. If `q0` is recalculated from upgraded technology, measured Y can lose comparability; choose the normalization rule before interpreting paired sigma results.
7. Distinguish a no-production, no-expenditure shutdown from no-production with positive investment/adoption spending. Do not assign both zero cash flow.
8. All candidate cost and technology laws must preserve nonnegative feasible resources and no hidden current-round or peer-level information.

### Next minimal research decision sequence

**First** decide a *terminal capital valuation rule* (e.g. residual capital at its purchase-price units, or an independently specified salvage-value function) and discounting convention **without setting numerical values**. **Second** approve transition timing, the frozen reference normalization, and adjustment form. **Third** approve the remaining capacity initialization, eligibility/efficiency scope and adoption payment event. **Finally** select any required numeric parameters and test feasibility, accounting, no-double-counting and 256-strategy distinctness. These are proposals, not approvals. Do not implement before the researcher's explicit equation-level authorization.

**Status:** Terminal-value inclusion APPROVED; valuation function, discounting, transition/cost equations and parameters OPEN. `research_validated: false`.


## A6 step 2H — Researcher approval: terminal owned capital at purchase price (2026-11-06)

**APPROVED:** Select terminal valuation option **A**: `V_T(K_i,201)=p_I*K_i,201`, where `p_I` is the capital purchase price in the same monetary units as investment expenditure. Do not introduce a separate salvage-price coefficient. The principal researcher has **not** approved a numeric `p_I`, depreciation `delta`, or discounting rule. No simulation code changes. `research_validated: false`.

**Interpretation and limitations:** This is a modeling assumption that remaining owned productive capital is worth its purchase-price units at the terminal date, not an empirical assertion about resale markets. Capital stocks and investment expenditure must have compatible units. If the same capital stock has depreciation, terminal value applies only to the surviving stock. If the initial K stock is common across strategies, a common initial-endowment value may be omitted for within-market ranking but must be acknowledged in cross-profile comparisons. Do not treat terminal valuation as a refund of every historical investment purchase.

### Discounting — next substantive choice (NOT YET APPROVED)

**Option A — No discounting (minimal experimental baseline):** `Score_i=sum_{t=1}^{200} CF_it + p_I*K_i,201`. This introduces no new time-preference parameter. It treats all rounds' monetary payoffs at the same weight, a deliberate assumption, not a general economic truth.

**Option B — Constant discount factor:** `Score_i=sum_{t=1}^{200} beta^(t-1)*CF_it + beta^200*p_I*K_i,201`, with `0<beta<=1`. This explicitly values future cash flows and terminal capital less when beta<1, but requires approval of beta and a sensitivity check. The timing convention is cash flow at end of each period t, terminal capital at the end of round 200; if beta is used, its exponents must be aligned consistently.

**Accounting warning:** The no-discounting formula is the special case beta=1 of the constant-discount specification. Either choice must remain compatible with a single owned-capital cash ledger: `CF=P*Y-w*sum l-C_adj-C_adopt-p_I I`, without charging imputed `r*sum k` a second time. The approved terminal valuation does not settle the capital stock law, financing limits, or whether terminal investment can be bought and immediately salvaged.

**Current decision ledger:** L3 capacity task-output bound APPROVED; L4 adoption_cost paid eligibility unlock APPROVED; owned-capital cash-flow convention APPROVED; ranking includes terminal stock APPROVED; terminal valuation at `p_I K_201` APPROVED. Discounting A/B, stock/cost/technology transition equations and numeric parameters remain OPEN. No code or CI change. `research_validated: false`.


## A6 step 2I — Approved no discounting; capital accumulation specification gate (2026-11-06)

**APPROVED BY PRINCIPAL RESEARCHER:** A6 ranking uses **no time discounting** (option A). Combined with the previously approved owned-capital convention and terminal valuation at the capital purchase price, the ranking objective is:

`Score_i = sum_{t=1}^{200} CF_it + p_I K_i,201`.

All 200 round cash flows have equal weights; no discount factor beta is introduced. This is an experimental assumption, not a claim that future cash is generally equivalent to current cash. `CF_it` is owned-capital cash flow, not legacy imputed-rental operating profit. Preserve all 256 strategy identities and approved L3/L4 semantics. **No numeric parameters, stock-transition assumptions or code changes were approved by this decision.** `research_validated: false`.

### Capital accumulation — minimum proposed law, not yet approved

Candidate common stock transition: `K_i,t+1=(1-delta)K_it+I_it`, where `K_i1=K_i0` is the shared initial owned-capital endowment per configuration, `I_it>=0`, `0<=delta<=1`. Production at t uses `K_it`; newly purchased `I_it` enters usable capacity no earlier than t+1. This timing is **PROPOSED**, not approved. The investment option activates I for L3.investment; whether I=0 for other L3 options is OPEN. Existing common labor cap `sum_j l_ijt<=Lbar_i` and capital cap `sum_j k_ijt<=K_it` continue; L3.capacity has additional approved task throughput cap `q_ijt<=h_ij`.

**Open economic decisions, to settle before code:**
1. **Depreciation:** set `delta=0` for a no-depreciation experimental baseline, or permit `delta>0` with a separately approved value and sensitivity. Do not choose a value here.
2. **Timing:** decide whether investment ordered in round t becomes usable at t+1 (recommended) or immediately at t; specify depreciation order so `K_i,201` is unambiguous.
3. **Investment feasibility/finance:** decide how I is funded or bounded (cash-on-hand/budget/borrowing/externally financed), and whether negative current cash flows are permissible. Without a budget/credit rule, I may be arbitrarily large; with terminal valuation `p_I K_201` and delta=0, an end-of-horizon purchase can cancel its own expenditure without production benefit. Avoid claiming unique investment optima from this identity alone.
4. **Capital unit price:** `p_I` is a shared monetary price per physical capital unit; its numeric value and whether it is identical across profiles/rounds are OPEN.
5. **Capital availability for other L3 strategies:** choose whether flexible/capacity/adjustment have fixed initial K while investment can expand K, and whether depreciation (if positive) applies to all firms.
6. **Terminal arbitrage/degeneracy:** Under delta=0 and `V_T=p_I K_201`, every extra unit purchased at t=200 costs pI and adds pI to terminal stock, yielding zero direct score contribution; earlier purchases may create productive returns. A finite feasible investment bound or a no-final-round-investment convention may be necessary for well-defined action selection. This is a mathematical warning, not approval of a restriction.
7. **Interaction with capacity:** If task-output cap h is fixed, additional K may be unproductive at binding task caps. This is acceptable as a model outcome, but no silent automatic h expansion is authorized.

### One parsimonious decision recommended next

**Capital depreciation convention** first: A = `delta=0` in the main 200-round experimental baseline (no depreciation state/parameter); B = `0<delta<=1` with value to be separately approved. Neither has been approved yet. Subsequent approval gates are timing, feasible investment bounds and terminal-period treatment, followed by cross-layer accounting tests. No code or CI changes; `research_validated: false`.

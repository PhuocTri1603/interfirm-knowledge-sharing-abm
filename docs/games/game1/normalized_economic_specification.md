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

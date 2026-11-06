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

# Game 2 — Observational Learning and Market Competition

> Canonical design document. Researcher-approved scope decision: **Option C (2026-10-31)** — Game 2A observational learning; Game 2B adds product-market competition. Status: ECONOMIC MECHANISM DESIGN, not implementation or validated results. Game 1 remains unchanged.

## 1. Research architecture

- **Game 1:** independent capital/labor search, maximizing output; accepted baseline.
- **Game 2A:** add public competitor observations and a decision rule using them, while preserving Game 1 production functions, fixed budgets, and output objective. No market prices or profit.
- **Game 2B:** introduce product-market demand, endogenous price, revenue, cost and profit. Compare informed and uninformed firms **within the same market model** to isolate the informational effect.
- **Game 3:** voluntary bilateral knowledge sharing, partner choice and sharing cost; excluded here.
- **AI shock/investment:** part of broader research vision, not automatically added to either Game 2 stage.

The prior experimental_design.md describes observational learning only and lists profit and competition as future extensions; this staged decision deliberately extends that earlier plan. Do not describe it as already implemented.

## 2. Inherited baseline (verified against Game 1 source)

Firm i has budget B=100, allocation share s_i in [0.05,0.95] for candidate search, K_i=B s_i, L_i=B(1-s_i), output q_i=F_{z_i}(K_i,L_i), and technology z_i among Cobb-Douglas, Leontief, Linear, CES. Initial s_i=0.50. A candidate is accepted only if it strictly improves current output. The accepted 100-firm multi-seed, 50/100/200-round matched-randomness protocol is the comparison reference. Game 1 code is not to be modified.

## 3. Game 2A: information economics

### 3.1 Information sets and timing

At the beginning of decision round t, firm i knows its own accepted state and private experiment history through t-1. Under treatment, it may also access **public records from t-1** for other firms. No firm may access another firm's failed candidates or t-round outcomes before all t-round decisions are fixed.

**Working specification, subject to researcher confirmation:** public fields are firm ID, production technology, realized output, and accepted capital share. Publishing the share is an explicit observability assumption, not something implied by public output alone. If share is private, a different inference model is necessary.

### 3.2 Comparator and behavioral rule

Proposed minimal mechanism:
1. From eligible firms with the **same production technology**, select the highest previous-round output; resolve ties deterministically by firm ID.
2. The firm may draw a candidate centered on that rival's last accepted capital share, with noise from the existing matched random schedule, clipped to feasible bounds.
3. Compare the candidate's output with its own status quo and accept only a strict improvement.
4. Each firm evaluates **exactly one** candidate per round in every arm.

Same-technology comparison is a design safeguard against blindly copying incompatible allocations. A cross-technology arm may later test transfer failure but is not required for the first pilot.

### 3.3 Arms and identification

- C0: Game 1 Guided (primary reference), no public information.
- C1: Game 1 Random (secondary benchmark).
- T1: Guided with competitor-informed candidate center in a prespecified fraction of rounds; otherwise original Guided candidate rule. The mixture probability must be set before simulation, with sensitivity analysis.
- Ablation T0: public records accessible but never used to generate candidates; expected to reproduce C0 under identical random draws.

**Estimand:** for seed r and horizon H, D_r(H) = mean_i[e_i,T1(H)] - mean_i[e_i,C0(H)], where e_i=q_i/q^*_{z_i}; report mean_r D_r(H) and paired 95% CI across independent seeds. Report technology-specific D_r,z(H). No pseudo-replication of firms within seeds.

**Confounding safeguards:** equal experiment counts, identical initial states, technology assignments, feasible domain and pre-generated random draws. All treatment branches consume indexed draws, not variable-length RNG streams. Do not claim that matched random numbers make every post-treatment trajectory identical.

### 3.4 Game 2A outcomes

Primary: efficiency difference at H=20,50,100,200. Secondary: first round reaching 99%/99.9% efficiency (right-censor if not reached), acceptance rate, distance from technology-specific constrained optimum, treatment uptake, same-technology match and observed-rival adoption. Pre-specify one primary horizon (suggest H=100) to limit multiple-testing claims.

### 3.5 Hypotheses (provisional)

H2A.1: public observation with an actionable allocation signal can improve learning efficiency under matched experimental opportunities.
H2A.2: effects differ across production technologies.
H2A.3: informational access need not improve outcomes when the signal is uninformative or imitation noise is large.

These are testable propositions, not simulation findings.

## 4. Game 2B: product-market economics

### 4.1 Minimal market closure — proposed, not yet approved

All firms produce a homogeneous good and sell into one market each round. Let aggregate quantity Q_t=sum_i q_it and inverse demand

P_t = max(0, a_t - b Q_t), with a_t>0, b>0.

Firm revenue R_it=P_t q_it. Let economic cost be C_it=c_K K_it+c_L L_it+f_i (and any explicitly approved experimentation/adjustment cost); profit is pi_it=R_it-C_it.

**Critical feasibility note:** in Game 1, B=100 is a fixed *input allocation budget*, not automatically an economic expenditure. Game 2B must decide whether K,L are quantities with per-unit prices c_K,c_L and whether B is a monetary spending constraint (c_K K+c_L L<=B) or a normalized resource constraint (K+L=B). Do not silently mix these interpretations.

**Critical strategic note:** with fixed K+L=B, identical unit costs and no option to reduce scale, a homogeneous-good market with nonnegative price can make profit maximization closely track output maximization, obscuring genuine strategic competition. Price feedback alone does not guarantee nontrivial firm tradeoffs. Before coding, specify at least one meaningful margin (e.g., adjustable production scale, unequal input prices, costly adjustment, or capacity choice), and check for pathological zero prices and demand calibration.

### 4.2 Decision and information timing

Proposed synchronous rounds:
1. Firms observe last-round market price and allowed competitor information.
2. Each chooses a feasible action using its policy and a **lagged expectation** of price or rivals' response; no current-round future price leakage.
3. Production quantities aggregate; market price clears through inverse demand.
4. Firms receive realized profit and update their learning histories.

A firm's action changes Q_t and therefore P_t. Whether firms act as price takers or internalize their own price impact is an explicit behavioral assumption to approve. If profit is the objective, acceptance must compare the *appropriate realized or expected profit measure*, not reuse Game 1's output acceptance mechanically.

### 4.3 Factorial identification (within Game 2B)

- M0: market competition, independent learning, no competitor observation.
- M1: same market, same decision opportunities, competitor observation enabled.
- Optional M2: market with different competitor-response expectations, tested only after M0/M1 work.

The difference M1-M0 estimates the effect of public competitor information **conditional on the market model**. Game 2B vs Game 2A is a change in environment and objective, not a clean causal estimate of observation alone. Both market arms must share initial conditions, demand shocks, cost parameters and random schedules.

### 4.4 Market outcomes and welfare

Firm profit, industry profit, quantity, price, concentration (HHI from output shares), entry/exit if later implemented, and consumer surplus under the linear-demand specification. For nonnegative interior P=a-bQ, CS=0.5*b*Q^2; if price is clipped at zero or demand has a cap, welfare formulas must reflect that boundary. No claim of welfare improvement is automatic from higher industry profits.

### 4.5 Hypotheses (provisional)

H2B.1: public rival information changes adaptation and profit outcomes in a market where decisions affect prices.
H2B.2: the value of rival information depends on technology and market conditions.
H2B.3: individual profit gains may diverge from consumer surplus and total welfare changes.

## 5. Design decisions remaining before implementation

1. **2A public visibility:** confirm accepted capital share is public (recommended for a minimal actionable signal) or private.
2. **2A attention:** same-technology best performer (recommended pilot) vs all-firm observation; number of rivals inspected.
3. **2A imitation probability:** fixed mixture rate and noise radius; prespecify sensitivity grid.
4. **2B resource accounting:** distinguish fixed resource quantities from monetary input costs and decide whether firms can vary total scale.
5. **2B demand calibration:** choose a,b or a demand-normalization rule ensuring informative positive-price regimes; decide whether a_t changes by round.
6. **2B market power:** price-taking vs strategic price anticipation, and how firms learn price impact.
7. **2B objective and learning:** expected vs realized profit for candidate selection; feedback and acceptance timing.
8. **2B observational signal:** what price, quantity, profit and allocation information is publicly available.

## 6. Validation gates

A. Researcher confirms behavioral assumptions for 2A; freeze a pre-analysis plan.
B. Implement Game 2A as separate modules, with deterministic tests for lagged observation, equal candidate opportunities, technology matching and matched randomization; do not modify accepted Game 1 code.
C. Run pilot then 100-seed experiments, independently recompute efficiency, CI and horizon consistency.
D. Approve Game 2B market closure and strategic margin; test market accounting, demand-price consistency, no future information and within-market M1-M0 contrasts.
E. Publish reproducible artifacts and limitations, then consider website visualization only if useful to the research.

## 7. Source provenance

- `docs/games/game1/research.md`: accepted independent-learning model and limits.
- `src/interfirm_abm/{simulation,firm,production,learning}.py`: actual Game 1 rules.
- `docs/proposals/experimental_design.md`: original three-game framework, before approved 2A/2B split.
- Option C approved by researcher on 2026-10-31.
- All 2A and 2B mechanisms beyond inherited Game 1 are **proposals**, not verified facts or executed experiments.


## 8. Researcher correction — heterogeneous 100-firm population (2026-10-31)

**Requirement:** 100 firms must not merely consist of 25 identical parameterizations per production family. Firms within each of four families must have distinct, randomly drawn technology coefficients, with controlled coverage of labor-intensive, intermediate, and capital-intensive types. This is a correction to the *research specification*, not a claim that the accepted Game 1 source code already satisfies it. Preserve the original Game 1 results as a historical homogeneous-within-family benchmark; do not silently overwrite its acceptance record.

### 8.1 Proposed reproducible stratified sampling

- Exactly 25 firms per family: Cobb-Douglas, Leontief, Linear, CES.
- Within each family: 8 labor-oriented, 9 intermediate, 8 capital-oriented.
- Draw independently within strata using a **uniform distribution conditional on stratum**, with a fixed population seed separate from experimental learning seeds:
  - labor-oriented: alpha_i ~ Uniform(0.10,0.40);
  - intermediate: alpha_i ~ Uniform(0.40,0.60);
  - capital-oriented: alpha_i ~ Uniform(0.60,0.90).
- Shuffle firm IDs reproducibly after drawing; store firm_id, technology, stratum, alpha_i, A_i, rho_i, population_seed in a canonical population artifact. Enforce alpha_i in (0,1), uniqueness of firm IDs, 25/technology and 8/9/8/technology. Randomly sampled coefficients need not be unique, although continuous draws will almost surely be distinct.
- This is a **balanced experimental design**, not an empirically estimated population distribution. Thresholds 0.40/0.60 and uniformity are researcher-adjustable assumptions, requiring sensitivity tests (e.g. alternative beta distributions and cutoffs).
- **Important:** alpha_i is the firm's *technological weighting coefficient*, not its chosen capital share s_it. For CES and Leontief, labeling alpha as an empirically observed capital expenditure share would be incorrect. “Capital/labor-oriented” is a within-model operational classification.

### 8.2 Firm-specific production functions

With A_i=1 for the first controlled heterogeneity experiment and fixed rho=-0.5 for CES:

- Cobb-Douglas: Y_i=A_i K_i^(alpha_i) L_i^(1-alpha_i).
- Linear: Y_i=A_i [alpha_i K_i+(1-alpha_i)L_i].
- Leontief: Y_i=A_i min(K_i/alpha_i, L_i/(1-alpha_i)).
- CES: Y_i=A_i [alpha_i K_i^(rho_i)+(1-alpha_i)L_i^(rho_i)]^(1/rho_i).

CES substitution elasticity sigma_i=1/(1-rho_i). Keeping rho fixed isolates heterogeneity in alpha; a separately controlled extension can draw rho_i from a prespecified distribution. **Do not vary alpha, rho, A, budgets, and behavioral rules all at once**, because that would obscure causal attribution. A_i heterogeneity (e.g., normalized lognormal) and resource-budget heterogeneity are later factorial robustness dimensions, not part of the first parameter-heterogeneity treatment.

For the proposed forms and equal normalized input prices, alpha_i > 0.5 corresponds to a capital-oriented technological optimum, alpha_i < 0.5 to a labor-oriented optimum; for the intermediate stratum both sides of 0.5 are included. Under linear production with alpha_i=0.5 all feasible allocations tie; tests must handle that case.

### 8.3 Comparability and normalization

At initial s_i=0.5, technology families may have different initial output levels; in particular the Leontief form can yield larger levels than the other functions under these parameters. Compare **within-firm output efficiency** Y_i/Y_i^* using each firm's own constrained optimum, not unnormalized cross-family output as evidence of superior learning. For Game 2A, a rival's raw output is not automatically comparable across alpha_i or families. Rank potential comparators by own-optimum-normalized efficiency only if that metric is explicitly public, or by observable output with a caveat about confounding; no omniscient access to private alpha_i.

### 8.4 Research design implications

- Rerun and audit a new heterogeneous-population Game 1 benchmark before Game 2A; the previously accepted 100-firm homogeneous-within-family experiment is not evidence for the new population.
- Compare Game 2A observational learning to a matched **heterogeneous** independent-learning control with identical sampled firms and random schedules.
- Prespecify technological distance d(i,j)=|alpha_i-alpha_j| for same-family comparisons; CES extension can add a separate distance in rho. Test same-family near vs far and cross-family transfer separately.
- Publicly observing a rival's alpha_i or own optimum is **not** automatically allowed. Public allocation and output are a defensible candidate signal but must be researcher-approved.
- In Game 2B, disentangle technology coefficients, factor prices, and observed input choices; alpha_i is not a firm's choice variable.

### 8.5 Literature grounding and limits

1. Arrow, Chenery, Minhas & Solow (1961), *Capital-Labor Substitution and Economic Efficiency*, Review of Economics and Statistics 43(3). Supports considering different input substitution structures, not the specific proposed 8/9/8 stratification or alpha ranges. https://faculty.econ.ucsb.edu/~tedb/Courses/GraduateTheoryUCSB/ACMS.pdf
2. Hopenhayn (1992), *Entry, Exit, and Firm Dynamics in Long Run Equilibrium*, Econometrica 60(5), 1127–1150. Supports firm heterogeneity as an economic modeling dimension, not a uniform distribution of input coefficients. https://ideas.repec.org/a/ecm/emetrp/v60y1992i5p1127-50.html
3. Axtell (2001), *Zipf Distribution of U.S. Firm Sizes*, Science 293(5536), 1818–1820, doi:10.1126/science.1062081. Empirical motivation for heterogeneous firm populations, but its firm-size distribution **does not identify a distribution for alpha_i**. https://pubmed.ncbi.nlm.nih.gov/11546870/
4. Kondo, Lewis & Stella (2018), *On the U.S. Firm and Establishment Size Distributions*, Federal Reserve FEDS 2018-075. Shows lognormal can fit firm-size and productivity distributions better than Pareto in their data; useful for a **separate future productivity A_i robustness exercise**, not direct evidence for uniform alpha_i. https://www.federalreserve.gov/econres/feds/on-the-us-firm-and-establishment-size-distributions.htm

**Approval boundary:** the researcher has approved random draws from a specified distribution and balanced capital/labor-oriented coverage. Numerical stratum cutoffs, distribution family, A_i=1 first-stage control, and CES rho treatment are explicit *proposals awaiting confirmation*, not already approved calibrations.

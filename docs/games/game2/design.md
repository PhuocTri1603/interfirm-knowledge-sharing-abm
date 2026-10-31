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

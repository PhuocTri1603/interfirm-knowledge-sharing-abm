# Game 1: scientific validation ledger

Status: **verification in progress; research_validated=false**. Technical completion of 100 × 256 × 200 is not proof of an economic mechanism. The diagnostic market is an illustrative scenario, not an approved PhD specification.

| Gate | Evidence | Current decision |
| --- | --- | --- |
| 1. Execution | GitHub Actions run 41971828596, 5,120,000 observations and artifact 13390269760 | Technical run passed; subsequent verification suite is separate |
| 2. Production | task feasibility tests and `task_ces_reference.py` tests for alpha=0.5, A fixed, sigma and Cobb–Douglas limit | **Not validated**: the actual diagnostic uses additive task activity; CES reference is not integrated; AI shock and substitution mapping not specified |
| 3. Market | quantity bounds, reserve-price checks, accounting identities in `task_mixed_market.py` | **Not validated**: illustrative inverse demand, rationing and cost assumptions; no equilibrium or calibrated demand |
| 4. Learning | policy-action tests for all compatible L3–L6 combinations, feedback and seeded reproducibility | **Not validated**: 16 adaptive × imitation identities use own-score optimization fallback, not imitation; no convergence evidence |
| 5. Robustness | reproducibility check for identical seed | **Not validated**: independent seeds, demand/technology perturbations, AI vs no-AI counterfactual and confidence intervals not yet executed |

## Approval-dependent economic decisions

1. **Production:** specify whether a CES K/L aggregator or a task-based assignment production function is the actual Game 1 mechanism. A CES benchmark alone is insufficient. Define sigma, the AI shock, and capital/labor feasibility, retaining A constant and alpha=0.5 where applicable.
2. **Market:** specify whether competition is Cournot, price competition or another explicit clearing institution, plus inverse demand, cost, and information assumptions. Current illustrative clearing computes price from total supply before reserve-price exclusion, so it is not asserted to be a competitive equilibrium.
3. **Information semantics:** adaptive means own-history only, while imitation requires peer actions/payoffs. Decide whether adaptive × imitation becomes a sequential observation regime or is excluded from scientifically comparable identities. Do not relabel own-score optimization as imitation.
4. **Sensitivity:** pre-register random seeds, parameter grids, convergence criterion, counterfactual definitions, summary estimands and uncertainty intervals before interpreting rankings.

## Release gate

`research_validated` must remain false until approved production/market specifications are implemented, all semantic conflicts resolved, and mechanism tests plus multi-seed/counterfactual/sensitivity reports are reproducible and reviewed. Passing CI is **necessary but not sufficient**. Do not silently flip the flag.

## 2026-11-05: Isolated CES AI-shock experiment added

- `src/interfirm_abm/task_ces_counterfactual.py`: paired no-AI / AI simulations with the same seeds, fixed A=1 and alpha=0.5; AI changes sigma only. Illustrative price-clearing and discrete K/L action plans are explicit.
- `tests/test_game1_ces_counterfactual.py`: pre-shock path equality, reproducibility, accounting bounds, sensitivity-grid completeness and refusal to call unsupported imitation.
- Robustness function defines a 5-seed × 3-post-shock-sigma grid. **The grid has not been executed in CI or independently reviewed at the time of this note.**
- This module is **not integrated** into the 256-player Game 1; its outcomes must not be described as validated Game 1 results.
- The 16 adaptive × imitation combinations remain **unresolved**. A non-imitation fallback is not a scientifically acceptable resolution.
- Remaining gates: economic specification approval, full-game integration, verified counterfactual execution, multi-seed summary and uncertainty reporting, semantic resolution, and model review.


## 2026-11-08 — Nine-strategy Game 1 full sample and robustness evidence (current engine)

**Scope clarification:** This is a new, separate *nine-strategy* executable experiment, not validation of the historical 256-strategy model described above. Engine: `src/interfirm_abm/game1_nine_strategy.py`; 3 L3 allocations × 3 L4 automation policies, 20 tasks, 200 rounds, controlled CES sigma values 0.5/1.0/2.0. Do not combine its results with 256-strategy reports. Model assumptions remain exploratory and uncalibrated; `research_validated=false`.

### Provenance and technical execution

- [Full sample run 42463803820](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/42463803820), head `c614b86d9192a57fb402b4772b3c3bb6bf80b79f`: **30/30 successful** simulation jobs and completed aggregate. Artifact `game1-full-sample-analysis` ID `13618500797`.
- [Previous full sample 42463760830](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/42463760830), head `47921bdc476ef15600203430f74ab9330cbcbd1f`: **30/30 successful**, artifact ID `13614944435`. This run precedes revised measurement of active AI usage.
- [Robustness run 42463803920](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/42463803920), same head as latest full sample: **20/20 successful jobs** (tests, 18 scenario partitions, aggregation), artifact `game1-robustness-analysis` ID `13617854610`.
- Artifact-level audit of latest full sample: **540,000** strategy-round records, 100 unique profiles, 60,000 distinct profile-sigma-round markets, exactly nine strategy observations each. No missing values, negative production or inconsistent market prices. Each market obeys `P=max(0,2-Q/9)` to floating-point precision (maximum absolute discrepancy < 7e-16). Cumulative profit differences match recorded per-round profits (maximum absolute discrepancy < 1.3e-13). Each strategy has 0–11 active AI tasks and the active count never exceeds the cumulative adoption count. Every profile-sigma market has exactly one recorded winner (winner definition breaks any ties by strategy ID).
- Additional dynamic-invariant audit of all 540,000 strategy-round records: adoption counts never decrease (0 violations); active AI count never exceeds ever-adopted count (0 violations); no-automation strategies never use or adopt AI (0 violations); shutdown never produces output or active AI usage (0 violations); every strategy-profile-sigma trajectory contains exactly 200 rounds (2,700 trajectories); the overall shutdown-action share is approximately 6.58%. These checks validate logged count/accounting semantics, not task-level feasibility or fee charging.
- **Audit boundary:** The round CSVs do not record input allocations, firm-level costs, each numerical optimizer's convergence/status, or task-level eligibility/adoption trajectories. Thus the checks above are accounting/market-output consistency, **not independent certification of input feasibility, optimality, adoption-cost accounting, or economic validity**.

### Descriptive full-sample findings (100 paired profiles per sigma; single main seed)

- Mean cumulative profit, Cost-Adjusted + Profit-Based: sigma=0.5 **149.141**, sigma=1 **151.840**, sigma=2 **119.040**; corresponding win counts **61/100**, **56/100**, **31/100**.
- At sigma=2, Productivity + Profit-Based has mean **120.907** and **29/100** wins; Uniform + Profit-Based has mean **117.635** and **24/100** wins. The strategy with the greatest win count is **not necessarily** the one with the greatest mean profit.
- Paired full-sample mean-profit differences (Cost-Adjusted+Profit-Based minus Productivity+Profit-Based): at sigma=0.5 **+58.659** (approximate 95% profile-level t interval **[42.932, 74.387]**); sigma=1 **+59.829** (**[42.859, 76.799]**); sigma=2 **−1.867** (**[−12.902, 9.168]**). These are descriptive uncertainty intervals over the 100 fixed synthetic profiles, not empirical-population or causal-confidence intervals.
- Mean *actual* active AI shares for Cost-Adjusted + Profit-Based in the latest full sample: **29.41%**, **28.60%**, **26.92%** for sigma 0.5, 1, 2, respectively. These counts use positive AI capital allocation (>1e-9), not selected AI modes. Previous artifact versions may differ.

### Predefined robustness subsample (ten fixed profiles × three paired seeds × three costs × three sigma)

- Robustness aggregation contains **2,430** distinct strategy-profile-seed-scenario-sigma results; the *independent technology clusters* in this sensitivity subset number **ten**, not 30 seeds×profiles or 2,430 player results.
- The Cost-Adjusted + Profit-Based strategy has the highest **mean** cumulative profit in all nine sigma×cost scenarios. Its win counts out of 30 paired profile-seed markets (baseline / capital-rental +50% / AI adoption fee ×3):
  - sigma=0.5: **22 / 16 / 23**;
  - sigma=1: **20 / 16 / 23**;
  - sigma=2: **14 / 14 / 15**.
- Paired robustness *profit gap* versus Productivity + Profit-Based under the **baseline** scenario, averaging three seeds within each profile and using a ten-profile t interval: sigma=0.5 **+69.27 [20.04, 118.50]**; sigma=1 **+71.52 [12.58, 130.46]**; sigma=2 **+7.12 [−6.56, 20.79]**. These intervals are exploratory, conditional on ten selected synthetic profiles, and should not be called definitive statistical significance.
- Cost-Adjusted + Profit-Based active AI share at baseline / higher rental / higher adoption fee: sigma=0.5 **31.59% / 27.92% / 31.05%**, sigma=1 **30.65% / 27.09% / 30.67%**, sigma=2 **30.43% / 26.59% / 29.35%** (rounded). Higher rental consistently lowers mean AI intensity, but causal mechanism and task-level decisions still need testing.
- **Counterintuitive result requiring mechanism audit:** Higher adoption fees raise Cost-Adjusted + Profit-Based *mean* profits in the sensitivity subset. Its paired 10-profile mean profit change and approximate 95% t intervals: sigma=0.5 **+2.357 [−4.838, 9.552]**; sigma=1 **+8.110 [−1.143, 17.363]**; sigma=2 **+18.514 [5.823, 31.206]**. Because every strategy competes simultaneously under the altered price-setting rule, general-equilibrium-style strategic/price effects may contribute, but no mechanism has yet been isolated; do **not** claim a higher adoption fee improves profitability in general.
- Seed effects remain material at sigma=2: baseline wins for Cost-Adjusted + Profit-Based are **1/10, 6/10, 7/10** for seeds 11/23/47. Do not treat ranking as seed-invariant.

### Outstanding scientific validation gates

1. **Production interpretation:** The CES output is a normalized index treated operationally as market supply. Confirm its economic interpretation, unit comparability and whether all 20 tasks can be bypassed when sigma>1. Sigma is **across task activities**, not identified K/L elasticity.
2. **AI treatment:** Eligibility is fixed and strategies choose among labor/eligible-capital task modes; this is **not yet a demonstrated exogenous AI shock**. Independently check first-use adoption charges, mode-selection versus positive-capital usage, and task-level responses to cost changes.
3. **Market mechanism:** The rule is a simultaneous quantity-dependent inverse-demand settlement, not a calibrated Cournot equilibrium or empirically identified demand schedule. Identify the contribution of market-price changes to fee/rental sensitivity before interpreting profits.
4. **Learning interpretation:** Per-strategy epsilon-greedy constant-step action values for five actions are closer to a non-contextual bandit than a fully specified Markov Q-learning agent. Check seed pairing, tie handling and learning traces.
5. **Numerical certification:** SLSQP multistart and COBYQA fallback with feasibility checks passed the current simulations, but per-call convergence messages, tolerance gaps and solver disagreement are **not recorded in the artifacts**. Numerical convergence/optimality is not proven merely by green CI.
6. **Inference:** Preserve paired technology-profile comparisons, clarify synthetic-profile uncertainty and strategy interdependence within markets, extend sensitivity beyond ten preselected profiles, and run genuine no-AI or fixed-market-price counterfactuals if the researcher approves them.

**Decision:** Technical execution PASS and current artifact consistency PASS; conditional robustness evidence AVAILABLE; scientific economic mechanism validation **NOT YET APPROVED**. Keep `research_validated: false`.


## 2026-11-08 — Targeted mechanism and solver audit added (results pending)

- Engine `run_game1(..., audit=True)` now optionally records per-strategy-round revenue, variable input cost, adjustment cost, first-adoption cost, labor/capital use, new adoption count and total market quantity. Default `audit=False` retains existing simulation outputs and economic decisions. Regression test compares audited versus ordinary paths and enforces the exact cost identity.
- `scripts/audit_game1_adoption_fee.py` runs matched baseline and triple-fee scenarios for the **same profile, sigma and seed**. It computes exact round-wise `Delta revenue = P_baseline * Delta own output + Q_baseline * Delta price + Delta price * Delta own output`, then `Delta profit = Delta revenue - Delta variable cost - Delta adjustment cost - Delta adoption cost`. This separates **accounting contributions** of market price, own quantity and direct cost. It does not identify causal mediation: competitors and learning can respond simultaneously. The resulting price term includes competitors' endogenous responses.
- `scripts/audit_game1_optimizer.py` wraps the actual scipy minimizer without changing its results and logs SLSQP/COBYQA status, iteration/function evaluation counts, primal constraint violations, objective recomputation errors and failure messages. It rejects successful solver reports with residuals >1e-6. This is **not** proof of global optimality, stationarity/KKT or solution uniqueness.
- Workflow `.github/workflows/game1-mechanism-audit.yml` runs nine matched fee comparisons (one profile × three sigma × three seeds) and three short solver diagnostics (one profile × three sigma × three rounds), after unit tests. This is an intentionally small **mechanism smoke test**, not 100-profile full validation. No outcome is claimed until Actions artifacts and logs are reviewed.
- Existing full-sample and robustness findings remain historical evidence for the prior code SHA; the new optional audit instrumentation should not be represented as a fresh validated full-sample result.
- **Next gates:** inspect actual fee-decomposition and solver artifacts, expand to representative profiles including known difficult sigma=2 cases, test optimizer multistart stability/first-order stationarity where mathematically appropriate, and obtain principal researcher review of economic interpretation. Keep `research_validated: false`.


## 2026-11-09 — F005 sigma=2 focused audit: VERIFIED (bounded scope)

**Audit status: VERIFIED for the scoped numerical/reproducibility and economic-direction checks.** This does **not** set `research_validated=true`; the broader nine-strategy model, the historical 256-strategy game, equilibrium interpretation, and global numerical optimality remain outside this audit.

### Historical Q-value recovery limitation

- Historical run [42576030370](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/42576030370), commit `8ea4fd63`, and solver run [42580951611](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/42580951611), commit `9e740959`, have **eight different decisions** for F005, sigma=2, seed=47, baseline fee, in rounds 95, 96, 98, 100, 101, 103, 104, 105, all in `L3=productivity|L4=cost_based`.
- The GitHub compare between those commits shows only new solver-audit script and workflow; no changes to economic engine or learning rules.
- The original historical round CSVs **did not record Q(b2), Q(b3), Q(b4), RNG state, or epsilon-exploration flags**. Their exact historical values cannot be reconstructed from those CSVs. Any Q-values from subsequent reruns belong to the rerun's numerical environment, **not** the original run. Therefore the specific cause of **each** of the eight historical decisions cannot be proven retrospectively.
- Controlled run [42583690003](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/42583690003) repeated 200 rounds, nine strategies, same seed 47 and single-thread numerical environment twice: **0/1800 action differences and 0/1800 record differences**.
- Q-value sensitivity run [42590979762](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/42590979762) compared BLAS 1 versus 4 threads with fixed code, seed and dependency versions: **five action differences** (rounds 97, 98, 100, 101, 103), **zero exploration-flag differences** across all 1800 records. At round 97, Q(b3)-Q(b4) changes sign from -0.0000215330 (one thread) to +0.0000286081 (four threads); both decisions were exploitation. This demonstrates a numerical-environment pathway to action divergence without changing epsilon-greedy. It does not retrospectively recover the eight historical Q paths.
- Solver focus run [42580951611](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/42580951611): 61,138 successful SLSQP calls, constraint residuals below 1e-6; no proof of KKT conditions or global optimality.

### Standardized-environment economic-direction check

- Source: pinned numerical-environment solver workflow [42585092976](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/42585092976), six artifacts, 200 rounds, F005, sigma=2, three paired seeds 11/23/47, baseline versus AI adoption fee x3, nine strategies. Pinned NumPy 2.4.6, SciPy 1.17.1, Pandas 2.3.3; BLAS/OMP/MKL threads = 1; `PYTHONHASHSEED=0`.
- Paired fee x3 minus baseline cumulative market output: seed 11 **-108.239483**, seed 23 **-119.151755**, seed 47 **-97.937743**; **negative in all three seeds**.
- Paired cumulative market price (sum of one market price per round): seed 11 **+12.026609**, seed 23 **+13.239084**, seed 47 **+10.881971**; **positive in all three seeds**.
- Paired total capital used across all strategies and rounds: seed 11 **-26375.793569**, seed 23 **-21090.883934**, seed 47 **-23099.252747**; **negative in all three seeds**.
- Paired active-AI task-round counts: seed 11 **-1539**, seed 23 **-572**, seed 47 **-499**; **negative in all three seeds**.
- Paired summed strategy profits across all rounds: seed 11 **+127.292021**, seed 23 **+142.354368**, seed 47 **+144.069541**; **positive in all three seeds**. This is a model-specific aggregate across nine interacting strategies, not evidence that every strategy profits, nor that higher AI fees improve real-world profits.
- The sign of the supply/price response matches the earlier unpinned F005 sigma=2 investigation (old cumulative market-output changes approximately -108.259/-119.117/-97.916 for seeds 11/23/47). Exact magnitudes differ slightly. **The economic direction, not bitwise identity across historical environments, is robust** for this particular F005/sigma=2/three-seed comparison.
- The price increase follows the **stipulated inverse-demand accounting identity** `P=max(0,2-Q/9)` when total market supply falls; it is **not** an independently established equilibrium or identified causal mediation mechanism.
- The paired results hold fee, technology profile, sigma and seed constant across scenarios, but endogenous competitor responses and learning are not isolated. The numerical tests do not establish universal sign stability for other profiles or sigma values.

**Decision:** Close the **focused F005 audit** as **VERIFIED WITH DOCUMENTED HISTORICAL Q LIMITATION**: controlled reproducibility passes, numerical sensitivity is demonstrated, and the specified sigma=2 economic-direction results are stable under the standardized environment. Do **not** assert the exact historical eight Q-paths were recovered, or that F005 certifies global optimality. The overarching `research_validated=false` remains unchanged until the scientific release gates above are satisfied.


## 2026-11-09 — Researcher-approved interpretation lock for current nine-strategy Game 1

**Approval scope:** Preserve the existing formulas, parameters, numerical implementation and nine-strategy engine unchanged. These are **interpretation decisions only**, not new model assumptions, code changes, or scientific validation of the full model.

1. **Output (Y):** The 20-task CES output is a normalized production index. For the simulated market only, treat its numerical value as a **conventional unit of market supply**. This is a modeling convention, not an empirically calibrated physical quantity.
2. **Action budget fraction (b):** The action fraction represents **resource-capacity utilization / mobilization**, not capital investment or intertemporal capital accumulation. Labor and capital have separate capacity ceilings; there is no capital stock transition equation.
3. **AI:** The current model represents AI through **capital-based task automation**, replacing labor with capital on eligible tasks under pure-mode allocation. AI is **not** a separate production input in this engine.
4. **CES sigma:** Sigma is the **elasticity of substitution among normalized task activities**, not a directly identified capital–labor substitution elasticity. Differences across sigma scenarios must not be described as AI shocks.

**Interpretation boundary still open:** For sigma=2, some task activities can be zero while the CES index remains positive. The economic meaning of omitting tasks (substitutable activities versus essential sequential production stages) requires researcher review before the production specification is fully locked. Also pending: market-equilibrium terminology, broader counterfactuals, and remaining scientific validation gates.

**State:** Four interpretation conventions APPROVED; production specification review IN PROGRESS; `research_validated=false`. No source code changed.


## 2026-11-09 — Researcher approval: interpretation of the 20 CES tasks

The principal researcher explicitly confirms that the **20 tasks represent mutually substitutable production activities**, **not** 20 mandatory sequential production stages. Thus, under the existing normalized CES aggregator, positive output with some zero-activity tasks at sigma=2 is an intended economically interpretable outcome, **not by itself a production-model inconsistency**. At sigma<=1, the existing CES formula still requires all task activities to be positive for positive output; this is a mathematical implication of the chosen elasticity, not a claim that tasks are technologically mandatory stages.

This decision **closes the open task-semantics interpretation question** from the previous entry. No formula, sigma value, allocation constraint, engine code, or simulation result is changed. Remaining model-level scientific validation (including empirical calibration, numerical optimality, counterfactual identification and market interpretation) is separate. **Game 1 step 1 — economic specification interpretation: COMPLETE, subject to no new assumptions.** `research_validated=false`.


## 2026-11-09 — Step 2 focused task-level / solver CI run #42634459614

**Evidence:** https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/42634459614 ; head commit `ae4d168a9dae08f5acee54fee9f6636edef1d2f1`, branch `game1-economic-policy-interface`, run conclusion `success`, 4/4 matrix jobs successful.

**Scope:** Profiles 0 and 4 × sigma 0.5 and 2.0 × seed 11 × 20 rounds for task-level audit; 3 rounds per matrix cell for solver instrumentation. Each job ran the nine-strategy unit test suite: 21 tests passed per job. Four matrices yield 720 settled player-rounds. Observational candidate interception reports 10,000 task-level rows across 500 production candidate calls (134, 134, 115, 117 for [profile0 sigma0.5, profile0 sigma2, profile4 sigma0.5, profile4 sigma2], respectively); these are production **candidate evaluations**, not necessarily all realized market allocations, and do not include shutdown as task-level rows. Distinguish from the 720 settled player-rounds.

**Observed PASS (scoped):** firm-level pure-mode checks; labor and capital usage <= their respective mobilized capacities; ineligible tasks never use capital; no-automation policy never uses capital; calculated CES output matches technology output index; newly charged AI adoption tasks match capital use above 1e-9 absent earlier adoption; `cost = wL + rK + adjustment + adoption_fee × newly adopted tasks`; candidate predicted profit identity; reference normalization; 146/146 SLSQP instrumentation calls reported successful with constraint residual and objective recomputation <=1e-6, no solver failures or COBYQA fallback. Solver calls by matrix [32,32,36,46]. All 4 artifact ZIPs uploaded.

**Important limitations:** Successful SLSQP and primal residual checks do **not** establish KKT sufficient conditions or global optimality; local-search `profit_based` is not certified globally optimal. The task-level logger intercepts proposed `candidate()` plans and does not label whether that plan is the finally selected market action except through separate round-level outputs. This run does **not** implement a matched AI/no-AI intervention that holds market mechanisms appropriately fixed, nor a causal AI effect estimate. It also does not span all 100 configurations, sigma=1, 200 rounds or multiple seeds. Retain `research_validated=false`.

**Step 2 decision:** Scoping production feasibility / CES / AI eligibility / adoption fee accounting PASS for tested matrices; global optimality and controlled AI effect remain OPEN. No engine, strategy, production equation or economic assumption modified.


## 2026-11-09 — Step 2 paired AI/no-AI CI run #42635875911

**Evidence:** https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/42635875911 ; commit `a61156ca8956495e36dda45d47a6eb194c6a9c98` ; conclusion SUCCESS, 4/4 matrix jobs successful and four artifact ZIPs uploaded.

**Design:** On each of two approved firm profiles F001 (index 0), F005 (index 4), each sigma 0.5 and 2, seed 11, 20 rounds, nine-player market: compare original AI-allowed simulation to separate no-AI market where all nine player slots remain and an observational wrapper routes the six AI-enabled slots to `no_automation` candidate policies. Core engine, economic parameters, RNG seeding and learning rules unchanged. Endogenous market price, action learning and rival responses can differ between the two markets. The paired output checks no AI capital, active AI or adoption fee in control and verifies round-level profit accounting identity. Additional fixed-price candidate comparisons hold initial plan, prior adoption, budget and price=1 constant; do not claim globally optimal effects.

**Run-log results** (all numbers AI-allowed minus no-AI; 9-player market, summed over 20 rounds; `delta_price_sum` = sum of 20 per-round market settlement price differences, not a percentage or equilibrium price):
| Profile | sigma | AI-active task-round count in AI-allowed market | delta total market-firm output | delta cumulative market-firm profit | delta price sum |
|---|---:|---:|---:|---:|---:|
| F001 | 0.5 | 184 | +27.714973597816364 | +12.571428559619934 | -3.079441510868486 |
| F001 | 2.0 | 536 | +89.80095620762022 | +13.073006187561218 | -9.977884023068913 |
| F005 | 0.5 | 75 | +1.99873299594909 | -6.523556151334075 | -0.22208144399434437 |
| F005 | 2.0 | 172 | +21.355609269611225 | -7.7934624271437345 | -2.372845474401247 |

**Scoped PASS:** Four paired experiments completed; no-AI control uses zero capital / active AI / AI adoption cost; pairwise round-level cost/profit decomposition identity; fixed-price candidate comparisons executed. **Economics:** Allowing AI raised total output and lowered aggregate round-settlement prices in all 4 tested combinations, but improved aggregate accumulated firm profit only for F001 and reduced it for F005. This is a model-specific, 20-round market-policy counterfactual, not a universally generalizable or direct causal individual-firm AI effect.

**Still OPEN:** economic decomposition of why F005 aggregate profits fall (revenue vs factor costs, adjustment costs, adoption fees); scope across 100 profiles, sigma=1, 200 rounds and multiple seeds; certification of global optimality is not established. Do not claim overall Game 1 scientific validity. **Step 2: focused execution/feasibility and paired-policy checks PASS; broader economic validation pending.** Keep `research_validated=false`.


## 2026-11-09 — Independent arithmetic decomposition of original paired AI/no-AI artifacts

**Provenance:** Four original ZIP artifacts from AI/no-AI GitHub Actions run #42635875911 (artifact ids 13683720500, 13682424918, 13682940858, 13682477915); each ZIP includes `round_panel_profile_*_sigma_*_seed_11.csv`, 360 rows (2 scenarios × 20 rounds × 9 strategies). Independent reaggregation of original panel data verified exact revenue identity `delta(PQ)=P_noAI*deltaQ + Q_noAI*deltaP + deltaP*deltaQ` and profit identity `delta_profit=delta_revenue-delta_variable_cost-delta_adjustment_cost-delta_adoption_cost` within 1e-7 on all 720 paired player-rounds. This is an independently executed calculation from historical data, **not an assertion that the new decomposition CI workflow succeeded**.

| Profile | sigma | Quantity contribution | Price contribution | Cross contribution | Delta revenue | Delta variable cost | Delta adjustment cost | Delta AI adoption fee | Delta profit | Delta labor | Delta capital |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| F001 | 0.5 | 40.942993 | -14.486954 | -5.697953 | 20.758085 | 8.049120 | 0.107536 | 0.030000 | 12.571429 | 0.000000 | 829.059402 |
| F001 | 2.0 | 134.607509 | -44.994404 | -50.183704 | 39.429401 | 25.905491 | 0.365904 | 0.085000 | 13.073006 | 0.000000 | 2668.265544 |
| F005 | 0.5 | 3.256775 | -0.740691 | -0.268216 | 2.247868 | 8.075257 | 0.676167 | 0.020000 | -6.523556 | -229.294800 | 1061.046321 |
| F005 | 2.0 | 32.185844 | -10.525374 | -2.898244 | 18.762226 | 25.823184 | 0.700004 | 0.032500 | -7.793462 | -125.566200 | 2785.354171 |

**Interpretation:** In F005 revenue rose in both sigma conditions, but additional variable input costs exceeded the revenue gain; adjustment costs were secondary and the directly charged AI adoption fee was small. The negative price contribution and price×quantity interaction partially offset the positive output contribution. In F001 net revenue gains exceeded added input, adjustment and AI adoption costs, resulting in higher profit. All numbers are simulation index units summed over 20 rounds/9 strategies, not calibrated money units. This decomposition is an exact accounting partition under the specific baseline-price convention, not causal price mediation. Do not change economic model or mark `research_validated=true`.


## 2026-11-09 — Original-data decomposition workflow CI confirmation (run #42637493190)

**CI source:** https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/42637493190 ; workflow `Game 1 existing-data AI profit decomposition`, head `046c9aa2d986a232a3caf195e01195a739f3b204`, conclusion SUCCESS (1/1 job). Original artifacts from paired AI/no-AI run #42635875911 downloaded; `scripts/decompose_game1_ai_existing.py` executed and reported `PASS: 4 original paired panels; 720 paired player-round records; exact revenue and profit identities`.

**Output:** artifact `game1-ai-existing-profit-decomposition` (id 13684455993; https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/42637493190/artifacts/13684455993), containing `decomposition_summary.csv` and `decomposition_by_player_round.csv`. Logged numbers agree with the independently reconstructed decomposition recorded above at numerical precision. One nonfatal GitHub Actions Node.js 20 deprecation warning occurred; no economic or test errors.

**Status:** Focused step-2 accounting cross-check PASS in the four representative comparisons; general validation across full configurations and seeds, solver global optimality, and wider research validation are NOT established. Preserve `research_validated=false`. No core engine, strategy, or economic assumptions changed.


## 2026-11-10 — Ten-profile / three-seed AI/no-AI robustness (run #42823775419)

**Source:** https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/42823775419 ; successful workflow on branch `game1-economic-policy-interface`, head SHA `67d605de6888bde2191db08ee19524b1348ffcaf`. Original aggregate artifact `game1-ai-robustness-aggregate` (ID 13768221872), files `all_90_cases.csv` (90 rows), `consistency_by_profile_sigma.csv` (30 rows), inspected directly. CI shows completion success and 91 artifacts (90 individual and one aggregate). First page of jobs shows 30/30 successes; total workflow SUCCESS, aggregate present. This records verified data, not inferred job-level details beyond available pages.

**Design:** Ten fixed profile indices [0,9,19,29,39,49,59,69,79,99], sigmas [0.5,1.0,2.0], seeds [11,23,47], 20 rounds, nine player strategies, market-level policy counterfactual with learning/prices endogenous. 90 comparisons, 180 scenario-markets, 32,400 player-round records in the underlying runs. Original engine not modified.

**Results:**
- Delta aggregate firm profit (AI-allowed minus AI-disabled): 56/90 strictly positive, 33/90 strictly negative, 1/90 near-zero (absolute tolerance 1e-8), mean +2.3468102127786605, sample SD 9.602739246501544, min -14.762143841504033, max +37.68349502637953. Do not treat these dependent heterogeneous simulation cases as 90 independent real-world observations.
- Delta total output positive in 89/90, zero in 1/90, never negative; total of settlement-market-price differences negative in 89/90, zero in 1/90, never positive. Price response is mechanically tied to demand `P=max(0,2-Q/9)`; do not describe it as an independent empirical verification.
- Sigma=0.5: positive/negative/zero 15/14/1, mean delta profit -0.1945, mean delta output +10.3189, mean sum of per-round market price differences -1.1465.
- Sigma=1: positive/negative/zero 20/10/0, mean delta profit +2.2018, mean delta output +15.2059, mean sum of per-round market price differences -1.6895.
- Sigma=2: positive/negative/zero 21/9/0, mean delta profit +5.0331, mean delta output +30.5706, mean sum of per-round market price differences -3.3967.
- Per-profile sign counts (over 9 sigma-seed cases each): F001 +9/-0/0; F010 +1/-8/0; F020 +7/-2/0; F030 +0/-9/0; F040 +2/-7/0; F050 +9/-0/0; F060 +4/-5/0; F070 +8/-0/1; F080 +9/-0/0; F100 +7/-2/0.
- Across 30 profile-sigma groups (3 seeds each): 14 all positive, 7 all negative, 9 mixed or with neutral; sign consistency is substantial within some technologies, not uniform globally.
- Independently validated both summary-level accounting equations to numerical precision from all_90_cases.csv: max absolute profit identity residual <8e-14 and revenue price-quantity decomposition residual <6e-14.

**Scientific conclusion (scoped):** AI allowed raises output and reduces endogenous market prices almost uniformly in this ten-profile sample; total accumulated market-firm profit is heterogeneous, sometimes positive and sometimes negative, depends on profile/sigma/learning-seed realizations. Descriptive sigma gradient is not a controlled causal estimate of elasticity effect: sampled technologies, algorithm dynamics and market effects may interact. This is a 20-round robustness panel over 10 selected profiles, NOT the full 100-profile/200-round design and NOT sufficient for universal empirical or inferential claims.

**Status:** Robustness audit PASS for execution/completeness/identities and quantitative descriptive assessment. Broader Game 1 validation pending (100 profiles, 200 rounds, more seeds/controlled interpretation, global numerical optimality unresolved). No engine/strategy/assumption changes. Keep `research_validated=false`.


## 2026-11-11 — Full 100-profile × 200-round AI/no-AI horizon robustness, GitHub run #42826231816

**Provenance:** GitHub Actions https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/42826231816 ; workflow `Game 1 AI no-AI full 100 profiles 200 rounds`, completed successfully, head SHA `ea548083bb38f339b8eed56ba89df7b29b5f2903`; aggregate artifact `game1-full-ai-robustness-aggregate` ID `13801381254` at https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/42826231816/artifacts/13801381254 . All three original CSV files inspected: `all_1800_horizon_cases.csv` (1,800 rows, 14 columns), `paired_20_vs_200.csv` (900 rows, 12 columns), `consistency_by_horizon_sigma.csv` (6 rows, 8 columns). Job-list and artifact endpoints are paginated; CI run-level conclusion SUCCESS and aggregate artifact verified. Independent reconstruction of accounting identities from aggregate: max absolute residual for profit 1.03e-11 and price-quantity revenue 9.21e-12.

**Design:** 100 approved profiles × sigma in {0.5,1,2} × seed in {11,23,47} = 900 paired policy contrasts, each with nine players and 200 rounds, for AI-allowed and AI-disabled markets. 20-round outcomes are exact prefixes of the 200-round trajectories. Full simulation comprises 1,800 scenario markets × 200 rounds × nine players = 3,240,000 player-rounds. No core engine, strategy or economic assumptions were changed. These are policy-environment contrasts with dynamic endogenous prices and learning.

**Aggregate result** (AI allowed minus AI disabled; firm-profit totals summed over nine players):
- 20-round horizon: profit 567 positive, 328 negative, 5 approximately zero (tolerance 1e-8); mean cumulative delta +2.675598, mean per-round +0.133780; mean delta revenue +17.792086, variable input cost +14.768425, adjustment +0.313846, AI fee +0.034217. Output positive in 893, negative in 2, near-zero in 5.
- 200-round horizon: profit 261 positive, 639 negative, 0 zero; mean cumulative delta -62.653554, mean per-round -0.313268; mean delta revenue +147.094663, variable input cost +206.418298, adjustment +3.291169, AI fee +0.038750. Output positive in 881, negative in 19, zero in 0.
- Sign stability 20→200: 582/900 same sign, 318/900 different sign; 312 positive→negative, 1 negative→positive, 5 near-zero→positive. Counts among 3 sigma strata: stable 231/300 at sigma .5, 196/300 at sigma 1, 155/300 at sigma 2. 844/900 observations had lower average incremental profit per round at 200-round horizon than at 20-round horizon.
- Accounting decomposition means at 200 rounds: quantity contribution +427.628450, price contribution -180.974478, price×quantity interaction -99.559308; net revenue +147.094663, less variable cost +206.418298, adjustment +3.291169, AI fee +0.038750, yields cumulative profit -62.653554.
- Sigma stratum, 20 rounds: sigma .5 positive/negative/zero=151/146/3, mean profit -0.703547; sigma 1=197/101/2, mean +2.656041; sigma 2=219/81/0, mean +6.074299.
- Sigma stratum, 200 rounds: sigma .5 positive/negative/zero=88/212/0, mean -50.524273; sigma 1=99/201/0, mean -37.498806; sigma 2=74/226/0, mean -99.937584.

**Interpretation:** Relative market-level profit gain from enabling AI is frequently positive at 20 rounds and frequently negative at 200 rounds, though not universally. In long trajectories, relative revenue is still higher but additional variable-input expenditures exceed the revenue increase on average. This is not solely an AI adoption fee effect, which is minimal in the accounting ledger. The 200-round experiment captures learning, endogenous market-price feedback, strategy choices, and adoption histories together; a 20→200 shift alone **does not identify a causal learning mechanism**. Same early trajectory is reused (not independent short-horizon reruns). Sigma strata are descriptive, not estimates of isolated task-substitutability effects. Output is the normalized CES task index used as quantity by convention. Report accumulated and per-round contrasts to avoid confusing horizon scaling with worsening economics.

**Scope / status:** Full-design 100-profile × 200-round horizon comparison PASS for execution, completeness, arithmetic identities, and descriptive result extraction. Important scientific validation remains pending for interpretation of mechanisms, solver global optimality and further sensitivity; do not set `research_validated=true`. No engine changes.


## 2026-11-12 — Round-level mechanism run #43036152839: partial / CI artifact failures

**Run:** https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/43036152839 , commit `98ac7f48771c04cffe8f3558e91569fbf9a24582`, workflow `Game 1 AI no-AI round-level mechanism audit`. Initial attempt concluded FAILURE; 95 configuration artifacts were available, aggregate missing. GitHub jobs API showed 95 successful profile jobs and five failures at profiles 76,77,78,86,87 (100 job page; final aggregate job pending/skipped due to needs). Logs for 77,78,86,87 indicate their Python computation completed and `actions/upload-artifact@v4` failed after five retries with `Unexpected token '<', "<!DOCTYPE "... is not valid JSON`, a GitHub artifact service/response error, not an established engine or economics failure. Profile 76 logs were unavailable (404 BlobNotFound); underlying cause unverified.

**Remediation:** Invoked GitHub connector `rerun_failed_workflow_run_jobs` for run #43036152839; GitHub returned success=true. The rerun of failed jobs is requested but **completion and aggregate results are not yet verified** at the time of this note. Do not claim scientific results or mark step passed until full aggregate `game1-ai-round-mechanisms-aggregate` is present and 180,000 round-paired observations checked. Keep engine untouched and `research_validated=false`.


## 2026-11-12 — Round-level K / price / revenue mechanism analysis (run #43036152839, attempt 2)

**Provenance:** https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/43036152839 ; retry completed successfully (attempt 2), aggregate artifact `game1-ai-round-mechanisms-aggregate` ID `13912731662`, files `by_round.csv` (200 round means), `by_period.csv` (three non-overlapping period means), `by_sigma_period.csv` (nine sigma-period means). Five formerly missing profile artifacts [76,77,78,86,87] are now present; total artifact count 100 (99 per-profile visible on paginated endpoint plus aggregate). Job computes 100 × 3 sigma × 3 seeds × 200 rounds = **180,000 matched market-round observations**, each market containing nine player strategies. No changes to engine, demand, policy, payoffs or learning parameters. Accounting identities verify to numerical precision in the aggregate (max profit residual among displayed periods <1.3e-14). Source script `scripts/audit_game1_ai_round_mechanisms.py` observes original engine `run_game1(..., audit=True)`.

**Definitions:** `delta` means AI-allowed scenario minus AI-disabled scenario, averaged across 900 matched markets *per round*. A market's K and L are totals over nine players, price is one shared market-clearing price, quantity is nine-player output total. AI-disabled control has capital use 0 **by construction**. Wage and rental are both `0.5/51.5≈0.0097087`; measured extra variable input cost = wage × delta L + rental × delta K. Output is normalized CES index treated as quantity by explicit modeling convention.

| Component, mean per matched market-round | rounds 1–20 | rounds 21–100 | rounds 101–200 |
|---|---:|---:|---:|
| delta profit | +0.133795 | -0.285828 | -0.424167 |
| delta revenue | +0.889603 | +0.783328 | +0.666460 |
| delta variable input cost | +0.738405 | +1.052752 | +1.073936 |
| delta capital used | +76.54268 | +111.10215 | +116.51954 |
| delta labor used | -0.48695 | -2.66875 | -5.90408 |
| rental × delta capital | +0.743133 | +1.078662 | +1.131258 |
| wage × delta labor | -0.004728 | -0.025910 | -0.057321 |
| delta adjustment cost | +0.01569 | +0.01636 | +0.01668 |
| delta AI adoption fee | +0.00171 | +0.00005 | +0.00001 |
| delta market quantity | +1.08169 | +1.54598 | +1.58935 |
| delta market price | -0.12019 | -0.17178 | -0.17659 |
| positive quantity revenue effect P0×ΔQ | +1.67304 | +2.18886 | +2.18985 |
| negative price revenue effect Q0×ΔP | -0.49034 | -0.90310 | -0.98885 |
| negative interaction ΔP×ΔQ | -0.29309 | -0.50243 | -0.53454 |

**Mechanism decomposition (early→late, round-mean changes):** Additional capital rises +39.977 units per market-round, rental expense +0.3881; labor savings grow -5.417 in labor and -0.0526 in wage expense, net additional input expense +0.3355. The adverse revenue components price+interaction deepen from -0.7834 to -1.5234, offset in part by increased quantity component +0.5168 (1.6730→2.1899). Net revenue increment falls ~0.2231, and delta profit falls 0.5580 per market-round (+0.1338→-0.4242). This is an **exact accounting decomposition**, not identified causal mediation: K selection, P and Q evolve jointly under fixed demand, stochastic learning and policy changes. Market price differences are mechanically induced by quantity differences via the approved inverse demand rule. Mean per-round delta profit was negative in 186 of 200 rounds and first negative at round 15 (aggregated mean; not individual profile claims).

**Sigma stratification, per-round delta profit:**
- sigma 0.5: first 20 -0.03518, rounds 21–100 -0.24590, last 100 -0.30149.
- sigma 1: +0.13280, -0.16614, -0.26861.
- sigma 2: +0.30376, -0.44544, -0.70246.

**Cross-run reproducibility caution:** Summing the new per-round mean delta profit yields +2.675894709 (first 20) and -62.607002632 (first 200), versus +2.675597757 and -62.653554024 in the earlier independent full-horizon run #42826231816. Difference in 200-round average = +0.046551392 (about 0.074% of the magnitude of the earlier mean). Although economically small and qualitatively consistent, the numerical difference must **not** be described as exact reproducibility. Investigate at profile/sigma/seed level and pin solver environment before scientific signoff; do not silently reconcile or overwrite originals.

**Scientific status:** CI and round-level accounting/completeness PASS; economic diagnostic: rising capital input costs and stronger negative endogenous price feedback jointly account for lower relative market profit, while positive volume effects partly offset them. No isolated causal identification of learning, capital policy or price. Reproducibility discrepancy unresolved. Leave `research_validated=false`; do not change core engine based on diagnostic alone.


## 2026-11-12 — Cross-run reproducibility and fixed-price accounting audit initiated

**Motivation:** Previous 100-profile × 200-round run #42826231816 and observational round-level run #43036152839 differ slightly in mean cumulative delta profit (−62.653554 vs −62.607003). This discrepancy remains unresolved until profile/sigma/seed reconciliation; do not treat approximate aggregate agreement as exact numerical reproducibility.

**Implementation (unchanged engine):** `scripts/audit_game1_ai_reconcile_fixed_price.py`, `.github/workflows/game1-ai-reconcile-fixed-price.yml`. CI fetches original saved per-profile CSV artifacts from both completed runs, with no simulation rerun and no changes to economics, prices, strategies or learning. It verifies all 900 profile × sigma × seed keys at horizons 20 and 200 (1,800 comparisons) and all 180,000 market-round keys. Outputs signed/absolute/relative discrepancies and sign changes, per-case and per-period ex-post fixed-price decomposition, and original market price feedback. Download calls have retries; CI aggregate and results not yet verified.

**Exact accounting definition:** For each market round, with the two original scenarios' realized quantities and costs unchanged, set reference price `P_ref=P_noAI`. Then `delta_pi_fixed=P_noAI*(Q_AI-Q_noAI) - (C_AI-C_noAI)`; `price_feedback=(P_AI-P_noAI)*Q_AI`; `delta_pi_actual=delta_pi_fixed+price_feedback`. The latter feedback equals original `price_effect+interaction_effect` in the revenue decomposition. This is **ex-post repricing of observed choices**, not a new market equilibrium, no reoptimization and no causal identification. Results will distinguish whether higher input costs already dominate at common prices or endogenous price feedback flips profit sign.

**Status:** Workflow added, not yet confirmed successful. Keep `research_validated=false`.


## 2026-11-12 — Completed reproducibility and ex-post fixed-price decomposition (run #43175642079)

**Provenance:** Workflow run https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/43175642079 completed SUCCESS on commit `c8289a6cfcb08161ce87fb5f34a857f620b12790`, job `analyze` PASS. Artifact `game1-ai-reproducibility-fixed-price` id `13923813178`, four original files (`reproducibility_1800_cases.csv`, `fixed_price_180000_market_rounds.csv`, `fixed_price_900_pairs_200round.csv`, `fixed_price_by_period.csv`). Dataset counts independently checked: 1,800 profile–sigma–seed–horizon matches; 180,000 paired market-rounds; 900 paired 200-round totals. Old benchmark = run #42826231816; new round series = run #43036152839. All accounting identities from the new audit passed; largest deviation from `actual=fixed+feedback` in 900 case totals ~2.5e-12. No simulations rerun; original scenario outcomes revalued ex post.

**Reproducibility (round-derived minus prior full-horizon outputs):**
- Horizon 20 (900 pairs): mean signed profit difference +0.000296952; mean absolute difference 0.0003992235; median absolute 5.88e-12; maximum absolute 0.11774293 at profile index 0, sigma 2, seed 11; 0 sign changes (tolerance 1e-8); 40 cases exceed absolute error .001, five exceed .01.
- Horizon 200 (900 pairs): mean signed difference +0.046551392; mean absolute 0.053663174; median absolute 3.56e-9; maximum absolute 31.772482 at profile index 26, sigma 2, seed 47, prior −325.304701/new −293.532219; next profile 31 sigma 2 seed 11 difference +7.723391, profile 34 sigma 1 seed 11 difference +2.386116. 0 sign changes; 250 cases exceed .001, 78 exceed .01, 16 exceed .1, three exceed 1. The top three positive outliers sum +41.881989 vs total signed error +41.896253 across 900 cells, indicating aggregate discrepancy is highly concentrated and largely offset by smaller positive/negative errors. **Numerical reproducibility FAIL/UNRESOLVED at strict precision**, even though qualitative profit sign is completely stable. Investigate particular profiles and optimizer numerical stability, solver versions and deterministic execution; no root cause asserted.

**Exact ex-post fixed-price accounting:** Set `P_ref=P_noAI` for realized production plans of each scenario; `Δπ_fixed=P_noAI*(Q_AI−Q_noAI)−ΔC_total` and `price_feedback=(P_AI−P_noAI)*Q_AI`, so `Δπ_actual=Δπ_fixed+price_feedback`. The difference `price_feedback=price_effect+interaction_effect` includes the cross-term. Counterfactual repricing is NOT an intervened fixed-price game and firms would generally choose differently if actual prices were held fixed.

**After 200 rounds, 900 paired markets (cumulative nine-player profits):**
- mean realized Δπ = −62.607003, mean fixed-price Δπ = +217.842966, mean price feedback = −280.449968; accounting residual <2.6e-12.
- actual Δπ negative 639/900, positive 261/900; fixed-price Δπ positive 779/900, negative 121/900; price feedback negative 882/900, positive 18/900.
- **518/900 fixed-positive cases become actual-negative under observed endogenous price**; all 121 fixed-negative cases remain actual-negative; no case had fixed-negative but actual-positive.
- sigma .5 actual/fixed/feedback means (−50.524004,+48.230887,−98.754891), fixed-to-actual positive→negative 130/300.
- sigma 1 means (−37.490455,+147.331094,−184.821549), positive→negative 169/300.
- sigma 2 means (−99.806549,+457.966916,−557.773465), positive→negative 219/300.

**Per market-round period means** (unweighted mean across 900 matched markets per round):
| period | actual Δπ | fixed-price Δπ | price feedback | Δ variable costs | Δ K | Δ P |
|---|---:|---:|---:|---:|---:|---:|
| 1–20 | +0.133795 | +0.917232 | −0.783437 | +0.738405 | +76.542684 | −0.120188 |
| 21–100 | −0.285828 | +1.119699 | −1.405527 | +1.052752 | +111.102153 | −0.171775 |
| 101–200 | −0.424167 | +1.099224 | −1.523390 | +1.073936 | +116.519542 | −0.176595 |
Across all 200 rounds the mean fixed-price Δπ is positive in every round, while mean price feedback is negative in every round. A market's price change is mechanically linked to its quantity change through the approved inverse demand curve, and both scenarios' selected actions, cumulative adoptions and RL evolve jointly. **Interpretation:** enabling AI raises quantity and variable input expense; at baseline no-AI prices, resulting volume gains typically outweigh cost changes, but endogenous price feedback is often sufficiently negative to reverse relative profit gains. This is a stronger descriptive mechanism diagnosis, not an independent causal price effect or a generic welfare conclusion. Reconciliation discrepancies remain unresolved; thus full scientific validation remains pending, `research_validated=false`.

**No core economic-engine changes.** No additional scientific claims or parameter decisions approved by this bookkeeping audit.


## 2026-11-12 — Targeted solver stability diagnosis launched (profiles 26/31/34)

Three largest 200-round numerical reproducibility discrepancies (new round-level run minus original full-horizon run) are profile index 26 / sigma 2 / seed 47 (+31.772482), index 31 / sigma 2 / seed 11 (+7.723391), and index 34 / sigma 1 / seed 11 (+2.386116). These are discrepancies **between two numerical runs**, not policy effects. They do not change the sign of the AI/no-AI cumulative profit contrast. Numerical cause not established.

Read existing `src/interfirm_abm/game1_nine_strategy.py`: `allocate()` uses SLSQP with deterministic multiple starts, `ftol=1e-8`, `maxiter=700`, with COBYQA fallback only when no feasible SLSQP result; validates budget feasibility and firm allocation but does not prove global optimality. The cost-adjusted objective includes absolute adjustment costs, a potential source of nonsmoothness; numerical sensitivity is a **hypothesis**, not a confirmed diagnosis.

Added observational diagnostic `scripts/audit_game1_solver_outliers.py` and workflow `.github/workflows/game1-solver-outliers.yml`. For each of the three cases, reruns both market policy scenarios twice within the same process (200 rounds each), wrapping `game.minimize` only to log method, status, objective, iterations, function evaluations and fallback frequency, then restoring it. Records first differing player-round between two identical reruns (if any) and cumulative profit by horizon. No modification to solver inputs, returned results, game decisions, economics or RNG. This diagnoses within-process determinism and visible solver failures, but **cannot by itself prove** cross-run numerical reproducibility or identify which optimizer invocation causes divergence without a more granular per-round trace. CI not yet verified. Keep `research_validated=false`.


## 2026-11-12 — Solver outlier CI complete: reproducible within environment; cross-run differences still unexplained

**Run:** https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/43178089634, SUCCESS, jobs diagnose(26), diagnose(31), diagnose(34) SUCCESS. Directly inspected original solver diagnostic artifacts `game1-solver-outlier-26` (ID 13926270180), `game1-solver-outlier-31` (13925828109), and `game1-solver-outlier-34` (13925866902), each containing `solver_calls_N.csv`, `summary_N.csv`, `within_process_differences_N.csv`.

**Same-process deterministic reruns (two exact repeats; 200 rounds; paired AI/no-AI):** For each profile 26 (sigma 2, seed 47), 31 (sigma 2, seed 11), 34 (sigma 1, seed 11), zero differing player-rounds across the two repeats in both scenarios; cumulative delta profits reproduce within each profile:
- 26: horizon 20 +7.564290, horizon 200 −293.532219; AI calls 11,908 and no-AI calls 3,318 **per repeat**, all SLSQP success status 0; COBYQA calls 0.
- 31: horizon 20 −2.217439, horizon 200 −364.108783; AI calls 13,350 and no-AI calls 3,380 per repeat, all SLSQP success status 0; COBYQA calls 0.
- 34: horizon 20 +1.126110, horizon 200 −88.060542; AI calls 13,636 and no-AI calls 3,380 per repeat; of AI SLSQP attempts, 13,539 success status 0 and 97 failure status 4 (`Inequality constraints incompatible`) **per repeat**, zero failed no-AI attempts, COBYQA calls 0. Each optimizer failure was apparently recovered by another feasible restart, consistent with `allocate` strategy (not a game-level failure).

**Interpretation:** within-one-environment deterministic repeatability PASS. Individual SLSQP starts are not uniformly successful for profile 34; fallback absence is expected because a feasible SLSQP result exists. Across-workflow numerical reproducibility remains NOT VERIFIED/FAIL at strict tolerance; the large 26 error is not accompanied by SLSQP failures here. No solver instability root cause established. To isolate cross-run divergence, compare identical profile/round/strategy output and optimizer invocation traces on pinned environment/commit versions; check whether first divergent allocation or an input/environment discrepancy, and only then consider modifying solver options. **No core economic engine change approved or performed; `research_validated=false`.**


## 2026-11-12 — Section 3.2 historical-commit instrumented reproduction gate launched

**Source:** Historical nine-policy full sample run #42463803820 at commit `c614b86d9192a57fb402b4772b3c3bb6bf80b79f`, 100 profiles × sigma {0.5,1,2} × 9 policies × 200 rounds, seed 11. Section 3.2 archived descriptive baseline run #43193319354.

**Code:** `scripts/reproduce_paper_section3_2.py`, `.github/workflows/paper-section3-2-reproduction.yml`; workflow run https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/43194569720. Original commit checked out into separate worktree; historical source imported without edits. Each sigma/batch job first runs the original engine **without instrumentation**, compares every round-level output, price, profit, cumulative profit, action, AI use and adoption against the archived CSV, and checks first-place rankings. Absolute tolerance 1e-7, relative tolerance 1e-9; report exact max residuals and first mismatches. On failure the job stops before mechanism collection, uploads gate diagnostics, and must not be called reproduced.

**Observational mechanism collection (conditional on gate PASS):** A separate original-engine replay wraps only the returned `candidate()` result to record chosen task plan, original pre-choice plan and new adoption. No optimizer, market, cost, CES, RNG or RL modifications. It independently calculates task activities and normalized activities, K/L allocations, mode switches, actual AI use, output, revenue, variable cost, adjustment cost, adoption cost, total cost and resource use; checks budget feasibility, CES output and profit/cost identities. The instrumented replay must match the uninstrumented replay within the same tolerances. Exports 18,000 firm-round and 360,000 task-round observations per 10-profile job **only if both gates pass**. Artifacts preserve environment package freeze. Original CI installed `.[dev]` without pinning all transitive dependency versions; cross-environment reproducibility is a separate open question.

**Status:** Full 30-job gate initiated; no pass/fail result claimed yet, no scientific mechanism conclusion approved, no figures replaced, no manuscript changes. `research_validated=false`.


## 2026-11-12 — Section 3.2 reproduction run #43194569720: strict baseline mismatch in multiple batches

**Run:** https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/43194569720. At inspection, 3/30 jobs SUCCESS, 10/30 FAILED and 17 unfinished (10 in progress, seven queued). These are provisional counts, not a full-run final outcome. All ten completed failures occurred at **Gate first; only then record mechanisms** with `REPRODUCTION_GATE_FAILED`, exit code 2; original source import/setup completed. Failures are real differences against archived run #42463803820 at prespecified `atol=1e-7, rtol=1e-9`, not a software crash or proof that the underlying economic model is erroneous. Do not relax the threshold post hoc to label them PASS.

**Direct job-log evidence:**
- sigma 0.5 batch 01 (F011–F020): max output abs error 0.0006607514 (1,306 rows outside tolerance), market price error 0.0000734149 (7,731 rows), cumulative-profit error 0.0011725686 (16,791 rows), terminal profit error 0.0009574388; zero action, AI/adoption-count and winner mismatches. First output mismatch F011, cost_adjusted/profit_based, round 8.
- sigma 1.0 batch 02 (F021–F030): max output abs error 0.0038251527, market price error 0.0004250170, cumulative-profit error 0.0024452931, terminal error 0.0021061771; zero action, AI/adoption-count and winner mismatches. First output mismatch F022, cost_adjusted/cost_based, round 5.
- sigma 0.5 batch 06: max output abs error 0.0018778888, cumulative-profit 0.0020949841, terminal 0.0020027800; zero action/winner mismatches.
- sigma 1.0 batch 08: max cumulative-profit absolute error 0.0041599678, terminal error 0.0038212583; zero action/winner mismatches.

**Reproduced successfully:** sigma 0.5 batches 00, 05 and 08 passed both strict baseline and independent instrumented-vs-uninstrumented gates; successful jobs logged `REPRODUCTION_AND_INSTRUMENTATION_PASS`. This is partial coverage only and must not be generalized to 100 profiles, three sigma or all environments.

**Environment and scientific interpretation:** Inspected CI logs resolve NumPy 2.4.6 and SciPy 1.17.1 on Python 3.11; original workflow installed `.[dev]` without a transitive dependency lock, so original 2026-11-08 environment remains unknown. Early deviations can appear in `cost_adjusted` allocations, consistent with—but not proving—numerical solver sensitivity. In recorded failed jobs action and winner identity remain stable; that does not imply strict numerical reproducibility. `research_validated=false`.

**Next gate:** Preserve all original diagnostic artifacts; do not use the failed cases as validated task-level mechanisms, alter model/solver tolerances, rerun the full 30-job matrix or publish Section 3.2 task-based plots while unresolved. First record complete run results and compare environment against recoverable historical logs; use a small targeted representative diagnostic comparing first divergent optimizer call before any broader rerun.


## 2026-11-12 — Original/replay dependency versions matched; targeted first-divergence trace

Historical run #42463803820 job 128678585255 (sigma .5 batch 1) and job 128678585404 (sigma 1 batch 2) show **the same resolved package versions** as failed reproduction run #43194569720 job 131102089020: Python 3.11, NumPy 2.4.6, SciPy 1.17.1, pandas 2.3.3, matplotlib 3.11.2. Therefore **a different NumPy/SciPy package version is not a supported explanation** for these failures. Remaining possible numerical differences include platform/BLAS/runtime, solver sensitivity or unobserved inputs; none is proven.

First observable failed-case output mismatch: F011, sigma .5, `cost_adjusted + profit_based`, round 8, archived output 0.922386678228658 versus reproduced 0.9223870620939845 (difference ~3.84e-7). First observable output mismatch for F022, sigma 1.0, `cost_adjusted + cost_based`, round 5, difference ~1.05e-7. Original archived CSV contains **no optimizer invocation logs**, so an exact historical SLSQP call cannot be reconstructed or certified as first diverging. Identifying the first observable round and tracing all original-engine candidate/optimizer calls contributing to it is the scientifically justified next step.

Added observational-only `scripts/trace_paper_section3_2_first_divergence.py` and targeted one-profile CI `.github/workflows/paper-section3-2-solver-trace.yml`, run https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/43207912859. It records per-call SLSQP method, status, objective, iteration/function evaluation counts, vector norm/hash and maps candidate calls to their actual market round, with first-divergent-round exports. It uses the unchanged historical game engine, no new solver settings, no increased reproduction tolerances and no economic mechanism conclusions. Pending CI outcome; `research_validated=false`.


## 2026-11-12 — Targeted F011 trace run #43207912859 completed: original-replay discrepancy not reproduced

**Verified CI:** https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/43207912859 SUCCESS; artifact `section32-first-divergence-F011` ID `13940801384` downloaded and inspected (candidate_trace.csv, optimizer_trace.csv, first_profile_round_differences.csv, targeted_diagnostic.json, environment.txt). Historical source commit `c614b86d9192a57fb402b4772b3c3bb6bf80b79f`, profile F011, sigma 0.5, seed 11, prespecified `atol=1e-7, rtol=1e-9`.

**Result:** `first_divergent_round=null`, empty first-profile difference CSV. All 200 rounds / nine policies reproduce archived values within the strict gate on this separate trace run. Crucially the focal F011 round 8 `cost_adjusted + profit_based` output is **0.922386678228658**, exactly equal to archived output, contrasting with failed run #43194569720 where it was 0.9223870620939845 (+3.838653265e-7). This is evidence of **cross-execution variability of computed allocations/results even at the same source and package versions**, not evidence that tracing causes or cures it.

**Solver trace details:** 9,154 SLSQP invocations recorded (all returned success status 0, no COBYQA); 1,697 non-shutdown candidate decisions. At round 8 the focal `cost_adjusted + profit_based` candidate comprises **20 SLSQP invocations, indices 229–248**, with all calls reported successful and selected output matching archived baseline; these indices belong to the *successful trace execution*, not the failed 2026-11-12 reproduction job. Original run #42463803820 did not save optimizer traces, so the exact first differing invocation in the failed job **remains unidentified**. The trace script's `first_divergent_round=null` should not be interpreted as solver-level reproducibility proof across jobs.

**Environment:** Both downloaded artifact `environment.txt` files, failed batch #43194569720 (artifact 13934237200) and successful trace #43207912859 (artifact 13940801384), are byte-for-byte identical. Python 3.11.18 / NumPy 2.4.6 / SciPy 1.17.1 / pandas 2.3.3; same package versions as sampled original 2026-11-08 job logs. Unobserved floating-point or runtime differences, SLSQP sensitivity and numerical bifurcations remain hypotheses, not established causes. Do not change optimizer tolerances, claim all 100 profiles reproduce, or interpret unvalidated task-level mechanism results. `research_validated=false`.

**Next diagnostic if required:** A single failed-profile process-independent comparison with full optimizer traces for **both** strict-pass and strict-fail executions, including candidate input hashes, optimizer initial points, constraints/modes and returned plans, is necessary before identifying the first *differing solver call*. Avoid full 30-job rerun until this has been localized.


## 2026-11-12 — Section 3.2 finalization gate: independent-process solver traces

User requires Section 3.2 completed before paper-agent handoff. The existing strict reproduction run #43194569720 ended with 3 success, 10 failure and 17 cancelled jobs, so full-sample gate remains **NOT PASSED**. No task-level mechanism figures or manuscript changes are authorized by these results.

A focused 3-independent-process F011 diagnostic is implemented in `scripts/compare_paper_section3_2_solver_traces.py`, `scripts/trace_paper_section3_2_first_divergence.py` (now records optimizer initial-point hashes) and `.github/workflows/paper-section3-2-independent-traces.yml`, run https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/43219989053. Each job imports unchanged historical source and records SLSQP call initial/output hashes, statuses, round/candidate mapping, and environment; compare job identifies earliest differing call and whether inputs already differed. A three-run pass would establish only targeted F011 reproducibility, **not** the 100-profile gate. If the three executions coincide, do not invent a root cause or silently declare complete; further controlled tests would be required.

Pending CI; no change to production/optimization/learning/market/seed, no tolerance increase, `research_validated=false`.


## 2026-11-12 — Three independent F011 traces consistently diverge from archived baseline

Workflow #43219989053 (https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/43219989053) completed **SUCCESS** for all four jobs (trace x3 and compare). The green workflow status is **not** the strict archive-reproduction gate. Each independent execution produced exactly 9,154 SLSQP calls and detected the same **first archived mismatch: F011, sigma=0.5, round 8, L3=cost_adjusted|L4=profit_based**; archived output 0.922386678228658, reproduced output 0.9223870620939845, abs delta 3.8386532641432325e-7. The three observed solver traces compared identically on captured call input/output hashes, status, method, iteration and evaluation counts. `environment.txt` matched between the three runs. The compare job reported `first_pairwise_solver_differences=[]`, `first_archived_divergent_rounds=[8,8,8]`, `environments_identical=true`, and `reproducibility_gate=NOT_ESTABLISHED`.

Interpretation: repeatability *within these three replays* is shown, but agreement with the original archive is not. The earlier targeted trace run #43207912859 (same nominal source and NumPy/SciPy versions) matched the archive; the new reproducible disagreement is consistent with a cross-run numerical discrepancy not explained by package versions alone. Historical per-solver traces do not exist, so **no first differing historical SLSQP invocation can yet be claimed**. Scope of future work: isolate archived vs replay optimizer behavior using controlled tests and numerical environment fingerprints before relaxing tolerances or interpreting independently instrumented mechanisms. Preserve `research_validated=false`; Section 3.2 cannot be handed over as validated mechanism analysis.


## 2026-11-12 — BLAS threading sensitivity, run #43225602926

Controlled numerical-runtime probe: https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/43225602926, source commit `9f3f496ee26862d335b9fab8488b7b047a2886f8`. Both CI jobs completed successfully; artifacts `section32-blas-threads-1` (13947314243) and `section32-blas-threads-2` (13947334185).

The probe held historical source commit `c614b86d9192a57fb402b4772b3c3bb6bf80b79f`, F011, sigma=0.5, seed=11, Python 3.11.18, NumPy 2.4.6, SciPy 1.17.1 constant, while setting `OPENBLAS_NUM_THREADS`, `OMP_NUM_THREADS`, `MKL_NUM_THREADS` together to 1 or 2. First archived discrepancy in both executions occurred at round 8, L3=cost_adjusted|L4=profit_based.

- Archived q: **0.922386678228658**.
- 1-thread q: **0.9223872969192003**, absolute discrepancy **6.186905422422839e-7**.
- 2-thread q: **0.9223870620939845**, absolute discrepancy **3.8386532641432325e-7**.
- One- versus two-thread outputs differ by **2.348252158e-7**.

Interpretation: the experiment demonstrates sensitivity of this replay to numerical threading configuration. Since the probe simultaneously changed three thread-related environment variables, it does **not** isolate a specific BLAS library or prove a unique root cause of archived differences. The successful CI job statuses indicate the trace scripts ran successfully, not that the strict reproduction gate passed. Preserve strict tolerances, historical data, `research_validated=false`, and the mechanism-evidence embargo for Section 3.2 (task-level allocations, K/L, AI, cost decomposition, Figures 3.4–3.6).


## 2026-11-12 — Full-sample controlled reproduction and economic stability gate launched

Following the approved four-step Section 3.2 completion plan, added `scripts/analyze_paper_section3_2_numerical_stability.py` and `.github/workflows/paper-section3-2-controlled-full-sample.yml`. The new CI matrix runs 30 independent historical-engine batches (100 profiles × 3 sigmas × 9 strategies × 200 rounds = **540,000** round observations) under explicitly fixed `OPENBLAS_NUM_THREADS=2`, `OMP_NUM_THREADS=2`, `MKL_NUM_THREADS=2`, original engine commit `c614b86d9192a57fb402b4772b3c3bb6bf80b79f`, seed 11, unchanged strict tolerance (absolute 1e-7, relative 1e-9).

Every batch saves baseline gate JSON and uninstrumented reproduced rounds even on failure. **Only if its archive reproduction gate passes**, that batch may record independent task/firm-level mechanisms and must also pass the instrumentation gate. The always-run aggregation job compares terminal profits, market winners and paired policy profitability signs and mean differences against the archived baseline across the full 540,000 rows, explicitly reporting whether economic conclusions survive numerical differences. The aggregation report must never substitute economic stability for strict numerical reproducibility; it retains `research_validated=false` and does not automatically validate Section 3.2.

Pending: inspect full-sample CI artifacts and reconcile any failed batches. Then audit independently recorded task allocation, K/L, AI adoption, cost identities and price/market accounting; Figures 3.4–3.6 must not be promoted from placeholders until these checks pass. No change to production technology, optimization tolerances or historical experiment.

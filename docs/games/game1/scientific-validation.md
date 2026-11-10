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

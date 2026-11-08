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

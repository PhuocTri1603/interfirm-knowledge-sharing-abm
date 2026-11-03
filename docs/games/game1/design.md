# Game 1 — Economic Foundations and Reconstruction Plan

**Status:** Theoretical reconstruction; economic assumptions pending researcher approval.  
**Authority:** [Theoretical Charter](../theoretical_charter.md)  
**Scope:** Game 1 only. Preserve existing algorithmic validation as historical technical work.

## Approved production-framework decision — 2026-11-03

The researcher has explicitly approved switching the production foundation for the 100-firm research program from a direct two-input aggregate CES specification to a **task-based production framework**, informed by Acemoglu and Restrepo's theory of automation.

- **Game 1:** Firms produce by performing tasks. Capital and labor can perform tasks subject to technological feasibility; AI-related change may alter which tasks can be automated. Input allocation, production, costs, and profits must follow economically motivated choices.
- **Game 2:** Competition, observation, and learning take place in the same task-based production environment.
- **Game 3:** Investigate voluntary interfirm sharing of technological knowledge, including potential knowledge about task performance or automation; do not assume sharing occurs or succeeds.
- **CES is not prohibited:** CES aggregation across tasks remains an admissible representation, but is distinct from treating aggregate K and L as the only two direct inputs.
- **Prior discussion:** A common A and fixed alpha = 0.5 were agreed for the earlier two-input CES formulation. Their meaning and applicability in a task-based model require explicit reconsideration; do not silently carry them over as task-level parameters.
- **Not yet specified or approved:** number and distribution of tasks, task-level technologies, eligibility and costs of automation, task aggregation functional form and elasticity, AI adoption/investment costs, firm heterogeneity, decision timing, market structure, and learning/sharing rules.
- **Implementation status:** This records an approved theoretical direction, not an implemented or validated task-based simulation. Preserve the legacy code and data as historical baselines until a separately approved implementation design is ready.

## Implementation checkpoint — approved population and task feasibility (2026-11-03)

- The principal researcher approved the synthetic population of 100 heterogeneous firms and 20 shared tasks per firm. Canonical review data: `data/firms/task_based_100_firms_profiles.csv`, `data/firms/task_based_100_firms_tasks.csv`, and their README.
- The initial implementation in `src/interfirm_abm/task_based_firm.py` loads the approved population and checks per-task automation eligibility, nonnegative allocations, and aggregate K/L endowment limits. Tests are in `tests/test_task_based_firm.py`.
- **Important limitation:** The within-task linear activity calculation is a provisional bookkeeping convention for feasibility testing only. It is **not** a researcher-approved production function; no aggregation from task activities to final output has been approved. Do not use this calculation to report production, profit, welfare, AI effects, or equilibrium.
- **Not yet implemented:** firm decision/optimization policy, output aggregator, input prices, market demand, AI shock, adoption costs, profit and welfare accounting for the task-based environment. The legacy `economic_firm.py` remains separate.
- This implementation does not change the theoretical charter or preassign cooperation, winners, or profit.

## Economic accounting interface checkpoint — 2026-11-03

- Added `src/interfirm_abm/task_economics.py` with an **aggregator-neutral interface** to evaluate a given feasible task allocation. The caller must supply the task aggregator and all prices; no economic functional form is chosen implicitly.
- Accounting separates output, revenue, capital and labor costs, fixed costs, optional adoption costs, and profit. This is an accounting identity for an externally supplied plan, **not** a firm optimization rule or market equilibrium.
- Added `tests/test_task_economics.py` covering identities, negative-price rejection, invalid aggregator output, and automation feasibility. The simple sum in one test is strictly a stub, **not an approved production aggregator**.
- Still awaiting researcher approval before scientific simulations: task aggregation and parameters; ownership and opportunity cost of K/L; output pricing/demand; timing; AI technology shock and investment/adoption; decision policy.
- Code has been committed, but passing CI has not yet been confirmed.

## Task aggregator candidates — mathematical implementation, not model selection (2026-11-03)

Added `src/interfirm_abm/task_aggregators.py` and `tests/test_task_aggregators.py` to make alternative task aggregation representations explicit and testable. **None is selected as the official Game 1 production function.**

- Weighted linear: `Y = sum_j omega_j q_j`. Allows compensation between task outputs.
- Weighted Leontief (separate normalized bottleneck example): `Y = min_j(q_j / omega_j)`. This normalization is distinct from the CES power-mean limit.
- Weighted CES: `Y = (sum_j omega_j q_j^rho)^(1/rho)`, `rho=(sigma-1)/sigma`, `sigma>0`; at `sigma=1` use weighted geometric mean. Positive weights sum to one. The `sigma -> 0+` limit is `min_j q_j` under this particular CES normalization.
- `sigma` governs substitution **between task outputs**. It must not be described as an identified capital–labor substitution elasticity. The within-task capital/labor mechanism is a separate theoretical layer.
- The current within-task additive activity formula is still a provisional accounting convention, not an approved technology. These aggregator tests verify mathematical identities only, not empirical realism or scientific validity.
- **Pending principal researcher approval**: which task aggregator (if any), task weights, elasticity, meaning of zero task output, and within-task production representation. Do not run economic experiments as if these choices were settled.

## Within-task execution cost quotes — technical checkpoint (2026-11-03)

- `src/interfirm_abm/task_execution.py` supplies pure-labor and pure-capital **cost quotes** for a given target task activity. The latter is prohibited if the firm's existing task eligibility mask is false.
- With productivity `a_L, a_K`, unit input prices `w,r`, and target activity `q`, hypothetical quotes are `L=q/a_L`, cost `wL`; or `K=q/a_K`, cost `rK` if eligible. The returned labor-minus-capital cost difference is **not** an automation/adoption decision.
- These are illustrative within-mode linear accounting equations, not an approved full task production function. They do not check aggregate endowment feasibility, market pricing, capital ownership/opportunity costs, adoption or adjustment costs, or investment constraints.
- `tests/test_task_execution.py` checks the arithmetic, zero activity, invalid inputs and ineligible capital mode. CI status has not yet been confirmed.
- The next economic research design question is how feasible task activities, fixed automation costs, input constraints, and task aggregation jointly determine optimal choices. No policy or result is inferred yet.

## Joint task-bundle feasibility checkpoint — 2026-11-03

- `src/interfirm_abm/task_bundle.py` evaluates an explicitly supplied **20-task pure-mode execution proposal** for a single approved firm. It calls existing labor/capital task quotes and checks that total required K and L do not exceed the firm's respective endowments.
- Reports aggregate input use, variable-cost quotes, resource violations, and per-task quotes; converts feasible bundles to `TaskAllocation` for reconciliation with the existing technical activity interface.
- `tests/test_task_bundle.py` checks zero allocations, shared resource shortages, ineligible automation, malformed bundles, and reconciliation of feasible task activity. Code is committed; CI has not been confirmed.
- **Not an optimizer:** The module neither chooses the 20 task modes nor selects activity targets. It does not use the provisional cash field, impose adoption costs, determine output prices, or claim equilibrium.
- **Scientific limitation:** The pure-mode linear task activity convention is still provisional; no production aggregator, behavioral rule, or AI-induced feasibility transition is approved. No economic findings should be reported from this infrastructure.

## Finite candidate profit comparison — implementation checkpoint (2026-11-03)

- Added `src/interfirm_abm/task_plan_selection.py` and `tests/test_task_plan_selection.py`. The module ranks **externally supplied** 20-task plans by accounting profit, using the existing shared K/L feasibility checker and an **externally supplied** task aggregator and prices.
- Each candidate explicitly specifies task modes, target activities, and optional fixed/adoption costs. Resource-infeasible candidates are excluded. If all candidates are infeasible, no winner is returned. Profit ties preserve input order.
- **Scope:** The best candidate is optimal **only among the supplied feasible candidates**, not globally profit maximizing. No algorithm creates candidate plans, selects technology adoption, predicts market prices, or models dynamic adjustment.
- The test suite uses an additive task aggregator strictly as a **test stub**, not a researcher-approved production function. No results from these synthetic test cases constitute economic findings.
- Further economic decisions still require approval: within-task technology, task aggregation, wages and rental rates, demand/output prices, cost interpretation, candidate generation/information set, and AI shock.
- GitHub code was committed; CI completion and results have not been verified.

## Local candidate-generation infrastructure — 2026-11-03

- Added `src/interfirm_abm/task_candidate_generation.py` and `tests/test_task_candidate_generation.py`. The generator takes an **externally supplied baseline 20-task plan** and an **externally supplied positive activity step**, returning the unchanged baseline plus single-task upward/downward activity changes and optional eligible pure-mode switches.
- The generator is deterministic, preserves fixed/adoption costs exactly as supplied, rejects invalid task identifiers and ineligible capital assignments, and never invents firm-specific investment budgets.
- The candidate set is **not** a behavioral learning rule. No information set, search cost, adaptive step size, trial-and-error policy, or belief formation is assumed. An eligible mode switch does not imply an actual adoption decision; zero-activity switches may be economically redundant.
- Candidates are not automatically resource-feasible; they must be passed through the existing bundle checker and, if relevant, the finite-candidate comparator. The resulting best candidate is only best within the supplied local neighborhood under the caller's aggregator/prices.
- Scientific simulation still awaits approved within-task production, task aggregation, costs, market demand/prices, AI shock, and economic behavior. CI not yet confirmed.

## Local pipeline integration — 2026-11-03

- Added `src/interfirm_abm/task_pipeline.py` and `tests/test_task_pipeline.py`. The pipeline composes the existing deterministic one-change candidate generator, shared-resource feasibility checker, economic accounting interface, and finite-set profit comparator.
- The caller supplies a baseline plan, activity step, task-output aggregator, and prices. The pipeline reports generated and feasible counts, baseline accounting profit, best candidate, and the best-minus-baseline **hypothetical** profit difference when baseline is feasible.
- A missing baseline profit (e.g. resource-infeasible baseline) yields no improvement metric; no realized change or behavioral learning is claimed.
- Tests use a simple additive aggregator as a deliberately injected **test stub**, not an approved economic production function. No 100-firm research results have been generated by these tests.
- **Remaining:** verify automated tests, audit approved CSV loading, researcher approval of technology and market assumptions, and eventually actual 100-firm economic simulation.

## Verified GitHub Actions checkpoint — 2026-11-03

- **Confirmed pass:** [Game 1 task-based validation run #3](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41608540625), triggered by commit `6151e32c57de9a43bb8fd1ed871ff2fc93447b06`.
- Python 3.11: **50 passed** in 0.12 s. Python 3.12: **50 passed** in 0.24 s. Verified directly from job logs, not inferred merely from workflow status.
- Both jobs concluded `success`. Post-run cache-reservation warnings did not fail tests or jobs.
- Scope: verifies the existing nine Game 1 test modules, including the canonical 100-firm/2,000-task population loader smoke test. **Does not verify market behavior, economic optimality, AI adoption, or research conclusions.**
- A later change to the canonical documentation does not affect the tested code. Subsequent changes to the code or data require renewed validation.

## Automated technical validation — 2026-11-03

- Added `.github/workflows/game1-task-validation.yml` to run the nine task-based Game 1 test modules on Python 3.11 and 3.12, on relevant main-branch pushes, pull requests, and manual dispatch.
- Added `tests/test_task_population_smoke.py` to load the canonical 100-firm profiles and 2,000 task records and assert basic structural consistency.
- The workflow was committed and its YAML contents re-read from GitHub. **No successful workflow run or passing test results have yet been verified.** A GitHub Actions green status is required before describing the implementation as tested.
- These checks are technical only. They do not validate a production function, an equilibrium, or any causal economic claim.

## Full 100-firm pipeline smoke test — 2026-11-03

- Added `tests/test_task_population_pipeline.py` to execute the existing local-neighborhood pipeline once for each of the approved 100 firms, using their canonical 2,000 task records. CI workflow includes this test file.
- Uses an explicitly **non-scientific fixture**: zero-activity labor baseline, unit activity step, unit input/output prices, and additive task aggregation test stub. These values are not approved or calibrated economic assumptions.
- Checks each firm yields a well-formed candidate set, a feasible baseline, finite comparable accounting values, and deterministic repeat results. Does **not** report aggregate output/profit or winners and losers as research findings.
- The test is committed, but **its CI result is pending verification**. The prior 50-pass result predates this new test.
- Next scientific design tasks: approve within-task production, task aggregation, price/cost interpretation, behavioral information and decision rule, and AI-induced technology change before research simulations.

## Verified 100-firm integration checkpoint — 2026-11-03

- **Milestone 4 (technical integration) passed:** [GitHub Actions Game 1 task-based validation run #5](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41646731779), triggered by commit `958c2e997cd7102737000700fe663f81c9dee34a`.
- Read the job logs: Python 3.11 **52 passed in 0.88 s**, Python 3.12 **52 passed in 0.60 s**. Both jobs and workflow concluded `success`.
- The two new tests exercise a canonical 100-firm / 2,000-task population through the local candidate-generation, feasibility, and accounting comparison pipeline, and check deterministic repeatability. Synthetic test-only prices, zero-activity baseline, unit activity step, and additive task stub are not research assumptions.
- Technical status: **PASS** for the tested commit; scientific status: **not validated**. Do not infer enterprise adoption choices, actual gains, market equilibrium, or AI effects from these unit/integration tests.
- Next research milestone: define and obtain researcher approval of within-task production, across-task aggregation, economic costs/prices, the firm's decision/information rule, and the AI shock before research experiment runs.

## Purpose

Construct an economically coherent artificial market of approximately 100 heterogeneous firms, with production technologies represented using Varian's production theory, firm-level economic decisions, and pre-/post-AI comparisons. This is a foundation for Games 2 and 3, not a mechanism designed to induce cooperation.

## Audit of the existing baseline

The current main-branch experimental design documents output maximization rather than profit maximization; no product-market competition; costless experimentation; deterministic production; and no AI investment. It labels profit, consumer surplus, welfare, and AI investment as future extensions. Accordingly, current learning-efficiency comparisons are **technical validation**, not completed Game 1 economic findings.

## Conceptual layers

1. **Technology:** Represent feasible production plans, initially through tested production functions but architecturally extensible to production sets, input requirement sets, and activity analysis. Distinguish functional forms from properties such as substitution elasticity, returns to scale, and convexity.
2. **Economic decisions:** Firms choose feasible inputs, production, and investments subject to costs, resource constraints, and available information. The objective and information set must be specified and approved before implementation.
3. **Market interaction:** Specify demand, price determination, supply, profits, and welfare accounting. Do not infer these from output efficiency.
4. **AI change:** Specify whether AI shifts total factor productivity, alters substitution, constitutes a separate input, or combines mechanisms. Compare matched pre-/post-shock environments without presupposing winners or losers.

## Relationship to subsequent games

Game 2 adds rival observation, information, and strategic learning within the same economic environment. Game 3 adds voluntary knowledge-sharing decisions and partner choice. Game 1 must not encode forced cooperation, sharing payoffs, or outcomes favorable to cooperation.

## Decisions requiring explicit theoretical specification before code

- Feasible technology representation and admissible firm heterogeneity.
- Objective function and input/resource prices.
- Demand and market-price formation.
- What firms know about their own technology and market conditions.
- Timing and adjustment rules, including any experimentation costs.
- AI shock, investment costs, and accumulation mechanism.
- Definitions of profit, market concentration, consumer surplus, and welfare.
- Experimental controls, validation tests, and matched comparisons.

Do not fill these gaps with arbitrary default economic assumptions. Recover previously approved choices where possible, and seek researcher approval for unresolved foundational choices.

## Implementation sequence

1. Audit current source and tests against this document and the charter.
2. Specify and validate the technology interface and economic accounting.
3. Implement the market and firm-decision environment with explicit assumptions.
4. Implement pre-AI and post-AI phases with controlled comparisons.
5. Validate accounting identities, feasible choices, market behavior, and reproducibility before reporting economic results.

**Research safeguard:** The model should make it possible to investigate whether cooperation emerges in later games; it must not make cooperation inevitable.

## Researcher-approved experiment architecture: extensible strategies — 2026-11-03

**Approved conceptual requirements (not yet implemented):**

- Use **one shared competitive market** per simulation run, rather than independent markets for strategies.
- Define base-firm characteristics, technology, initial inputs and initial conditions separately from behavior. For a controlled comparison, clone each base firm once per registered strategy; clones share the same initial attributes but become independent competing agents.
- Strategy identifiers are **open-ended strings**, e.g. `A`, `B`, `C`, `AXXXX`. Do not hard-code a three-strategy limit or use production-function names as strategy identifiers.
- With `N` base firms and `S` strategies, a fully crossed experiment contains `N × S` competing agents. Strategy additions create further agents in the **same** market.
- All agents interact through shared market outcomes. Evaluate per-round and cumulative payoffs, with matched comparisons among clones of the same base firm over repeated rounds.
- Adding strategies changes the market composition and potentially prices and outcomes for all existing strategies. Record the full strategy roster and market setup for each run; do not interpret cross-roster comparisons as isolated strategy effects.
- The current 100-firm heterogeneous synthetic population is **not** automatically replaced or deleted. The researcher has clarified a homogeneous-base-firm comparison as the initial controlled scenario; reconcile this with the existing heterogeneous population before experiments.
- No specific strategy decision rules, production function, pricing rule, AI shock, or payoffs have been approved by this architectural clarification. Do not implement research behavior by guessing them.

**Implementation boundary:** The existing technical pipeline and passing CI tests remain intact. This checkpoint records research design; modular strategy registration and cloning are future implementation tasks.


## Extensible shared-market strategy clones — implementation checkpoint (2026-11-03)

- Implemented `src/interfirm_abm/task_strategy_population.py`: open-ended `StrategySpec` identifiers; `build_shared_market_population` constructs one independent `TaskBasedFirm` clone per (base firm, strategy) pair, with identical initial tasks, capital, and labor and unique `base_firm_id::strategy_id` identifiers.
- Implemented `tests/test_task_strategy_population.py` and included it in `.github/workflows/game1-task-validation.yml`. Checks 300 agents for three strategies, 400 for four including `AXXXX`, arbitrary IDs, deterministic construction, and invalid rosters.
- **Scope boundary:** `SharedMarketPopulation` is a container for agents in one intended market; it does not yet simulate shared demand, endogenous prices, strategic decisions, interactions, or payoffs. Strategy labels are not executable policies. Technical checks must not be interpreted as an economic experiment.
- The original heterogeneous 100-firm CSVs are preserved as the existing fixture. The homogeneous-base-firm experimental scenario requested by the researcher remains to be specified independently.
- **CI VERIFIED (2026-11-03):** [GitHub Actions run #41649277668](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41649277668), code commit `b408019726b58308e014a6c14b374dc84a1947c0`, completed `success`: Python 3.11 **62 passed (1.02 s)**; Python 3.12 **62 passed (1.26 s)**. Technical strategy-cloning milestone passed; no economic market behavior validated.

## Milestone 6 — Shared-market accounting layer (2026-11-03)

- Implemented `src/interfirm_abm/task_shared_market.py` to evaluate a **given** joint profile of externally supplied nonnegative agent outputs and total costs for the strategy clones in one shared market. The evaluator computes aggregate supply, calls a caller-injected inverse-demand function, and applies the same market price to all agents. Each agent retains independent revenue/profit accounting and base-firm/strategy identity.
- Added `tests/test_task_shared_market.py` to CI. Tests cover cross-agent price effects, 100 base firms × 4 strategies, negative profits, zero output, invalid data, and determinism. The inverse-demand examples in tests are **synthetic stubs**, not researcher-approved demand specifications.
- **Not an equilibrium or dynamic game:** No agent decision rule, optimization, endogenous price formation beyond the injected price schedule, market clearing/rationing, learning, AI shock, input cost derivation, repeated-round state, or welfare measure has been approved or implemented. Supply is assumed sold for accounting; this is not an empirically supported market-clearing claim.
- **CI VERIFIED (2026-11-03):** [Game 1 Actions run #41650640957](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41650640957), code commit `f36cd9f1ddb735b480128c2f5c714b7c0b870f62`, completed `success`. Python 3.11: **72 passed in 0.64s**; Python 3.12: **72 passed in 1.38s**. Shared-market *technical accounting* passed. **Economic market equilibrium, behavioral learning, and scientific conclusions remain unvalidated.**

## Milestone 7 — Repeated shared-market accounting (2026-11-03)

- Added `src/interfirm_abm/task_repeated_market.py`: evaluates an externally supplied sequence of complete joint output/cost profiles for the same strategy-cloned population. At each zero-based round, all agents share a price returned by a caller-injected `inverse_demand(round, total_supply)` schedule. Tracks individual round profits, cumulative profits and first round reaching a cumulative-profit threshold.
- Added `tests/test_task_repeated_market.py` to the Game 1 CI workflow. Tests include multi-round shared-price feedback, arbitrary strategy IDs with 400 agents, losses, round-dependent prices, invalid inputs and deterministic evaluation.
- **Interpretation boundary:** These are accounting trajectories for supplied hypothetical actions. No strategy behavior, input choice, learning, capital accumulation, demand estimation, equilibrium, welfare or AI shock is selected. Test price schedules and actions are synthetic fixtures, not scientific findings.
- **CI VERIFIED (2026-11-03):** [Game 1 Actions run #41651175768](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41651175768), code commit `1c19fc5b38ae0a401e56d7f7d9d5513ac812c0d3`, completed `success`. Python 3.11: **79 passed in 1.29s**; Python 3.12: **79 passed in 0.81s**. This validates the repeated-market accounting implementation and tests only. Researcher approval of economic decision rules and dynamic state remains required before behavioral simulation.

## Milestone 8 — Injected strategy policy interface (2026-11-03)

- Added `src/interfirm_abm/task_strategy_policy.py`: `AgentDecision(output, total_cost)`, `DecisionContext(round_index, clone, completed_rounds)`, `StrategyPolicy`, `generate_policy_actions`, and `run_policy_market`. Every strategy label must have an externally supplied policy; there are no built-in winning strategies or learning rules. Policies can inspect only completed-round market records supplied by the harness, not other agents' current-round actions.
- Added `tests/test_task_strategy_policy.py` to Game 1 CI. Synthetic tests exercise multiple rounds, equal treatment of labels, 400 agents, invalid actions/rosters, and reproducibility of stateless policies.
- **Scope limitation:** This is a software interface, not a researcher-approved economic behavior model. Policies currently output final quantity and total cost, not task-level K/L allocations or adoption decisions. Inputs and costs must ultimately be linked to feasible task plans and an approved production model before scientific use. Injected price functions are hypothetical. Stateful policies require explicit reproducibility controls; the current runner recomputes previous-round accounting when extending the trajectory, so injected demand schedules must be pure/deterministic.
- **CI VERIFIED (2026-11-03):** [Actions run #41652217057](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41652217057), code commit `a5146c8a4e8cd9a43f8411e8aa5d80fa982dfb48`, completed `success`. Python 3.11: **86 passed in 1.36s**; Python 3.12: **86 passed in 0.91s**. This validates policy-interface software behavior against synthetic tests, not the economic validity of modeled strategies.

## Milestone 9 — Task-plan strategy adapter (2026-11-03)

- Added `src/interfirm_abm/task_policy_adapter.py` with `TaskPlanPolicy`, `evaluate_policy_task_plan`, and `adapt_task_plan_policy`. A caller-supplied strategy chooses all 20 task modes and activity targets; the adapter quotes K/L and input costs, rejects resource-infeasible plans, calls an injected task-output aggregator, and converts the resulting output and total cost into the shared-market `AgentDecision` interface.
- Added `tests/test_task_policy_adapter.py` and included it in CI. Synthetic labor-only plans and sum-of-activities aggregation are **test fixtures only**, not approved economic assumptions.
- **Scientific boundary:** Task-level linear activity, pure labor/capital execution, and externally supplied aggregation remain provisional. The adapter does not choose K/L, optimize, model AI adoption, validate production theory, or define market equilibrium. A researcher-approved task production model, aggregation, and input-price interpretation are required before interpreting outputs as economic evidence.
- **CI VERIFIED (2026-11-03):** [Actions run #41653126765](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41653126765), code commit `95e18529aae660137db5eec41a9b7fffa1935692`, completed `success`. Python 3.11: **89 passed in 0.77s**; Python 3.12: **89 passed in 0.92s**. This validates task-plan-to-market technical integration against test fixtures; it does not establish an approved task production function, optimizing behavior or economic equilibrium.

## Milestone 10 — Economic model validation audit (2026-11-03)

**Status: Theory audit, not approval or simulation evidence.** No production function, price schedule, or behavioral policy is selected by this section. Source: Acemoglu and Restrepo (2018), *The Race between Man and Machine*, American Economic Review 108(6):1488–1542, https://doi.org/10.1257/aer.20160696 ; Acemoglu and Restrepo (2018), *Modeling Automation*, AEA Papers and Proceedings 108:48–53, https://doi.org/10.1257/pandp.20181020 ; Acemoglu and Restrepo (2019), *Automation and New Tasks*, Journal of Economic Perspectives 33(2):3–30, https://doi.org/10.1257/jep.33.2.3 . Theoretical authority within this repo: `docs/theoretical_charter.md`.

### A. What the current implementation actually means

1. `task_based_firm.py`: provisional within-task activity `q_ij = aL_ij L_ij + aK_ij K_ij`, with capital disallowed on ineligible tasks. This implies perfect substitutability *within an eligible task* in the accounting formula; it does **not** establish the production technology that the researcher intends to study.
2. `task_execution.py` and `task_bundle.py`: compare **pure labor** and **pure capital** execution modes, with fixed target activity and finite K/L endowments. They do not optimize a continuous mixed input allocation, or include adjustment, fixed adoption, or sunk costs by default.
3. `task_aggregators.py`: linear, normalized Leontief, and CES candidates aggregate **task activities** into final output. The CES sigma is a **cross-task elasticity**, not directly an identified aggregate K/L substitution elasticity. Note: `weighted_leontief = min_j(q_j/omega_j)` is **not** the sigma-to-zero limit of the implemented weighted CES; the latter tends to `min_j(q_j)` under its current normalization.
4. `task_policy_adapter.py`: externally chosen task plans map to K/L accounting and market output/cost. It does not validate economic incentives or establish an optimizing firm.
5. `task_shared_market.py`: evaluates externally supplied joint quantities at a common caller-injected inverse-demand price. It is **not** an equilibrium model. All supplied output is valued at that price by convention, not because a sales/clearing mechanism has been established.
6. `task_strategy_policy.py`: only completed-round market history is provided by the harness. This is an information-set restriction of the implementation, not yet a researcher-approved behavioral assumption. The runner does not endogenously update capital, labor, productivity, technology eligibility, or knowledge.

### B. Required economics decisions (not approved)

| Layer | Question for principal researcher | Why it matters |
| --- | --- | --- |
| Within-task technology | Can capital and labor perform the same task, in exclusive modes or mixtures? Under what task-specific productivity and feasibility conditions? | Determines the economic meaning of automation and factor substitution |
| Cross-task aggregation | Are tasks essential/complementary, substitutable, or another production-set representation? Which normalization and task weights? | Determines marginal product, bottlenecks and output |
| Inputs and costs | Are K/L endowments fixed capacities, owned stocks, or purchasable flows? Are w and r market prices or opportunity costs? | Avoids mixing capacity constraints with rental-cost accounting |
| Automation | Does an AI shock change task eligibility, capital productivity, task set, or adoption cost? Are adoption and technological feasibility distinct? | Distinguishes displacement, productivity, adoption, and adjustment mechanisms |
| Market structure | Are firms price takers, Cournot quantity setters, or operating under another demand/sales arrangement? What information do they observe? | Determines whether quantity decisions internalize own price impact |
| Choice and timing | What objective, feasible set, beliefs, information, and decision sequence governs the firm? | Converts a technical policy interface into an economic decision model |
| Dynamic state | Which stocks/technologies/knowledge persist across rounds, and what are their transition laws? | Needed for learning and investment rather than independent accounting snapshots |
| Outcomes | Which welfare concept, counterfactual and price normalization are appropriate? | Prevents labeling aggregate profits as social welfare |

### C. Literature-grounded guardrails

- In Acemoglu and Restrepo's task framework, automation is **a change in which tasks capital can perform instead of labor**; it is not adequately represented merely by increasing an aggregate productivity constant or changing the cross-task CES elasticity. Their models also distinguish displacement from productivity and reinstatement/new-task mechanisms. These results apply under the respective papers' assumptions, not automatically to this ABM.
- A task-based model does not, by itself, imply that automation increases profits for every firm, or that K/L ratios move in one direction for every firm. Prices, comparative productivity, costs, feasible task assignments and market feedback all matter.
- A 100-firm clone experiment with 3 or 4 strategies is a useful controlled software comparison, but it does not identify causal economic effects until treatment, common shocks, equilibrium/interference and counterfactual assumptions are specified.

### D. Recommended next validation sequence (not a choice of model)

1. Document an explicit *candidate* within-task production/assignment technology and its feasible set, then derive cost minimization for a given vector of task requirements.
2. Choose and normalize a *candidate* task aggregator; check monotonicity, scaling, zero-task behavior, and factor demand implications.
3. Define economic meaning of K/L stocks, wages/rental rates, and any automation fixed or adjustment costs; avoid double-counting.
4. Specify market demand and timing; distinguish accounting price from a justified market equilibrium or quantity-game outcome.
5. Only then implement optimizing or bounded-rational strategy policies and evaluate before/after automation counterfactuals.
6. Preserve the existing 89-test software baseline, adding economic property tests and sensitivity tests as hypotheses are approved.

**Decision gate:** This audit approves no new economic assumptions. The principal researcher must approve a candidate technology and market specification before research-grade simulation.

## Milestone 11 — Candidate within-task technologies and cost-minimization derivations (2026-11-03)

**Status:** Comparative theory note only. This section does **not** select the Game 1 technology, objective, cost structure, or AI shock. All formulas below are explicit candidate assumptions to be evaluated by the principal researcher. The approved direction remains task-based production.

### 11.1 Candidate A — Task assignment / pure-mode automation

For firm `i`, task `j`, required activity `q_ij >= 0`, task-specific efficiencies `aL_ij > 0`, `aK_ij > 0`, wage `w >= 0`, capital service price `r >= 0`, and an exogenous **technical eligibility** indicator `e_ij in {0,1}`:

- Labor mode: `L_ij = q_ij/aL_ij`, `K_ij = 0`; variable cost `cL_ij(q) = w q/aL_ij`.
- Capital mode, **only if** `e_ij=1`: `K_ij = q_ij/aK_ij`, `L_ij = 0`; variable cost `cK_ij(q) = r q/aK_ij`.
- If both modes are feasible, the unconstrained *per-task variable-cost* comparison selects capital only when `r/aK_ij < w/aL_ij`, labor only for the reverse inequality, and either at equality. This is **not** the globally optimal assignment when firm-wide K/L capacities bind or there are adoption/adjustment costs.
- With mode-specific fixed adoption cost `F_ij >= 0` payable for capital mode, comparison for one task and one period becomes `F_ij + r q/aK_ij` versus `w q/aL_ij`. A break-even activity threshold exists only if `w/aL_ij > r/aK_ij`: `q* = F_ij/(w/aL_ij - r/aK_ij)`. Sunk versus recurring costs and adoption persistence require separate specification.
- An AI *feasibility* shock can be represented as `e_ij: 0 -> 1`; a productivity shock `aK_ij` and a cost shock `F_ij` are conceptually different treatments. Eligibility does not imply adoption.

**Critical caveat:** The current `task_bundle.py` quotes match the *variable-cost arithmetic* of these pure modes, but do not optimize assignment or model fixed adoption costs or dynamic eligibility changes.

### 11.2 Candidate B — Continuous within-task K/L substitution

For a candidate task technology `q_ij = [beta_ij (aL_ij L_ij)^rho + (1-beta_ij) (aK_ij K_ij)^rho]^(1/rho)`, `0 < beta_ij < 1`, `rho=(sigma_KL-1)/sigma_KL`, `sigma_KL > 0`, interior cost-minimizing choices with positive `w,r` and `L,K` satisfy:

`K_ij/L_ij = [((1-beta_ij)/beta_ij) (aK_ij/aL_ij)^rho (w/r)]^sigma_KL`.

This elasticity `sigma_KL` describes **within-task capital–labor substitution**, unlike the existing `task_aggregators.task_ces` parameter, which describes substitution **between task outputs**. At `sigma_KL=1`, the limit is Cobb–Douglas; at low elasticity inputs approach complements; as elasticity becomes large they approach perfect substitutes under appropriate normalization. Boundary solutions and eligibility restrictions must be treated separately. This formula is a conditional first-order condition, not an approved model or a claim about aggregate factor shares.

### 11.3 Candidate C — Complementary within-task inputs

For a candidate fixed-proportions task technology `q_ij = min(aL_ij L_ij, aK_ij K_ij)`, the minimum-cost inputs for target `q_ij` with nonnegative prices are `L_ij=q_ij/aL_ij` and `K_ij=q_ij/aK_ij`; variable cost is `q_ij(w/aL_ij+r/aK_ij)`. The formula requires **both** inputs; merely enabling capital does not displace labor. This is a separate technological hypothesis, not an alternative implementation of the current pure-mode quotes.

### 11.4 Comparison and decision boundary

| Property | A: pure-mode task assignment | B: within-task CES | C: within-task complements |
| --- | --- | --- | --- |
| K and L jointly required within a task | No, by candidate assumption | Usually interior, depending on parameters and constraints | Yes |
| How AI may enter | Eligibility, task productivity, or adoption costs | Productivity/feasible set/parameters, explicitly defined | Productivity of one or both required inputs |
| Typical factor response | Discrete mode switch, subject to capacity and costs | Continuous conditional demand response | Fixed conditional proportions |
| Existing code support | Quotes and feasibility only | Not implemented | Not implemented |
| Approved by principal researcher | No | No | No |

**Cross-task aggregation remains a separate decision for all three candidates.** It is not valid to infer an aggregate capital–labor substitution elasticity solely from a CES aggregator over task outputs. Task-specific choices are also coupled by firm-wide resource constraints, output requirements, and any market objective.

**Important model distinction:** The currently coded provisional `q=aL L+aK K` is a *mixed-input linear accounting function* when eligibility permits capital. It is mathematically distinct from a discrete choice between labor-only and capital-only modes. Although both can produce a corner solution under simple linear prices without capacity constraints, they need not generate the same feasible assignments, especially with global resource constraints or fixed costs.

### 11.5 Validation gates before economic simulation

1. Decide whether the object of study is task *assignment* (candidate A), smooth within-task substitution (B), complements (C), or a theoretically justified heterogeneous combination.
2. Define the feasible input set and economic interpretation of the 100 firms' initial K/L endowments, including whether prices are opportunity costs, rental flows or purchases.
3. Choose task-output aggregation and clarify whether each task is essential; then derive the firm's constrained cost-minimization problem **jointly across 20 tasks**.
4. Define AI shock separately from AI adoption, including information, irreversibility, costs and transition timing.
5. Define product-market pricing and firm information before deriving a profit-maximizing policy. Do not use accounting results as equilibrium claims.

**Literature anchors:** Acemoglu and Restrepo (2018), *The Race between Man and Machine: Implications of Technology for Growth, Factor Shares, and Employment*, American Economic Review 108(6), 1488–1542, https://doi.org/10.1257/aer.20160696 ; Acemoglu and Restrepo (2018), *Modeling Automation*, AEA Papers and Proceedings 108, 48–53, https://doi.org/10.1257/pandp.20181020 ; Acemoglu and Restrepo (2019), *Automation and New Tasks: How Technology Displaces and Reinstates Labor*, Journal of Economic Perspectives 33(2), 3–30, https://doi.org/10.1257/jep.33.2.3 ; Varian, *Microeconomic Analysis*, 3rd ed., production and cost-minimization framework. These references motivate the economic questions; the candidate equations above are **explicit model constructions for review**, not quotations or validated specifications from the papers.

**Research governance:** No candidate is approved by this note. The researcher retains the choice of technology and assumptions; the assistant may implement mathematical property tests only after the choice is approved.

## Milestone 12 — Joint 20-task constrained cost minimization (2026-11-03)

**Status: theoretical derivation / candidate formulation only; not a selected production model.** This follows Milestone 11 candidate A (exclusive labor or capital task modes), while retaining the ability to replace that candidate after researcher approval. No new behavioral policy or economic experiment is activated.

### 12.1 Conditional cost-minimization problem

For firm `i`, tasks `j=1,...,20`, activity `q_ij >= 0`, mode `m_ij in {L,K}`, and technical eligibility `e_ij in {0,1}`, define the illustrative requirements:

`L_ij(L,q)=q/aL_ij; K_ij(L,q)=0`; `L_ij(K,q)=0; K_ij(K,q)=q/aK_ij` with `m_ij=K` only when `e_ij=1`.

Conditional on a **researcher-supplied** task aggregator `F_i`, output target `Ybar_i`, nonnegative wage `w`, capital-service price `r`, and (optional) task-mode adoption charges `f_ij >= 0`, a candidate firm problem is:

`C_i(Ybar_i; Kbar_i,Lbar_i) = min_{m,q} sum_j [w L_ij(m,q) + r K_ij(m,q) + f_ij 1{m_ij=K}]`

subject to `F_i(q_i1,...,q_i20) >= Ybar_i`, `sum_j K_ij <= Kbar_i`, `sum_j L_ij <= Lbar_i`, `q_ij >= 0`, and the eligibility mask. If the feasible set is empty, the target cannot be met with the given capacities. Adoption charges should be included only if they are genuine incremental costs of the relevant decision horizon; sunk charges must not be charged again. `w` and `r` are treated here as service/opportunity prices, not a statement that stocks are purchased each round.

This is a **mixed discrete-continuous** conditional cost-minimization problem. Independent per-task cheapest-mode selection is not generally valid under joint capacities, fixed adoption charges, or nonseparable task aggregation.

### 12.2 Shadow-value logic for fixed task requirements

For a given externally specified activity vector `q` and no adoption charges, suppose nonnegative multipliers `lambda_K` and `lambda_L` are attached to binding shared capacity constraints. The Lagrangian has terms `lambda_K(sum_j K_j-Kbar)` and `lambda_L(sum_j L_j-Lbar)`. For a *conditional* comparison of a task's modes at the same `q_j`, their effective costs are:

- Labor: `(w+lambda_L) q_j/aL_j`.
- Capital: `(r+lambda_K) q_j/aK_j`, if eligible.

Hence the conditional capital-mode preference is `(r+lambda_K)/aK_j < (w+lambda_L)/aL_j`, with ties allowed. This is an **economic interpretation of marginal scarcity**, not a general sufficient condition for the discrete global optimum: nonconvexities, adoption charges, and endogenous `q_j` can invalidate a per-task decomposition or a zero-duality-gap claim. Shadow prices are additional capacity-scarcity values *in this Lagrangian*; do not add them again as realized accounting expenses.

### 12.3 Constructed counterexample: independent task selection fails

**Illustration only; not a result from the 100-firm data.** Consider two active tasks, each with target `q=1`; all other tasks have fixed zero requirements. Both tasks are capital-eligible. Let `w=r=1`, `aL=1` and `aK=2` for both tasks. Thus each task costs `1` with labor or `0.5` with capital. Set shared capacities `Kbar=0.5` and `Lbar=1`.

Independent minimization selects capital for both tasks, requiring `K=1 > Kbar`: **infeasible**. A feasible least-cost assignment is capital for one task and labor for the other, requiring `K=0.5`, `L=1`, with variable cost `1.5`. Assigning both to labor violates `Lbar=1`. The example proves only that a per-task cheapest-mode rule can violate shared capacity constraints under these illustrative numbers. It does not establish the optimal economic model for Game 1.

### 12.4 Implications for future implementation

- A **feasibility evaluator** (existing `task_bundle.py`) is not an optimizer: it checks a supplied plan, not the best plan.
- For fixed `q`, finite-mode enumeration is conceptually possible (up to `2^20` combinations before eligibility pruning), but computational convenience alone does not justify the economic assumptions. Dynamic programming or mixed-integer optimization would require explicit modeling choices and numerical validation.
- With endogenous `q` and a chosen `F_i`, an optimization solver must handle the coupled output constraint; the existence, uniqueness, convexity and optimality guarantees depend on the chosen technology and fixed costs.
- The market decision remains separate: cost minimization at `Ybar` is only an input-demand subproblem. A profit-maximizing quantity decision would require a justified price/demand and information structure.
- A technological eligibility change `e_ij:0 -> 1` weakly expands the **feasible set** under otherwise unchanged assumptions, but need not strictly lower realized cost or induce adoption; this monotonicity statement is conditional on the candidate assignment model, not an empirical AI finding.

### 12.5 Researcher decision gate

Before implementing a joint optimizer or interpreting its results, confirm (i) task-assignment technology, (ii) whether task activity requirements or final output are fixed, (iii) cross-task aggregation, (iv) capacity and price interpretation, and (v) adoption costs/timing. Until then, keep Milestone 12 as a theory-only specification and preserve the verified 89-test software baseline.

**Theory anchors:** Varian, *Microeconomic Analysis* (3rd ed.), production sets, cost minimization and constrained optimization; Acemoglu & Restrepo (2018), *The Race between Man and Machine*, https://doi.org/10.1257/aer.20160696; Acemoglu & Restrepo (2019), *Automation and New Tasks*, https://doi.org/10.1257/jep.33.2.3. The constructed counterexample and Lagrangian expressions are derived for the explicit candidate above, not quoted findings from these sources.

## Milestone 13 — Existence, convexity and global optimality audit (2026-11-03)

**Status: conditional mathematical audit of Milestone 12 candidate A, not researcher approval.** No solver, economic policy or AI treatment is introduced. The mathematical results below are deductions from the explicitly stated candidate assumptions, not empirical findings.

### 13.1 Feasibility is distinct from optimality

For a given firm, take finite nonnegative capacity bounds `Kbar,Lbar`, strictly positive finite task efficiencies `aL_j,aK_j`, 20 tasks, and a fixed eligibility mask. A feasible plan must select one eligible mode for each task, assign `q_j >= 0`, satisfy shared capacity constraints and `F(q) >= Ybar`. An output target may be **infeasible** even when each task individually has an available labor mode. In particular, high task requirements can exhaust joint capacities.

**Check zero-output edge cases explicitly:** `Ybar=0` is feasible with `q=0` if `F(0)>=0` and zero-input modes are permitted; otherwise feasibility depends on the chosen aggregator. A negative or nonfinite target should be rejected by an implementation, but this is an input validation convention, not a theoretical result.

### 13.2 Conditional existence proposition

**Proposition (candidate A):** Suppose (i) the number of tasks and eligible mode assignments is finite and nonempty; (ii) `Kbar,Lbar` are finite and nonnegative; (iii) `aL_j,aK_j` are finite and strictly positive; (iv) `F: R_+^20 -> R` is continuous; (v) the output target is feasible; and (vi) costs are continuous in activity within each mode and finite, with any mode-fixed charges finite. Then the conditional cost-minimization problem attains a minimum.

**Argument:** For any fixed mode vector, shared K/L bounds and strictly positive efficiencies bound every `q_j` from above, so the feasible activity set is bounded. Nonnegativity, linear capacity inequalities, and the continuous-output superlevel condition make it closed; hence it is compact. Continuous cost attains a minimum on every nonempty fixed-mode feasible set. There are finitely many eligible mode vectors, so the least of their attained minima exists. This proves existence, **not uniqueness, convexity, efficient computability, or equilibrium**.

If the target is infeasible, the problem has **no feasible solution**; do not report a finite optimal cost. If capacity bounds are removed or the technology/cost assumptions change, this particular existence argument must be revisited.

### 13.3 Conditional convexity within a fixed mode

For a **fixed** eligible mode vector, activity costs and capacity constraints are linear in `q`. If `F` is **concave** and continuous, its superlevel set `{q : F(q)>=Ybar}` is convex. Therefore the fixed-mode conditional cost-minimization problem is a convex optimization problem (possibly infeasible). This includes an appropriately parameterized concave CES aggregator, but not every arbitrary user-supplied `F`.

The full mode-choice problem is generally **nonconvex** because the feasible set is a finite union of mode-specific sets. Fixed adoption charges can also create discrete jumps in the objective across mode selections. Thus a first-order condition or locally optimal candidate is **not generally sufficient** to establish a global optimum for the mixed problem.

**Uniqueness is not guaranteed:** Even a fixed-mode convex problem with linear costs can have multiple cost-minimizing activity vectors. Strict convexity/appropriate regularity of the objective and feasible set would need separate verification; do not infer unique K/L choices from existence alone.

### 13.4 Solution methods and what they certify

| Method | What it can establish | Important limitation |
| --- | --- | --- |
| Evaluate a supplied 20-task plan (existing code) | Whether that plan is feasible and its accounting cost | Cannot prove global optimality |
| Independent cheapest-mode choice | Conditional per-task cost comparison | Can violate shared capacities and output coupling |
| Enumerate eligible mode vectors, globally solve each continuous subproblem | Global optimum if all eligible modes are covered and each subproblem is solved globally with verified tolerances | Up to `2^20 = 1,048,576` mode vectors before pruning; computationally demanding |
| Mixed-integer optimization | Potential global certificates/bounds for an accurately encoded problem | Applicability and guarantees depend on chosen aggregator, objective, solver, tolerances and formulation |
| Heuristics / local search | Candidate feasible plans, useful exploratory baselines | No general global optimality certificate |

For a **fixed task-activity vector**, the problem reduces to a finite discrete assignment with shared resource capacities; for **endogenous task activities** and nonlinear `F`, it is a coupled mixed discrete-continuous problem. No algorithm should be selected solely because it is convenient to code.

### 13.5 Economic interpretation and remaining limits

- **A technology shock that expands the eligibility mask** weakly enlarges the candidate feasible set, holding all else constant. Conditional on an already feasible output target, its *minimum achievable cost* therefore cannot increase **if newly eligible modes are optional and existing costs/constraints are unchanged**. This does **not** imply observed adoption, higher equilibrium profit, higher welfare, or a fall in labor demand.
- Shadow-price comparisons in Milestone 12 are diagnostic conditional comparisons. With discrete choices, the Lagrangian dual can have a positive duality gap, and capacity multipliers need not globally rank mode assignments.
- Firm-wide capacities, labor and capital opportunity prices, adoption charges, and the meaning of `Ybar` must be settled before cost differences are interpreted as economic incentives.
- Cost minimization at fixed output is not profit maximization; the latter additionally requires an output/market decision and appropriate information assumptions.

### 13.6 Review checklist before any solver implementation

1. Researcher approval of the pure-mode task-assignment candidate or another within-task technology.
2. Researcher approval of the aggregator `F` and its continuity, concavity, normalization, zero-task and scale properties.
3. Specification of whether `q` is exogenous or chosen jointly to meet an output target, and whether a target is economically meaningful.
4. Economic treatment of K/L capacities, wages, rental rates, fixed adoption charges, and the time horizon.
5. Choice of numerical optimality standard: feasibility tolerance, objective tolerance, global bound/gap and reproducibility controls.
6. Separate scientific evaluation of automation counterfactuals after the mathematical model is approved.

**Literature orientation:** Varian, *Microeconomic Analysis*, 3rd ed. (production sets, conditional factor demand and cost minimization); Acemoglu and Restrepo (2018), *The Race between Man and Machine*, https://doi.org/10.1257/aer.20160696; Acemoglu and Restrepo (2019), *Automation and New Tasks*, https://doi.org/10.1257/jep.33.2.3. The compactness/existence and fixed-mode convexity arguments are **derived for this candidate model**; they should not be attributed as quoted theorems from the cited task-automation papers.

**Decision gate:** No economic assumptions or optimization algorithm approved by this audit. Preserve the current verified software tests and do not report simulated findings.

## Milestone 14 — Production-property audit: monotonicity, scale, continuity, substitution, convexity (2026-11-03)

**Status: theory-only review.** No candidate aggregator, within-task technology, optimization method, or AI shock is selected. Claims below are conditional mathematical implications of specified illustrative assumptions; they are not simulation findings or statements about observed firms.

### 14.1 Separate the objects under review

Let `q=(q_1,...,q_20)` denote task activities, `Y=F(q)` final output, and `(K,L)` available inputs. A **production set** records feasible input-output combinations; an **output aggregator** maps task activities to final output; a **policy** chooses an allocation from the feasible set. Properties of one do not automatically imply properties of the others.

For candidate A, task modes are discrete and eligible capital modes are optional. Let `V(Kbar,Lbar;e)` be the *maximum technically feasible output* with given capacities and eligibility mask, if a continuous aggregator and feasible plan are specified. Distinguish this technical frontier from output actually chosen by a profit-seeking or learning firm.

### 14.2 Monotonicity and free disposal

If unused K/L may be left idle, the eligible modes do not shrink, and technology does not change, increasing either resource capacity weakly enlarges the feasible set. Thus `V(Kbar',Lbar';e) >= V(Kbar,Lbar;e)` whenever `Kbar'>=Kbar` and `Lbar'>=Lbar`, provided the maxima exist. This does **not** imply actual chosen output or profit rises.

If `F` is componentwise nondecreasing, greater task activity cannot lower final output, holding other tasks fixed. For the existing candidate aggregators with nonnegative activities and strictly positive weights: weighted linear is increasing in each task; normalized Leontief is weakly nondecreasing (a non-bottleneck task can have zero marginal effect); weighted CES for `sigma>0` is weakly nondecreasing, with strictness and boundary derivatives depending on positive task activities and parameters.

**Free disposal** is an explicit production-set assumption, not a theorem from nonnegative coefficients. It must be stated before treating the output frontier as monotone.

### 14.3 Returns to scale and normalization

For `t>=0`, the candidate weighted linear, normalized Leontief and weighted CES task aggregators are **homogeneous of degree one in task activities**: `F(tq)=tF(q)`, using the continuous extension at `t=0`. The provisional pure-mode task requirements are also proportional to activity. Consequently, in the *unconstrained static candidate* with scalable input capacities, no fixed charges, unchanged technology and no non-scalable restrictions, the maximum feasible output scales linearly with a proportional scaling of both capacities. This is a **conditional constant-returns-to-scale construction**, not a finding about the 100 synthetic firms or actual industries.

With **fixed capacities** held constant, proportional expansion of a plan may be infeasible; with fixed adoption charges, scale economies can arise in *average cost* even if physical production is constant-returns-to-scale. A fixed monetary charge does not by itself change the physical production function's homogeneity. Dynamic investment or indivisibilities require separate analysis.

### 14.4 Continuity and discrete technology

Each implemented candidate aggregator is continuous on the nonnegative activity domain under its documented parameter restrictions, including its specified zero-activity behavior. For a **fixed** task-mode assignment, input requirements and task activities vary continuously with their continuous inputs.

A discrete switch in the chosen task mode can cause the **selected input allocation** to jump as relative costs cross a threshold. That does **not** prove that the production possibility frontier or the minimum-cost *value function* is discontinuous. With finitely many modes and continuous mode-specific value functions on a common feasible domain, their pointwise minimum is continuous; however, mode-specific infeasibility and changing eligibility can change that conclusion. A binary eligibility shock is a discrete change in the feasible technology, not an infinitesimal change of a continuous parameter.

### 14.5 Substitutability is level-specific

- **Within-task**: the provisional linear activity formula `q_j=aL_j L_j+aK_j K_j` permits perfect substitution when both inputs are technically eligible; pure-mode assignment is a *discrete* substitution choice. CES and fixed-proportions within-task models from Milestone 11 are separate candidates.
- **Across tasks**: `task_aggregators.task_ces` defines substitution among task activities, parameterized by `sigma_tasks`; it is not directly a within-task `sigma_KL`.
- **Aggregate K/L**: any effective substitution response of total firm capital and labor depends on task efficiencies, eligibility, task aggregation, input prices, resource capacities, and the allocation rule. It must be derived or simulated under approved assumptions, not inferred from one CES parameter.

### 14.6 Convexity, concavity and production sets

For nonnegative task activities and strictly positive weights, the candidate weighted linear aggregator is both concave and convex; normalized Leontief (a minimum of linear terms) is concave; the weighted CES power-mean aggregator with `sigma_tasks>0` (equivalently `rho<1`) is concave on the nonnegative orthant. Their superlevel sets `{q:F(q)>=Ybar}` are therefore convex.

**However**, a union over discrete pure-mode task assignments need not be convex even if each fixed-mode feasible subset is convex. In particular, a midpoint of a labor-only plan and a capital-only plan may require mixing modes prohibited by the candidate A assignment rule. Thus the full task-assignment production set and optimization problem are not guaranteed convex. A mathematical relaxation permitting fractional mode mixtures may change the economic technology and cannot silently be treated as equivalent.

### 14.7 Property-test matrix (specification only, no tests added)

| Proposed test | Expected conditional property | Boundary / failure mode |
| --- | --- | --- |
| Task aggregator monotonicity | `F(q+delta)>=F(q)` for nonnegative `delta` | Nonmonotone researcher-supplied aggregators need not pass |
| Positive homogeneity | `F(tq)≈tF(q)` for `t>=0` | Fixed charges are cost, not output; finite precision near zero |
| Continuity | Nearby positive activity vectors yield nearby output | Do not mistake jumps in chosen modes for discontinuity of `F` |
| Concavity | `F(theta q+(1-theta)z)>=theta F(q)+(1-theta)F(z)` | Requires candidate aggregator assumptions and numerical tolerance |
| Capacity expansion | Enlarged capacities do not remove feasible old plans | Fails if extra capacity must be used or technology changes |
| Eligibility expansion | Newly capital-eligible tasks preserve old feasible plans | Does not guarantee adoption, profit, or welfare gains |
| Full technology convexity | **Not generally expected** for exclusive task modes | Convexification changes candidate technology |

These are candidate *mathematical property checks*, not an instruction to rewrite or approve production functions. Existing CI tests remain the technical baseline; no new CI run is required for this documentation-only audit.

### 14.8 Decision gate and theoretical references

Before adding property-based tests or optimization to the canonical Game 1 pipeline, the principal researcher must approve (i) the within-task feasible technology, (ii) the cross-task aggregator and normalization, (iii) whether free disposal is assumed, (iv) the economic meaning of fixed capacities and costs, and (v) whether a convex relaxation is economically admissible.

**Theory orientation:** Varian, *Microeconomic Analysis*, 3rd ed., production theory, production sets, returns to scale, cost functions; Acemoglu & Restrepo (2018), *The Race between Man and Machine*, https://doi.org/10.1257/aer.20160696; Acemoglu & Restrepo (2019), *Automation and New Tasks*, https://doi.org/10.1257/jep.33.2.3. The property statements here are mathematical deductions for the stated candidates, **not** quotations or empirically validated results from these works.

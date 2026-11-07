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

## Milestone 15 — From task technology to firm cost and market supply (2026-11-03)

**Status: economic-theory comparison, not model selection.** This note separates conditional cost minimization from output choice and strategic market behavior. It does not approve a demand function, price-taking assumption, Cournot game, equilibrium concept, cost schedule, or firm policy.

### 15.1 Cost minimization as a conditional subproblem

For a specified candidate task technology `T_i`, capacities `Kbar_i,Lbar_i`, and output requirement `Y`, define the **conditional variable cost**:

`C_i^v(Y;Kbar_i,Lbar_i,e_i,w,r) = min_{(q,m,K,L) in T_i, F_i(q)>=Y, K<=Kbar_i, L<=Lbar_i} (wL+rK + eligible incremental mode charges)`.

If no feasible plan meets `Y`, define `C_i^v(Y)=+infinity` for mathematical bookkeeping. The capacity-constrained feasible output set `D_i={Y>=0: C_i^v(Y)<infinity}` must be established from technology; do not assume it is unbounded.

**Accounting boundary:** If K and L are fixed *owned* capacities, clarify whether `rK` and `wL` are actual purchased service flows, imputed opportunity costs, or already-sunk expenditures. Avoid counting both acquisition costs and full service costs for the same input over the same period. Fixed costs can be separated as `C_i(Y)=C_i^v(Y)+F_i^{fixed}` when economically justified, but fixed costs must not be confused with sunk costs or technology feasibility.

With free disposal and nonnegative incremental costs, `C_i^v(Y)` is weakly nondecreasing in the **minimum-output-requirement** `Y` because `{plans:F(q)>=Y_2}` is a subset of `{plans:F(q)>=Y_1}` for `Y_2>Y_1`. This conditional monotonicity does **not** imply differentiability, convexity, or a continuous marginal-cost schedule. Discrete automation choices may produce kinks or nonconvexities.

### 15.2 Output choice under price-taking behavior (candidate only)

If a firm faces an **exogenous** output price `p>=0` and can sell all chosen output at that price, a static candidate is:

`max_{Y in D_i} [pY-C_i(Y)]`.

At a differentiable *interior* optimum, `p=C_i'(Y)` is a **necessary** first-order condition; it is sufficient for a global maximum only with additional conditions such as convex cost and a convex feasible output interval. With capacity limits, corners, discrete task modes, or nonconvex costs, one must compare global profit values and consider boundary choices. No universal smooth supply curve follows from the current task-based code.

An industry with 100 firms does not automatically make each firm a price taker. Price-taking is an explicit information/market-power assumption, not a population-size threshold.

### 15.3 Output choice with strategic quantity competition (candidate only)

Under a **Cournot-style** candidate, with a differentiable inverse-demand function `P(Q)` and `Q=sum_i Y_i`, firm `i` chooses `Y_i` given competitors' quantities:

`max_{Y_i in D_i} [P(Y_i+Q_-i)Y_i-C_i(Y_i)]`.

For an interior differentiable optimum:

`P(Q)+Y_i P'(Q)=C_i'(Y_i)`.

The term `Y_i P'(Q)` represents the firm's own price impact, which the price-taking condition omits. These conditions are **not** sufficient for Nash equilibrium without verifying best responses, feasibility and any relevant regularity. A Nash equilibrium, if it exists, requires every firm's quantity to be a best response to the others. Multiple equilibria or no pure-strategy equilibrium can arise under some nonconvex/discrete technologies; no existence claim is made for the unspecified current market.

**Current code boundary:** `task_shared_market.py` and `task_repeated_market.py` calculate a common price for externally supplied quantities; they do not solve the price-taking supply problem, Cournot best responses, market clearing, or equilibrium.

### 15.4 Comparative statics of AI: conditional, not predetermined

Suppose an AI shock only expands task eligibility, leaving all old modes, input prices, capacities, adoption charges and the aggregator unchanged. The set of feasible production plans weakly expands. Consequently, the **conditional minimum cost** for any previously feasible target cannot rise; similarly, the firm's **maximum attainable profit** cannot fall *if the firm faces the same fixed price or the same fixed competitors' quantities and inverse demand* and can still choose its former plan.

These are **fixed-environment value-function inequalities**, not claims that equilibrium profits, wages, employment, consumer surplus or welfare increase. If every firm changes behavior, aggregate quantity and prices may change, and the strategic equilibrium must be solved anew. The shock may also alter costs or information, invalidating the fixed-environment comparison.

### 15.5 Costs, supply and welfare are different outputs

| Object | Conditional definition | Cannot infer without further assumptions |
| --- | --- | --- |
| Minimum cost | Least expense for target output under a specified technology | Observed input allocation or actual behavior |
| Supply decision | Chosen output given price or strategic beliefs | Unique smooth supply schedule |
| Firm profit | Revenue minus appropriately defined economic costs | Social welfare |
| Consumer surplus | Requires demand and allocation/sales assumptions | Welfare from aggregate firm profits alone |
| Total surplus | Requires consumer benefits and all relevant real resource costs/transfers | Welfare without a specified market and accounting boundary |
| Learning outcome | Requires policy, information, state transitions and feedback | Learning from a repeated accounting evaluator alone |

### 15.6 Suggested validation plan, conditional on researcher approval

1. Derive `D_i` and `C_i(Y)` from an approved task technology; check feasibility, monotonicity, boundary behavior, cost accounting and potential kinks.
2. Specify **one** market interpretation for the main baseline (price-taking, Cournot, or another justified institution); document information sets and timing.
3. Derive the corresponding global output-choice problem, then test it on transparent small examples before using the 100-firm population.
4. Distinguish exogenous-price counterfactuals from re-equilibrated market counterfactuals. Do not treat price impact as an optional code flag without economic meaning.
5. Define sales, transfers, fixed costs, investment costs and welfare components before reporting aggregate outcomes.
6. Preserve technical test coverage; add scientific property checks only after the principal researcher approves their assumptions.

**Theory references:** Varian, *Microeconomic Analysis*, 3rd ed., production/cost/profit maximization and competitive supply; Tirole, *The Theory of Industrial Organization* (1988), quantity competition and strategic market behavior; Acemoglu & Restrepo (2018), *The Race between Man and Machine*, https://doi.org/10.1257/aer.20160696; Acemoglu & Restrepo (2019), *Automation and New Tasks*, https://doi.org/10.1257/jep.33.2.3. All inequalities and first-order conditions above are conditional derivations for the candidate structures, not empirical findings or claims attributed verbatim to those sources.

**Decision gate:** The researcher must approve the task production specification and market institution before implementing cost curves, firm supply rules or equilibrium solvers. This milestone changes documentation only.

## Milestone 16 — Market equilibrium and strategic interaction audit (2026-11-03)

**Status: comparative economic theory only; no market institution, behavioral rule or equilibrium solver is approved.** This section connects the conditional cost/value analysis of Milestone 15 to market interaction while preserving the distinction between accounting trajectories and equilibrium outcomes.

### 16.1 Three different solution concepts

1. **Competitive equilibrium candidate.** Each firm chooses an individually optimal production/supply plan at an exogenous-to-it price `p`; a separate market-clearing condition equates aggregate supply to demand at that same price, subject to a fully specified demand side and trade feasibility. Price-taking alone, without market clearing, is **not** a competitive equilibrium.
2. **Nash–Cournot candidate.** For inverse demand `P(Q)`, firms simultaneously choose feasible quantities `Y_i in D_i`, taking rival quantities `Q_-i` as fixed in their best-response calculation. An equilibrium `Y*` requires `Y_i* in argmax_{y in D_i} [P(y+Q_-i*)y-C_i(y)]` **for every firm**. The common market price is `P(sum_i Y_i*)`. A first-order condition alone does not establish a best response or equilibrium.
3. **ABM learning trajectory.** At each round, policies generate choices based on an information set and past observations. Such a trajectory may fluctuate, stabilize, cycle, or exhibit persistent exploration. A stationary observed state is **not automatically** a Nash or competitive equilibrium, and failure to converge is not proof that no equilibrium exists.

The existing `task_shared_market.py`, `task_repeated_market.py` and `task_strategy_policy.py` evaluate externally supplied choices or injected policies. They do not verify the relevant best-response or market-clearing conditions.

### 16.2 Conditions that matter for equilibrium existence

For a **continuous-quantity Cournot** game, a standard sufficient route to a pure-strategy Nash existence theorem requires each firm's feasible quantity set to be nonempty, compact and convex, and each profit function to be continuous in all quantities and quasiconcave in its own quantity. Under those assumptions, a fixed-point existence theorem applies. These are **sufficient conditions**, not automatic consequences of the 100-firm task model.

Task-mode discreteness, adoption charges, endogenous capacity choices and nonconvex cost schedules can undermine own-quantity quasiconcavity or the required convexity. Consequently, **no pure-strategy equilibrium existence claim is justified for the present unspecified task model**. Mixed strategies, convexified production or alternative timing would require explicit additional assumptions.

For competitive equilibrium, the existence argument additionally depends on demand, feasibility, commodity structure and appropriate production/consumer assumptions. A common price computed from an inverse-demand function does not itself demonstrate market clearing or decentralized price-taking optimality.

### 16.3 Two-firm transparent benchmark (illustration, not empirical result)

Take two firms with constant marginal cost `c>=0`, nonnegative quantities, and linear inverse demand `P(Q)=a-bQ` over the economically relevant range, with `a>c` and `b>0`. Firm `i` solves `max_{q_i>=0} (a-b(q_i+q_-i)-c)q_i`. The best response is

`BR_i(q_-i)=max{0,(a-c-b q_-i)/(2b)}`.

The unique symmetric Cournot equilibrium is `q_1*=q_2*=(a-c)/(3b)`, `Q*=2(a-c)/(3b)`, and `P*=(a+2c)/3`. At this benchmark, `P*>c`. A price-taking benchmark under the same constant-cost simplification would instead require an explicit demand-clearing allocation at `P=c`; firm-level supplies may be indeterminate at that price. This comparison illustrates market power, **not** a prediction for the 100-firm ABM.

**Numerical consistency example:** with `a=10,b=1,c=4`, Cournot quantities are `q_1=q_2=2`, total quantity `4`, price `6`, and each firm's profit `(6-4)2=4`. These are constructed arithmetic checks only.

### 16.4 Automation comparative statics and strategic feedback

Let `C_i^0(Y)` and `C_i^1(Y)` denote before/after conditional cost functions under a **pure optional eligibility expansion**. Holding the other economic primitives fixed, `C_i^1(Y)<=C_i^0(Y)` at each previously feasible `Y`, as shown in Milestone 15. This does **not** order equilibrium prices, outputs, market shares or profits without solving the market interaction.

Distinguish three counterfactual levels:

- **Technical:** Which plans become feasible when an eligibility mask changes?
- **Partial equilibrium / fixed rivals:** What is a firm's optimal response with rivals' quantities and demand fixed?
- **Re-equilibrated market:** How do all firms respond, and what joint outcome satisfies the selected equilibrium or learning criterion?

A common AI shock can change all firms' best-response maps simultaneously. A change in one firm's profit may reflect its own technology, rivals' responses, and price feedback; these channels must not be conflated.

### 16.5 Shared market with strategy clones: unit of analysis

The 100 approved base firms and any cloned strategy agents must not be counted interchangeably. If each base firm is copied into four independently competing strategy agents, the market has **400 sellers**, not 100 sellers each considering four counterfactual policies. If the research goal is to compare four strategies **holding the same 100-firm market composition fixed**, the clean design is four separate matched market runs (one strategy assignment per base firm per run), with comparable shocks and initial conditions. If the goal is **within-market strategic coexistence**, 400 competing clones can be justified, but it is a different economic treatment with different aggregate supply and market power.

**Decision gate:** The principal researcher must choose whether strategy clones coexist as actual sellers or serve as matched counterfactual alternatives. Do not interpret a 400-agent market as the original 100-firm economy.

### 16.6 Equilibrium and learning diagnostics (specification only)

| Concept | Appropriate diagnostic | Not sufficient |
| --- | --- | --- |
| Price-taking firm optimum | Profit gap versus feasible alternative quantities at fixed price | `p=MC` alone at a corner or nonconvexity |
| Competitive equilibrium | Individual optimality **and** market clearing | Merely calling `P(Q)` |
| Cournot equilibrium | For each firm, unilateral best-response profit gap `<= tolerance` | Stable aggregate quantity or zero price change |
| ABM convergence | Time-series stability and cross-seed robustness, under declared metrics | A single flat trajectory |
| Market welfare | Consumer benefit, producer surplus and resource/transfer accounting under approved demand and cost definitions | Sum of accounting profits |
| Automation effect | Matched technology and market counterfactuals with explicit treatment | Before/after differences without controlled changes |

A proposed Cournot deviation metric is `gap_i=max_{y in D_i} pi_i(y,Y_-i)-pi_i(Y_i,Y_-i)`, with `gap_i>=0` when the current action is feasible. `max_i gap_i <= epsilon` can diagnose approximate Nash only when the unilateral maximizations are solved to sufficient global accuracy; a finite local-neighborhood check does **not** certify Nash in a nonconvex task model.

### 16.7 Researcher decision gate

Before implementing an equilibrium solver or reporting a market finding, the principal researcher must approve: (i) the task technology and derived feasible supply/cost correspondence; (ii) demand and sales rules; (iii) market institution (price-taking, Cournot or alternative); (iv) quantity/price information and timing; (v) strategy-clone unit of analysis; and (vi) equilibrium versus learning trajectory as the target object.

**Theory references:** Varian, *Microeconomic Analysis*, 3rd ed., firm supply and competitive equilibrium; Tirole, *The Theory of Industrial Organization* (1988), Cournot competition; Nash (1950), *Equilibrium Points in N-Person Games*, Proceedings of the National Academy of Sciences 36(1):48–49, https://doi.org/10.1073/pnas.36.1.48; Acemoglu & Restrepo (2018), *The Race between Man and Machine*, https://doi.org/10.1257/aer.20160696. The two-firm benchmark and diagnostics are constructed theoretical examples, not quotations or empirically validated results.

**Implementation:** Documentation-only update. No new simulation, optimization solver, production assumptions or CI tests are introduced.

## Milestone 17 — Before/after AI counterfactual design and identification audit (2026-11-03)

**Status: preregistration-style design proposal only.** No AI treatment, task technology, equilibrium model, strategy, welfare definition, or scientific hypothesis is approved. No experiment has been run. This section provides a framework for the principal researcher to select and authorize a research design.

### 17.1 Treatment must be specified before comparison

Let `e_i^0` and `e_i^1` denote firm `i`'s pre/post technical eligibility masks over 20 tasks. An illustrative **pure feasibility expansion** treatment satisfies `e_ij^1 >= e_ij^0` for all tasks and firms, with all other primitives held fixed. This isolates the option to use capital in newly eligible tasks. It is **not equivalent** to an AI productivity shock (`aK` change), an adoption-cost reduction, or new task creation; these require separate treatments and potentially different theoretical predictions.

Record the treatment assignment at the **base-firm and task** level, not only as an aggregate AI indicator. Eligibility is not actual adoption. The adoption decision may depend on prices, costs, endowments and information.

### 17.2 A staged counterfactual ladder

| Stage | Technology | Firm actions | Rival actions and price | What it identifies conditionally |
| --- | --- | --- | --- | --- |
| S0: baseline | `e^0` | Pre-shock feasible plans | Pre-shock market environment | Reference outcome |
| S1: mechanical replay | `e^1` | **Exactly the same** old plans | Same rival actions and price | Feasibility/accounting consistency check; **zero effect** for a pure optional eligibility expansion with unchanged costs and plans |
| S2: own response, fixed environment | `e^1` | Firm `i` reoptimizes (if a choice model is approved) | Rivals' quantities and demand held fixed | Firm-level option value / partial response, not a market equilibrium effect |
| S3: joint response | `e^1` | All firms adjust under the same approved rule | Market price responds endogenously | Total change including strategic feedback, conditional on model |
| S4: dynamic learning | `e^1` | Firms learn with specified information/state transitions | Time-varying joint actions and prices | Path-dependent adaptation; **not** automatically equilibrium |

The stages answer different questions. S1 is not an estimate of productivity effects if the shock only changes optional eligibility: the old feasible plan remains available and unchanged. The S2-to-S3 difference is a useful **scenario comparison**, but cannot automatically be called a unique additive “competition effect”: nonlinear responses, equilibrium selection and spillovers may make the decomposition path-dependent.

### 17.3 Counterfactual notation and decomposition limits

Let `O_i(T,A_i,A_-i,P)` denote a selected outcome (e.g. firm profit), where `T` is the technology regime, `A_i` own action, `A_-i` rival actions and `P` the price rule. An illustrative comparison is:

`Delta_i^joint = O_i(T^1,A_i^1,A_-i^1,P^1) - O_i(T^0,A_i^0,A_-i^0,P^0)`.

An own-response comparison with rivals fixed is

`Delta_i^own = O_i(T^1,A_i^{BR,1}(A_-i^0),A_-i^0,P(Q_i^{BR,1}+Q_-i^0)) - O_i(T^0,A_i^0,A_-i^0,P^0)`,

where the **market price is recomputed consistently with the firm's unilateral quantity** under an inverse-demand game. Alternatively, a genuinely exogenous-price experiment must explicitly keep `p` fixed; do not mix these institutions. `Delta_i^joint - Delta_i^own` is a **path-specific residual** rather than an identified universal strategic externality. No causal empirical identification is claimed by synthetic counterfactuals.

### 17.4 Matching, interference and strategy cloning

- Use the approved 100 base-firm identifiers and 20 tasks as the matched unit across regimes. Preserve task efficiencies, initial capacities and all non-treatment primitives unless a separate factorial treatment explicitly changes them.
- A **100-firm matched scenario** and a **400-agent coexistence market** are different economies. Never present them as interchangeable comparisons.
- When comparing strategy policies, hold the market population definition, initial state, treatment, information timing and random-number design constant to the extent the chosen model permits. Distinguish independent-market replications from 400-agent within-market interactions.
- **Interference is expected:** a firm's outcome can depend on rivals' technology and actions via market price. Standard independent-unit treatment-effect language is inappropriate without a defined interference structure.
- In stochastic ABM runs, paired random seeds can reduce comparison noise when the stochastic streams and scenario coupling are well defined; identical seed labels alone do not guarantee identical random draws if the number/order of calls changes.

### 17.5 Outcomes and denominators to specify

| Level | Candidate measurement | Interpretation boundary |
| --- | --- | --- |
| Task | Eligibility share, capital-mode adoption share, task-specific activity and cost | Eligibility is not adoption; task weights and zero-activity tasks matter |
| Firm | Output, K and L used, K/L ratio, variable and total cost, profit, adoption expenditures | K/L undefined if L=0; input quantities and prices need consistent units |
| Market | Aggregate output, inverse-demand price, firm shares, profit distribution and concentration | Common market price alone is not a market-clearing or equilibrium certificate |
| Efficiency | Feasible output frontier, cost-minimization gap, best-response gap | Depends on approved technology and ability to solve global benchmarks |
| Welfare | Consumer surplus, producer surplus, real resource costs, investment costs | Cannot infer welfare from sum of profits; transfers and externalities need explicit accounting |
| Dynamics | Time-to-adoption, volatility, persistent mode choices, cross-seed distributions | Require genuine state transitions and policy behavior, absent in current accounting harness |

Define whether ratios are firm-weighted, output-weighted or task-weighted. Report both absolute and relative changes where denominators are nonzero, and identify zero-denominator cases explicitly. Do not call an accounting-profit sum total welfare.

### 17.6 Pre/post scenarios and falsification checks

1. **No-treatment replay:** `T^1=T^0` and identical action profiles must produce identical deterministic outcomes under the same price/cost functions.
2. **Eligibility-only mechanical replay:** old plans remain feasible and yield unchanged accounting outcomes if no other primitive changes.
3. **Feasible-set nesting:** an optional eligibility expansion must not remove previously feasible task bundles.
4. **Conditional cost monotonicity:** minimum cost at a fixed feasible output cannot rise after an optional eligibility expansion with unchanged economic primitives, if globally minimized.
5. **Firm fixed-environment option value:** maximum attainable profit cannot fall when the old feasible action remains available and the rivals/environment are held fixed; this does **not** order post-shock equilibrium profit.
6. **Equilibrium diagnostics:** if claiming Cournot outcomes, compute global unilateral best-response gaps; if claiming competitive equilibrium, check both price-taking optimality and clearing.
7. **Population integrity:** every scenario has exactly the declared number of market sellers; base firms and strategy clones are counted separately.
8. **Stochastic robustness:** declare number of replications, shock timing, randomization, uncertainty intervals and any stopping/convergence criterion before interpreting results.

These are **proposed future checks**, not passing tests. Existing verified CI (89 tests on Python 3.11 and 3.12 at run #41653126765) remains the software baseline, not scientific validation.

### 17.7 What cannot yet be concluded

No approved AI shock or adoption mechanism exists, so the model cannot currently estimate automation adoption, displacement of labor, equilibrium prices, welfare changes, winners/losers or cooperation effects. Nor can it attribute observed changes to AI without a controlled scenario design. Milestone 17 does not resolve the unresolved production/market choices of Milestones 11–16.

### 17.8 Researcher approval checklist

The principal researcher must decide: (i) exact AI treatment and timing; (ii) within-task technology and task aggregation; (iii) capacity, input price and adoption-cost accounting; (iv) output choice and market institution; (v) 100-firm matched scenarios versus 400-agent coexistence; (vi) outcome and welfare definitions; and (vii) whether the primary estimand concerns a static optimum, a strategic equilibrium or a dynamic learning path. Only after these decisions should an experiment runner or economic result pipeline be implemented.

**Theory anchors:** Acemoglu & Restrepo (2018), *The Race between Man and Machine*, https://doi.org/10.1257/aer.20160696; Acemoglu & Restrepo (2019), *Automation and New Tasks*, https://doi.org/10.1257/jep.33.2.3; Varian, *Microeconomic Analysis*, 3rd ed. (technology, cost, firm choice); Tirole, *The Theory of Industrial Organization* (1988) (strategic market interaction). The staged counterfactual ladder, matching rules and falsification checks are **proposed design constructions**, not claims that these references endorse the exact simulation protocol.

**Implementation status:** Documentation-only. No production code, tests, CI or economic assumptions changed.

## Milestone 18 — Consolidated Game 1 research design and decision register (2026-11-03)

**Status:** Consolidation for principal-researcher review; **not** authorization of unresolved economic assumptions. This section summarizes Milestones 10–17 without replacing their detailed derivations. The governing authority remains `docs/theoretical_charter.md`.

### 18.1 Research purpose and continuity

Game 1 is the economic baseline for a single research program investigating whether and when **voluntary interfirm knowledge sharing emerges among competing, self-interested firms**. Game 1 should characterize feasible production choices and market consequences of technological change without encoding a desired winner or cooperation outcome. Game 2 adds rival observation, experimentation and learning; Game 3 adds endogenous sharing decisions. Keep economic theory central and ABM instrumental.

### 18.2 Approved foundations versus unresolved specifications

| Dimension | Confirmed foundation | Unresolved decision (requires explicit approval) |
| --- | --- | --- |
| Disciplinary charter | Economics, Varian-style production/cost/choice foundations; Axelrod as cooperation inspiration | Any material change to the charter |
| Production representation | Task-based production inspired by Acemoglu–Restrepo, rather than imposing a direct two-input aggregate CES as the sole foundation | Within-task technology: discrete assignment, CES mixing, complements, or justified heterogeneous types |
| Population | Approved synthetic 100 base firms, 20 tasks each; canonical CSVs under `data/firms/` | Economic interpretation/calibration of task coefficients, capacities and heterogeneity |
| Task aggregation | Explicit aggregator-neutral software interface; candidate linear, Leontief, CES aggregators available | Which aggregator, task weights, elasticity, normalization and zero-task behavior |
| Factor inputs | K/L allocations subject to technical feasibility checks | Stock versus flow, owned versus hired capacity, input prices and opportunity costs |
| AI treatment | AI may change task automation feasibility | Which tasks change, whether productivity/adoption costs also change, timing, irreversibility |
| Decision problem | Feasibility, cost and accounting evaluators implemented | Conditional cost minimization, profit maximization, information, beliefs, horizon and behavioral policy |
| Market | Shared price accounting for supplied quantities implemented | Price-taking, Cournot or alternative institution; inverse demand and clearing/sales |
| Comparison design | Before/after counterfactual ladder proposed | Primary estimand, equilibrium versus learning, strategy clone coexistence versus matched scenarios |
| Outcomes | Technical output/cost/profit fields available | Economic cost definition, consumer surplus, welfare, adoption and displacement measures |

The previously discussed `alpha=0.5` and common productivity `A` belonged to an earlier aggregate CES framing. They **must not be imported** into the task model without renewed economic interpretation and approval.

### 18.3 Theoretical workflow: one coherent chain

**Technology and feasibility** `(task eligibility, task efficiencies, K/L capacities)` -> **task allocation and aggregation** `(q_j, F(q))` -> **conditional cost correspondence** `C_i(Y)` -> **output/market choice** `Y_i` -> **joint price and firm outcomes** -> **matched AI counterfactuals** -> **dynamic learning and voluntary sharing in later games**.

Every arrow requires an explicit economic mechanism; a software adapter is not evidence that the mechanism has been specified or validated.

### 18.4 Candidate minimal baseline for discussion (NOT APPROVED)

To reduce unnecessary degrees of freedom, a **candidate** initial theoretical benchmark could use: (a) exclusive task assignment between labor and eligible capital; (b) a clearly normalized task aggregator chosen from the tested candidates; (c) fixed finite K/L capacities and explicitly interpreted service prices; (d) optional automation eligibility expansion with adoption costs initially isolated as a separate sensitivity dimension; (e) an explicit single-market quantity or price-taking institution; and (f) matched 100-firm before/after markets rather than automatically treating 400 clones as the same economy.

This is a **review proposal only**, not a default implementation instruction. No part (a)–(f) becomes an official research assumption by appearing here.

### 18.5 Pre-implementation approval order and dependencies

1. **Production technology:** choose within-task feasible modes, input efficiencies and eligibility; decide whether mixed K/L within a task is meaningful.
2. **Aggregation:** choose `F(q)`, weights, zero-task rules and whether all 20 tasks are essential; establish monotonicity/concavity/homogeneity as applicable.
3. **Cost accounting:** clarify capacities, service prices, fixed versus sunk costs, adoption cost and time horizon; prevent double counting.
4. **AI treatment:** define exact eligibility/productivity/cost shock and which dimensions are held constant.
5. **Market institution:** define demand, pricing, sales, information and timing; choose competitive, Cournot or another mechanism.
6. **Agent choice:** specify objective, optimization versus bounded rationality, available information and state transitions.
7. **Experimental unit:** choose matched 100-firm scenario markets or a deliberately different within-market coexistence design; state stochastic replication protocol.
8. **Estimands and validation:** define cost, output, adoption, profit, equilibrium gap and welfare metrics; separate code tests from scientific claims.

A downstream choice must not silently settle an upstream unresolved assumption.

### 18.6 Minimal technical and scientific validation gates

- **Population integrity:** exactly 100 distinct base-firm IDs and 20 task records per firm in the approved dataset; no unannounced reweighting or duplicate market sellers.
- **Feasibility:** capital only in eligible tasks; K/L use within capacities; infeasible output targets reported explicitly.
- **Mathematical properties:** task aggregator monotonicity, scale behavior, zero handling and fixed-mode concavity checked against the approved specification.
- **Cost consistency:** fixed/variable/adoption charges distinguished; cost monotonicity under nested output targets where assumptions imply it.
- **Optimization:** a feasible plan is not necessarily optimal; global certificates or honest approximation gaps required before claiming optimum.
- **Market:** a common inverse-demand price is not an equilibrium; test global best-response gaps or market clearing as appropriate.
- **Counterfactuals:** no-treatment replay invariance, eligibility-only old-plan invariance, nested feasible sets, matched population, and controlled rival-price feedback.
- **Inference:** simulation comparisons conditional on model assumptions, not automatically real-world causal estimates. Learning dynamics must be explicitly implemented before claiming learning.

Existing software validation: [GitHub Actions #41653126765](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41653126765) succeeded with 89 tests on Python 3.11 and 89 tests on Python 3.12. This is **technical validation**, not approval of a production model or scientific evidence. This milestone adds documentation only, so no new CI run is claimed.

### 18.7 Decision register (for researcher approval, not filled by assistant)

| ID | Decision to approve | Current status |
| --- | --- | --- |
| D1 | Within-task production / assignment representation | Open |
| D2 | Cross-task aggregator and parameters | Open |
| D3 | K/L capacity and cost interpretation | Open |
| D4 | AI shock and adoption mechanism | Open |
| D5 | Product-market institution and demand | Open |
| D6 | Decision rule and information structure | Open |
| D7 | 100-base-firm versus 400-clone market interpretation | Open |
| D8 | Primary outcomes, welfare and counterfactual estimands | Open |

**Milestone 18 completion criterion:** A consolidated, internally consistent *review document* is complete when these open choices and dependencies are explicit. **Game 1 economic-model approval is not complete** until the principal researcher makes the relevant decisions. Do not implement an optimizing economic experiment or claim results on the strength of this consolidation alone.

**Literature orientation:** Varian, *Microeconomic Analysis*, 3rd ed.; Acemoglu & Restrepo (2018), *The Race between Man and Machine*, https://doi.org/10.1257/aer.20160696; Acemoglu & Restrepo (2019), *Automation and New Tasks*, https://doi.org/10.1257/jep.33.2.3; Tirole, *The Theory of Industrial Organization* (1988); Axelrod, *The Evolution of Cooperation* (1984). The dependency sequence, validation gates and candidate baseline are this project's research-design proposals, not empirical findings or direct prescriptions attributed to those sources.

## D1 researcher clarification — all four technologies as competing strategies (2026-11-03)

**Researcher instruction:** "Cứ làm hết phương án, và theo tôi nó là chiến lược" — retain **all** previously proposed A/B/C/D options as strategies to study, rather than asking the researcher to select only one. This supersedes the D1 single-choice gate in Milestone 18. **D1 scope approved: study all four.** The precise mathematical specifications, economic calibration, and comparison protocol remain open to review. Do not construe this instruction as approving arbitrary parameter values, output aggregation, demand, or market institutions.

### D1 strategy catalog (all retained)

| ID | Candidate technology strategy | Within-task activity representation | Critical boundary |
| --- | --- | --- | --- |
| A | Exclusive task assignment | Labor-only `q=aL*L` or eligible capital-only `q=aK*K` | Discrete mode choice, eligibility and possible adoption costs |
| B | Continuous K/L substitution | CES `q=[beta(aL*L)^rho+(1-beta)(aK*K)^rho]^(1/rho)` | Requires approved `beta`, `sigma_KL`, and how eligibility restricts capital |
| C | Fixed-proportions complementarity | `q=min(aL*L,aK*K)` | Requires both inputs; eligibility semantics must be reconciled |
| D | Hybrid task technology | Each task draws/receives a specified type among A/B/C | Must specify task-type assignment, information and fairness |

**Conceptual caution:** These are *production-technology strategies / technology regimes*, not yet behavioral strategies (e.g., myopic profit maximization, experimentation, imitation). Technology and behavior are separate experimental factors. In particular, strategy B and C are not simply alternative decision policies over an identical feasible set. Do not attribute performance differences to "better learning" if the underlying technology differs.

### Fair experimental comparison without preassigned advantage

1. Preserve the 100 approved base-firm identities and their 20 task IDs in each strategy scenario.
2. Use a **matched 100-firm market per technology regime** to isolate regime-level contrasts, or deliberately specify a mixed-regime 100-firm market to study coexistence. A 400-agent coexistence market is a different population and cannot be silently substituted for the approved 100-firm baseline.
3. Hold common initial attributes, task weights, input prices, demand, shock assignment and randomization protocol fixed when the economic meanings match; explicitly document quantities that cannot be equated across technologies.
4. Choose a normalization/calibration procedure so that different functional forms are not mechanically ranked by arbitrary output units or parameter scaling. Equal baseline output or cost is a **possible calibration target**, not yet approved.
5. Compare feasibility, input demands, costs, output, adoption, profit and market outcomes only after the shared aggregation and market rules are approved. Report heterogeneity and uncertainty; do not force a winner.
6. Keep technological eligibility distinct from behavioral adoption. For B and C, the meaning of "capital ineligible for a task" requires an explicit production-set specification (a CES task may become labor-only; a Leontief task may be infeasible unless its technology is modified). Do not silently impose the A rule on B/C.
7. The hybrid strategy D needs an explicit exogenous task-type mapping or an endogenous technology-selection decision with associated costs. These are **different** research questions.

### Updated decision status

- **D1: Scope decided — include A, B, C, D as competing technology strategies.** Exact forms/parameters/eligibility conventions remain pending, as does whether these are fixed firm types or selectable technologies.
- **D2–D8: Still open.** Cross-task aggregation, K/L accounting, AI treatment, market institution, behavioral policy, population comparison design and welfare metrics are not approved by D1.
- Existing technical `StrategySpec(strategy_id)` labels and market clones do not yet implement these four economic technologies. **Do not claim D1 code implementation or CI validation from this documentation update.**

**Theory:** Varian, *Microeconomic Analysis*, 3rd ed. (production sets and heterogeneous technologies); Acemoglu & Restrepo (2018), *The Race between Man and Machine*, https://doi.org/10.1257/aer.20160696 (task assignment and automation). CES and Leontief are conventional production representations used here as research alternatives, not asserted to be the exact Acemoglu–Restrepo task technology.

**Next technical step:** define a technology-neutral within-task evaluation interface and property tests that preserve the different feasible sets; do not activate economic results before the remaining researcher decisions.

## D2 review — Cross-task aggregation under four D1 technology strategies (2026-11-03)

**Status: proposal for researcher review, NOT approved.** D1 retains A/B/C/D as technology-strategy alternatives. D2 concerns the distinct mapping from 20 task activity levels to final firm output. Do not conflate a within-task CES in D1 with a CES **across tasks** in D2.

### D2 candidate aggregator set

For `q_j>=0`, positive task weights `omega_j`, and a common normalization chosen before comparison:

1. **Weighted linear:** `Y=sum_j omega_j q_j`. Tasks can compensate for one another at constant marginal rates in the activity space. This does not imply that labor and capital themselves are perfect substitutes across the whole firm.
2. **Leontief / essential-task bottleneck:** `Y=min_j (q_j/b_j)` with positive requirements `b_j`. An essential task with zero activity makes output zero; an increase in a non-bottleneck task may not change output.
3. **CES across tasks:** `Y=[sum_j omega_j q_j^rho_tasks]^(1/rho_tasks)` for appropriate parameter/domain conventions, with `rho_tasks=(sigma_tasks-1)/sigma_tasks`. The weights and scale normalization must be chosen consistently; the Cobb–Douglas limit needs its own well-defined normalization. This `sigma_tasks` is distinct from any `sigma_KL` within a task.

The user has **not** explicitly approved retaining all three D2 candidates. Their instruction to retain all options concerned D1. Therefore D2's three-way comparison is proposed, not recorded as an approved decision.

### Crossed research-design matrix (proposal only)

| D1 within-task strategy | D2 Linear | D2 Leontief | D2 CES |
| --- | --- | --- | --- |
| A: exclusive task assignment | Candidate | Candidate | Candidate |
| B: within-task CES | Candidate | Candidate | Candidate |
| C: within-task complements | Candidate | Candidate | Candidate |
| D: hybrid task types | Candidate | Candidate | Candidate |

Twelve cells are **candidate technology combinations**, not twelve validated economic models. The hybrid strategy needs a defined mapping of task types. For B/C, automation eligibility needs a defensible interpretation before evaluation. If a task is technologically infeasible under a regime, an aggregator that treats all tasks as essential can make the whole firm infeasible; this is a substantive economic implication, not a numerical error.

### Comparison safeguards

- Preserve 100 approved base-firm IDs and their 20 tasks in matched scenarios.
- Specify whether all tasks are essential or optional, and how zero-activity tasks are treated.
- Use common output units and explicit task weights/normalization; raw output levels from arbitrarily scaled functions are not comparable.
- Hold input price, capacity, demand and AI treatment definitions constant **where economically meaningful**; disclose technology-specific constraints.
- Treat the within-task technology choice and cross-task aggregator choice as distinct experimental factors; interaction effects may be research objects.
- Avoid ranking candidate cells by profitability before specifying and approving cost accounting and market demand.
- This matrix is a research-design proposal and does not imply that firms can endogenously choose their own production technology at zero cost.

### D2 approval gate

Principal researcher to decide whether D2 should (a) hold a single aggregator constant across all four D1 technologies to isolate within-task effects, (b) test all three aggregators in a 4×3 factorial design, or (c) adopt a different task aggregation representation. The choice of weights, CES elasticity, Leontief requirements, scale normalization and task essentiality is a **separate** parameter-approval step.

**Literature orientation:** Varian, *Microeconomic Analysis*, 3rd ed. (production aggregation and substitution); Acemoglu & Restrepo (2018), *The Race between Man and Machine*, https://doi.org/10.1257/aer.20160696; Acemoglu & Restrepo (2019), *Automation and New Tasks*, https://doi.org/10.1257/jep.33.2.3. These references support the general production/task framing, not this project's specific 4×3 matrix.

**Implementation:** Documentation-only proposal. No D2 assumption approved, no new simulations or tests.

## Researcher-approved multi-layer strategy architecture — D2 decision (2026-11-03)

**Explicit researcher decision:** Retain **all** D2 options (linear, Leontief, CES) as strategies, just as D1 retains all four within-task technology strategies. Each new strategy layer expands the combinatorial design by Cartesian product. **Persist each layer's identity and parameters** so results can later be analyzed by individual layer, interactions, or firm clusters. This is a project-wide experimental design principle, not a license to invent unapproved economic parameters.

### Approved layer catalog and current count

| Layer | Meaning | Options | Count | Approval |
| --- | --- | --- | --- | --- |
| L1 / D1 | Within-task production technology | Assignment; CES; Leontief; Hybrid | 4 | All options retained |
| L2 / D2 | Cross-task output aggregation | Linear; Leontief; CES | 3 | All options retained |

Current **12 technology strategy combinations** = `4*3`. For future layers with option counts `n_3,...,n_m`, the nominal full-factorial design has `N_strategy = 4*3*product(n_3,...,n_m)` combinations. Counts are nominal: a combination can be **structurally incompatible**, infeasible or redundant under its specified economics. Such cells must be flagged and not silently discarded or treated as valid results.

### Strategy identity, provenance and result schema (design contract)

Represent each scenario with a stable **structured strategy key**, e.g. `L1=assignment|L2=linear`, and an independent canonical `strategy_id`; do not rely on positional labels such as "strategy 7". Store:

- `experiment_id`, `scenario_id`, `strategy_id`, `base_firm_id`, `market_id`, `replication_id`, `round_index`;
- `layer_choices` (mapping `layer_id -> option_id`) and `layer_parameters` with versioned units/normalization;
- `technology_regime`, `shock_id`, `seed`, `population_definition`, `model_spec_version`;
- feasibility/status and outcomes (task adoption, K/L, output, cost, profit, price, market concentration and optional welfare after definition);
- cluster labels and **cluster definition version** stored separately from strategy-layer assignments.

A single `strategy_id` must never overwrite the constituent layer choices. Keep a registry of option definitions and their scientific rationale, references and researcher approval state.

### Analysis contract

1. **Layer-level effects:** summarize outcome distributions conditional on L1 and L2 separately, with market/scenario/replication and population definitions explicit.
2. **Interactions:** compare `L1 × L2` cells; effects need not be additive, and raw cell differences are not automatically causal.
3. **Firm heterogeneity:** stratify by pre-treatment, economically defined characteristics (e.g. K/L intensity, task capability, eligible task share). Do not define a purported baseline cluster using post-treatment outcomes.
4. **Clusters:** cluster membership must carry a definition/version and distinguish ex ante firm attributes from ex post outcome-based descriptive clusters; ex post clusters cannot be interpreted as predetermined causes.
5. **Market dependence:** firms in the same market interact through prices, so avoid treating firm rows as independent replications; market-level comparisons and uncertainty must respect shared shocks and within-market dependence.
6. **Balance:** if an interaction cell is infeasible, record it explicitly; avoid reporting marginal layer averages without identifying missing cells and weighting.
7. **Comparison unit:** a 12-cell crossed design does **not** mean 1,200 simultaneous competitors. Prefer 12 matched 100-firm market scenarios for isolation when later approved; mixed strategies in one market are a distinct, explicitly approved economic experiment.

### Remaining scientific and implementation gates

**Approved:** D1 scope = all four within-task technologies; D2 scope = all three aggregators; multi-layer Cartesian-product strategy bookkeeping; later layer and cluster analysis.

**Not yet approved:** actual parameters, hybrid task assignment, eligibility conventions for CES/Leontief, task weights/normalization, production and cost calibration, demand, market structure, whether all nominal combinations are economically meaningful, and whether regimes are separate markets or coexisting firms. D3–D8 remain open.

**Technical next step:** build a deterministic, data-only layer registry and Cartesian-product enumerator with unique stable keys and metadata, plus tests for 4×3=12 and future layer expansion, without generating economic output or altering existing approved firm population. Implementation must preserve existing `StrategySpec` compatibility and avoid conflating a strategy scenario with a market seller.

**Theory orientation:** Varian, *Microeconomic Analysis*, 3rd ed. (technology and cost comparisons); Acemoglu & Restrepo (2018), *The Race between Man and Machine*, https://doi.org/10.1257/aer.20160696 (task automation); the crossed-factor design and layer/cluster analysis protocol are **researcher-directed design decisions**, not empirical results or specific claims from these sources.

## D3 review — Resource access, factor costs and intertemporal constraints (2026-11-03)

**Status: proposed Layer 3 for researcher review, NOT yet approved.** D1 (four within-task technologies), D2 (three cross-task aggregators), and persistent layer/cluster metadata are approved as *scope*. D3 must distinguish input price accounting, physical capacity and dynamic adjustment; these are separate economic mechanisms, not necessarily mutually exclusive technology choices.

### Proposed D3 resource regimes

| Option | Proposed economic mechanism | Core mathematical distinction | Critical approval question |
| --- | --- | --- | --- |
| A — Flexible inputs | Hire input services at prices `w,r` without separate exogenous K/L capacity bounds | `min wL+rK` subject to production feasibility | Are prices fixed and input services freely accessible? |
| B — Capacity constrained | K/L quantities limited by existing feasible access | `K<=Kbar, L<=Lbar` | Are bounds stocks, service flows, credit limits or exogenous quotas? |
| C — Adjustment cost | Changing input use or capacity is costly | `cost_t=wL_t+rK_t+phi(Delta K_t,Delta L_t)` | What state carries over, and which changes are costly? |
| D — Capital investment | Firm can accumulate productive capacity over rounds | `K_{t+1}=(1-delta)K_t+I_t` (illustrative only) | What is the investment price, financing constraint, timing and depreciation? |

**Non-exclusivity warning:** C and D can coexist with A or B. A four-way D3 category is an initial *scenario-regime catalog*, not a logically exhaustive or orthogonal factorial decomposition. A cleaner future design might use separate resource-access, adjustment-cost and investment layers, multiplying combinations only when definitions are mutually consistent and economically meaningful.

### Layer multiplication and scenario counts

Current approved `L1 × L2 = 4×3 = 12` nominal strategy combinations. If the researcher approves the four proposed D3 regimes as a third scenario layer, the nominal count becomes `4×3×4=48`. **48 is a proposed design-space size, not 48 validated technologies, simulations, markets or competing firms.** For any future decomposed layers, count by the Cartesian product and retain an explicit compatibility flag for structurally inconsistent cells.

### Cost-accounting and dynamic safeguards

- Distinguish factor-service rental `rK` from capital-goods investment expenditure `p_I I`. If `K` is owned stock, avoid automatically charging both full capital rental and acquisition costs for the same period without a justified user-cost/financing model.
- A static one-period constrained optimization and a dynamic capital-accumulation problem do not have the same state space or objective; compare outcomes only under a declared horizon and discounting convention.
- Input scarcity and factor prices may both bind. Shadow values of capacity are not the same as market input prices.
- Keep AI adoption cost separate from K/L adjustment cost and capital investment cost unless the researcher explicitly defines their overlap.
- A strategy's technology layer (D1/D2) and resource regime (D3) are distinct explanatory factors. Do not call a profit difference a behavioral learning effect without implementing behavior.
- Cross-scenario comparisons need matched 100-firm identifiers, declared output normalization, comparable factor-price units and explicit market/replication IDs. Firms within one market are not independent samples.

### Proposed metadata

Extend `layer_choices` with `L3.resource_regime`; record `factor_price_basis`, `capacity_basis`, `adjustment_cost_spec`, `investment_law_spec`, `time_horizon`, `discounting`, `compatibility_status`, and parameter/specification versions. Store ex ante firm clusters separately from strategy layers and from ex post outcome clusters.

### Researcher gate

D3 options A/B/C/D and their mathematical specifications are **proposals**, not researcher-approved assumptions. The principal researcher may approve all as a layer, approve a decomposed factor design, or refine the catalog. No parameter values, dynamics or code are authorized by this note.

**Literature orientation:** Varian, *Microeconomic Analysis*, 3rd ed. (conditional factor demand, factor prices and constraints); Hayashi (1982), *Tobin's Marginal q and Average q: A Neoclassical Interpretation*, Econometrica 50(1):213–224, https://doi.org/10.2307/1912538 (investment/adjustment-cost theory); Acemoglu & Restrepo (2018), *The Race between Man and Machine*, https://doi.org/10.1257/aer.20160696. These sources motivate the categories; the A–D catalog and layer multiplication are project design proposals.

**Implementation:** Documentation-only D3 proposal; no production-code changes, no new simulations or tests.

## D3 researcher approval — four resource regimes in one layer (2026-11-03)

**Explicit researcher decision:** "Tôi phê duyệt D3 gồm bốn phương án A/B/C/D trong một layer. Hãy tiếp tục." D3 is approved **as one four-option strategy layer**, not decomposed into separate access/adjustment/investment layers. Retain all options: A flexible inputs, B capacity constrained, C adjustment cost, D capital investment.

### Updated approved strategy-layer registry

| Layer | Research dimension | Options | Count | Status |
| --- | --- | --- | --- | --- |
| L1 / D1 | Within-task production technology | Assignment; CES; Leontief; Hybrid | 4 | Scope approved |
| L2 / D2 | Cross-task aggregation | Linear; Leontief; CES | 3 | Scope approved |
| L3 / D3 | Resource/cost regime | Flexible Inputs; Capacity Constrained; Adjustment Cost; Capital Investment | 4 | **Scope approved, one layer** |

The nominal crossed design now has **4 × 3 × 4 = 48** strategy combinations. Preserve a stable composite strategy key with separate `L1`, `L2`, `L3` choices and all approved parameters and provenance. Retain compatibility/feasibility flags for cells where the economic primitives are not well-defined. No combination is silently removed, and the 48 combinations are **not** 48 concurrent firms, nor 48 simulations already performed.

**Important economic boundary:** D3 regimes are scenario labels, not mutually exclusive mechanisms in economic reality. Adjustment-cost and capital-investment regimes require a defined dynamic state and time horizon; their combination with fixed technology, input prices and market structure cannot be inferred from their labels. The approval is to **retain all four as options in a single layer**, not to invent investment laws, adjustment parameters or treat the options as proven comparable.

### D4 — AI shock and adoption layer: review candidates, NOT APPROVED

The next decision concerns what AI changes in the task economy, distinct from the D1 technology and D3 resource regimes. Candidate *treatments* for discussion:

| Candidate | Technology/economic intervention | Interpretation and safeguards |
| --- | --- | --- |
| A: Automation eligibility expansion | Expand which tasks permit capital execution, retaining old feasible modes | For CES/complementarity tasks, must specify a coherent eligibility mapping; mere eligibility is not adoption |
| B: Task capital-efficiency improvement | Raise capital task efficiency `aK_j` on specified tasks | Productivity shock differs from pure eligibility expansion |
| C: Adoption cost reduction | Reduce an explicitly modeled fixed or marginal adoption charge | Only meaningful if an adoption cost is defined and non-double-counted |
| D: Joint shock | Prespecified combination of A/B/C | Requires explicit component definitions and interaction attribution |

These are **proposed alternatives**, not researcher-approved D4 strategies. A future D4 layer would multiply the current 48 nominal combinations by the number of approved options, subject to compatibility flags. AI shocks must not silently force firms to adopt or predetermine the research outcome.

**D4 design gate:** The principal researcher must decide whether to retain all proposed D4 options as another layer, refine the treatment catalog, or use a single controlled shock. Timing, task coverage, shock magnitude, adoption behavior, treatment assignment, and normalization remain open.

**References:** Acemoglu & Restrepo (2018), *The Race between Man and Machine*, https://doi.org/10.1257/aer.20160696; Acemoglu & Restrepo (2019), *Automation and New Tasks*, https://doi.org/10.1257/jep.33.2.3; Varian, *Microeconomic Analysis*, 3rd ed. The proposed shock catalog is a project design framework, not a finding from those references.

**Implementation status:** Documentation-only update; no new strategy generator, economic model, simulation, tests or CI run.

## D4 researcher approval — four AI shock strategies in one layer (2026-11-03)

**Explicit researcher decision:** Approve retaining all four D4 options A/B/C/D as **one fourth strategy layer**, continuing the Cartesian-product multi-layer design. This is approval of the option catalog and layer architecture, **not** of shock magnitudes, task assignments, adoption behavior or economic results.

| Layer | Approved option catalog | Count |
| --- | --- | --- |
| L1 / D1 | Assignment; within-task CES; within-task Leontief; Hybrid | 4 |
| L2 / D2 | Cross-task Linear; Leontief; CES | 3 |
| L3 / D3 | Flexible Inputs; Capacity Constrained; Adjustment Cost; Capital Investment | 4 |
| L4 / D4 | Automation Eligibility Expansion; Capital Efficiency Improvement; Adoption Cost Reduction; Combined Shock | 4 |

**Nominal strategy count:** `4 × 3 × 4 × 4 = 192`. Store `L1`–`L4` identifiers and their parameter/definition versions for each strategy, along with market/scenario, base firm, task, replication and cluster metadata. Count feasible, incompatible and unparameterized cells separately. Do not interpret 192 strategy cells as 192 competing firms or completed simulations.

### D4 treatment boundaries

- **A — Eligibility:** expand capital-feasible task set without deleting prior feasible methods. Define separate eligibility semantics for each L1 technology, particularly complementarity.
- **B — Efficiency:** improve specified `aK_j` values. Do not automatically equate an efficiency gain with a task becoming eligible.
- **C — Adoption cost:** reduce a defined adoption expense. Without an approved cost function, this treatment is a placeholder and cannot produce economic effects.
- **D — Combined:** explicitly specify the component interventions and their magnitudes; do not infer an interaction effect from a single before/after comparison.
- Preserve no-treatment controls, identical-plan replay, matching and cross-market interference checks from Milestone 17. AI availability is not automatically AI adoption.

### D5 preview — Market institution layer (proposal, NOT APPROVED)

Candidate regimes to examine, retaining economic distinctions:

| Option | Institution | Necessary model ingredient |
| --- | --- | --- |
| A | Price-taking with market clearing | Firm supply choices and explicit demand/clearing |
| B | Cournot quantity competition | Inverse demand and globally evaluated unilateral best responses |
| C | Price competition | Product differentiation/capacity/rationing and a well-defined pricing game; homogeneous Bertrand can have degenerate outcomes |
| D | Dynamic adaptive market | Agent information, decision rules, price formation and state transitions; not necessarily equilibrium |

These are **candidate D5 strategies**, not yet approved. Market structures cannot be treated as mere labels over identical accounting rules. A price-taking market with clearing, a Cournot game, a Bertrand-style game and an adaptive ABM require different behavioral/institutional mechanisms. Keep D5 separate from learning-policy details that may later constitute an additional layer.

**Approval gate:** Researcher to confirm D5 catalog and whether all four institutions should form one layer. If four options are approved, the nominal crossed count becomes `192×4=768`; compatibility and comparison unit must be reported explicitly.

**References:** Varian, *Microeconomic Analysis*, 3rd ed.; Tirole, *The Theory of Industrial Organization* (1988); Acemoglu & Restrepo (2018), *The Race between Man and Machine*, https://doi.org/10.1257/aer.20160696; Acemoglu & Restrepo (2019), *Automation and New Tasks*, https://doi.org/10.1257/jep.33.2.3. These are theoretical anchors, not endorsements of the project's factorial design.

**Implementation:** Documentation-only update. No economic solver, layer generator, simulations, tests or CI run are claimed.

## D5 researcher approval — four market institutions in one layer (2026-11-03)

**Explicit researcher decision:** Retain all four D5 alternatives **in one layer**, following the approved multi-layer strategy architecture. The researcher approves the catalog and layer structure, **not** specific demand, game forms, behavioral equations, equilibrium solutions, or numerical parameters.

| Layer | Dimension | Options | Count |
| --- | --- | --- | --- |
| L1 / D1 | Within-task technology | Assignment; CES; Leontief; Hybrid | 4 |
| L2 / D2 | Cross-task aggregation | Linear; Leontief; CES | 3 |
| L3 / D3 | Resource and cost regime | Flexible Inputs; Capacity Constrained; Adjustment Cost; Capital Investment | 4 |
| L4 / D4 | AI shock mechanism | Eligibility Expansion; Capital Efficiency; Adoption Cost Reduction; Combined Shock | 4 |
| L5 / D5 | Market institution | Price-taking Competitive; Cournot Quantity; Price Competition; Dynamic Adaptive | 4 |

**Nominal strategy combinations: `4×3×4×4×4=768`.** Every scenario must retain a structured layer key, option identifiers, parameter and specification versions, compatibility status, market ID, base-firm ID, replication, and cluster provenance. A strategy combination is **not** a firm and 768 cells are **not** 768 simultaneous sellers or completed experiments.

### D5 distinctions that must survive implementation

- **Competitive:** price-taking firm optimality plus explicit market clearing and a coherent demand side.
- **Cournot:** quantities are strategic choices; evaluate unilateral best responses against rivals' quantities, with inverse demand.
- **Price competition:** prices are strategic choices; requires a precise product differentiation, capacity, rationing and sales rule where appropriate. Do not silently treat a homogeneous-product Bertrand outcome as the general price-competition result.
- **Adaptive market:** dynamic policy and price-formation rules must be specified; a simulated steady state is not automatically Nash or competitive equilibrium.
- Some crossed cells may require a separate time horizon or solution concept, especially dynamic D3 with static D5; preserve all nominal cells in the registry while explicitly flagging model-incompatibility or missing specifications.
- To isolate layer effects, distinguish separate matched 100-firm market scenarios from a deliberately constructed mixed-strategy market. Never multiply 100 base firms by 768 and present the result as the original economy.

### D6 preview — Behavioral and learning policy layer (PROPOSAL ONLY)

The next dimension concerns **how a firm chooses** within its feasible technology and market institution, distinct from the technology itself. Candidate policy families for researcher review:

| Option | Candidate decision policy | Required economic definition |
| --- | --- | --- |
| A — Optimizing benchmark | Choose globally profit-maximizing feasible action given information and institutional timing | Explicit objective, feasible action set, beliefs, optimization standard |
| B — Trial-and-error | Experiment with local K/L, task and/or output changes; evaluate realized outcomes | Experiment proposal, memory, acceptance/rejection and exploration rules |
| C — Softmax reinforcement | Assign choice probabilities based on learned action values | Action menu, reward signal, updating, temperature and decay |
| D — Rival-responsive imitation | Observe selected rivals and adapt toward their observed actions or performance | Observation scope, information noise, rival selection and feasibility |

These are **candidate D6 options**, not approved strategies. They are not necessarily mutually exclusive: trial-and-error may use softmax selection, and imitation can coexist with optimization. If retained as one categorical layer, define each as a complete, mutually identifiable **policy regime** rather than asserting their underlying behavioral mechanisms cannot coexist.

**Next decision gate:** Ask the principal researcher whether all four D6 candidate policy regimes should be retained as a single new layer. If approved, the nominal count would be `768×4=3,072`, subject to compatibility and computational feasibility. Do not implement behavioral dynamics before the policy rules and information sets are specified.

**Theory orientation:** Varian, *Microeconomic Analysis*, 3rd ed. (economic optimization); Tirole, *The Theory of Industrial Organization* (1988) (strategic competition); Sutton & Barto, *Reinforcement Learning: An Introduction*, 2nd ed. (2018) (reinforcement/softmax learning, as a computational mechanism rather than an economic finding); Posen & Levinthal (2012), *Chasing a Moving Target: Exploitation and Exploration in Dynamic Environments* (exploration/exploitation literature). These references motivate categories but do not validate this project's specific policy catalog.

**Implementation status:** Documentation-only approval record; no economic code, simulations, tests or CI run changed.

## D6 researcher approval — retain all four behavioral policy families in one layer (2026-11-03)

**Explicit researcher decision:** "có, giữ hết" in response to retaining all four D6 behavioral strategies in one layer. The approved **catalog scope** is:
- A — Profit Optimization (benchmark with explicit objective, feasible set and information).
- B — Trial-and-Error (local experiments, reward evaluation, memory).
- C — Softmax Learning (probabilistic action choice based on learned action values).
- D — Rival Imitation (observation of selected rivals, information and imitation rules).

D6 is **one four-option layer**. These are distinct **policy regimes** for factorial labeling, although their underlying mechanisms could be combined in a later separately approved model. Retaining all does not approve specific learning rates, temperature, memory decay, optimization solver, observed rival data, timing or action menu.

### Updated approved nominal layer space

| Layer | Meaning | Number of options |
| --- | --- | ---: |
| L1 / D1 | Within-task technology | 4 |
| L2 / D2 | Cross-task aggregation | 3 |
| L3 / D3 | K/L resource and cost regime | 4 |
| L4 / D4 | AI shock mechanism | 4 |
| L5 / D5 | Market institution | 4 |
| L6 / D6 | Decision/learning policy | 4 |

**Nominal Cartesian-product count: `4×3×4×4×4×4=3,072`.** Every record must preserve all six option IDs, parameters, status, and experiment provenance. This is **not** 3,072 firms, markets, completed runs or economically valid combinations. Incompatibilities and under-specified cells remain visible in the registry. Keep market/replication identifiers and ex ante firm clusters distinct from technology/policy strategy IDs.

### D6 interaction safeguards

- An optimizing benchmark requires an approved objective, information set and economic constraints; it is not interchangeable with a heuristic policy.
- Trial-and-error and softmax can both be mechanisms within a more complex policy; their placement in this layer means the researcher is comparing *policy regimes*, not asserting theoretical mutual exclusivity.
- Rival imitation needs a well-defined observable set, rival-selection rule and a feasible translation of observed rival actions into the firm's own technology and constraints.
- D5 market institution × D6 policy regime may have incompatible equilibrium interpretations: adaptive policy trajectories do not automatically satisfy Cournot, Bertrand or competitive equilibrium.
- Preserve the 100-base-firm population and task identities; do not automatically instantiate all 3,072 strategies simultaneously in one market.
- Evaluate layer interactions and clusters only after matched experiment designs, explicit outcome definitions, and treatment/market dependence are resolved.

### D7 preview — Population and market composition (NOT APPROVED)

The next decision is **how to place technology-policy combinations into markets**, distinct from the number of strategy cells. Candidate market-population arrangements:

1. **A — Matched separate markets:** 100 base firms in each strategy-cell scenario, with the same ex ante firm profiles; no cross-cell price spillovers. Allows controlled between-scenario comparisons.
2. **B — Mixed strategy market:** 100 total firms allocated among strategy combinations in a single market, with an explicitly defined assignment mechanism; strategic interactions and spillovers are endogenous to the mix.
3. **C — Matched clones coexist:** Clone 100 base firms into selected strategy variants in the same market (e.g. 100×k agents). This changes market size and competition and is **not** equivalent to A or B.
4. **D — Stratified mixed markets:** 100 total firms assigned to strategy variants by prespecified ex ante K/L, task capability or other firm strata; permits heterogeneous exposure, but requires assignment and causal interpretation safeguards.

These are proposed D7 **market-composition regimes**, not approved. They may be retained as another layer if the principal researcher chooses, but changing market size between A/B/C changes the economic object, not just a strategy label. For 3,072 × 4 options the nominal crossed count would be 12,288, with potentially incompatible cells.

**Literature orientation:** Varian, *Microeconomic Analysis*, 3rd ed.; Tirole, *The Theory of Industrial Organization* (1988); Sutton & Barto, *Reinforcement Learning: An Introduction*, 2nd ed. (2018); Posen & Levinthal (2012), *Chasing a Moving Target: Exploitation and Exploration in Dynamic Environments*. These support general economic and learning concepts, not the specific factorial catalog.

**Implementation:** Documentation-only researcher approval. No new executable strategy-layer registry, simulation, tests or CI results.

## D7 researcher approval — all four market-population regimes in one layer (2026-11-03)

**Explicit researcher decision:** "có, giữ hết" — retain all four D7 population/market-composition alternatives as **one layer**. This approves their inclusion in the research-design catalog, not their allocation algorithms or empirical comparability.

| Layer | Meaning | Number of options |
| --- | --- | ---: |
| L1 / D1 | Within-task technology | 4 |
| L2 / D2 | Cross-task aggregation | 3 |
| L3 / D3 | Resource and cost regime | 4 |
| L4 / D4 | AI shock mechanism | 4 |
| L5 / D5 | Market institution | 4 |
| L6 / D6 | Behavioral learning policy | 4 |
| L7 / D7 | Population and market composition | 4 |

**Approved D7 scope:**
- A — **Separate Markets:** matched 100-base-firm markets under separate strategy-cell scenarios.
- B — **Mixed Market:** one 100-firm market containing a defined mixture of strategy assignments.
- C — **Clone Competition:** matched base-firm clones with different strategies coexisting; number of agents can exceed 100, so market size, demand and strategic interactions differ.
- D — **Stratified Market:** strategy assignment conditioned on explicitly specified *ex ante* firm strata/clusters (e.g., K/L intensity, task capabilities), with 100 firms unless separately specified.

**Nominal full-factorial design size: `4×3×4×4×4×4×4=12,288`.** This is a **registry count**, not a count of agents, distinct valid economic models, simulations or completed experiments. Preserve `L1` through `L7` as explicit fields, along with versioned parameters, experiment/scenario IDs, market and base-firm identifiers, replication seeds, compatibility flags and cluster-definition provenance.

### D7 analysis safeguards

1. Do not assume one strategy cell maps to one seller: market composition is a **market-level experimental regime**.
2. Separate Markets and Mixed Markets answer different questions (isolated effects versus interactions/spillovers); do not pool their outcomes as if the treatment assignment were identical.
3. Clone Competition changes effective market size and possibly market power. Record `n_base_firms`, `n_market_agents`, cloning factor, demand scale and clone assignment explicitly.
4. Stratified Market needs **pre-treatment** cluster definitions, stratification weights and assignment rules. Ex post outcome clusters are descriptive, not valid ex ante strata.
5. Some D5 × D6 × D7 cells may be economically under-specified or conceptually incompatible. Retain their IDs and report status rather than silently deleting them.
6. Analyze within-market dependence and market-level replications, not firm rows as independent random trials.
7. Researcher approval does not specify the number of simulation replications, sampling design, demand parameters, strategy assignment shares or solver.

### D8 preview — Outcome and welfare analysis layer (PROPOSAL, NOT APPROVED)

D8 originally referred to **outcomes, welfare and estimands**. Because the user wants to preserve all options as analyzable layers, it is important not to mistake a *measurement lens* for an economically causal treatment. Proposed four D8 **analysis lenses**:

- A — **Firm performance:** output, costs, profit, capital/labor input, adoption and survival/concentration metrics where defined.
- B — **Market performance:** aggregate output, price, allocation, market concentration and dynamics, with explicit market definition.
- C — **Welfare/distribution:** consumer surplus, producer surplus, total surplus, and distribution across firm/worker groups **only** when demand, costs and transfers are defined consistently.
- D — **Learning/transition:** adjustment speed, regret relative to a feasible benchmark, exploration/exploitation, path dependence and adoption trajectories, requiring dynamic policy and time-series data.

These lenses can **all be measured on the same simulated run**; they are not mutually exclusive choices that change production or market behavior. If the researcher wants D8 to count as another four-option *analysis layer*, a nominal reporting grid would have `12,288×4=49,152` **scenario–analysis-lens records**, but **not** 49,152 different economic strategy configurations or simulations. Preserve the distinction between treatment/design layers L1–L7 and an optional outcome/analysis dimension L8.

**D8 researcher gate:** Approve all four lenses as a separate reporting/analysis layer, refine the outcome taxonomy, or keep outcomes as multiple metrics without multiplying strategy counts. Do not call outcome metrics causal strategies.

**References:** Varian, *Microeconomic Analysis*, 3rd ed.; Tirole, *The Theory of Industrial Organization* (1988); Acemoglu & Restrepo (2019), *Automation and New Tasks*, https://doi.org/10.1257/jep.33.2.3; Sutton & Barto, *Reinforcement Learning: An Introduction*, 2nd ed. (2018). These provide theoretical background for outcomes and learning, not an endorsement of the D8 taxonomy.

**Implementation:** Documentation-only. No new model equations, executable layer registry, simulation, tests or CI run.

## D8 researcher approval — four outcome lenses as one Analysis Layer (2026-11-03)

**Explicit researcher decision:** "chính xác" confirming that all four D8 outcome groups are retained as one **Analysis Layer** for layer-wise, cluster-wise and interaction analysis. D8 is **not** an eighth causal technology, behavioral policy, or market-composition strategy.

### Approved D8 analysis lenses

| Lens | Outcome family | Measurement prerequisites |
| --- | --- | --- |
| A — Firm Performance | Output, costs, profits, K/L mix, technology adoption and firm-level changes | Defined accounting, firm identity and factor prices |
| B — Market Performance | Aggregate production, prices, concentration, market dynamics | Market boundaries, demand and market-clearing/pricing rules |
| C — Welfare & Distribution | Consumer and producer surplus, total surplus, distributional impacts | Consistent demand, cost and transfer definitions; welfare not inferred from firm profit alone |
| D — Learning & Transition | Adaptation paths, exploration/exploitation, speed of adjustment, regret, technology transition | Dynamic actions, comparable benchmarks, time-series and state histories |

### Two distinct cardinalities

- **7 strategy/design layers:** `4×3×4×4×4×4×4 = 12,288` **nominal** scenario strategy combinations. Not all are necessarily feasible, specified or comparable.
- **1 analysis layer with 4 lenses:** `12,288×4 = 49,152` **scenario–lens reporting pairs** if every nominal combination receives every lens. This is **not** 49,152 unique strategy configurations, market simulations, or firms.
- One simulated trajectory may support several or all lenses if the required economic data exist. Report unavailable metrics explicitly; do not invent welfare, equilibrium, or learning results.

### Data and analysis contract

Keep strategy layer IDs `L1` through `L7` immutable in each scenario record and `analysis_lens_id` separately in output tables. Maintain `strategy_id`, `scenario_id`, `market_id`, `base_firm_id`, `agent_id`, `round_index`, `replication_id`, `seed`, `model_spec_version`, `compatibility_status`, and `cluster_definition_version`. For cloned markets distinguish base firm from clone agent. Cluster definitions should distinguish **ex ante** firm characteristics from **ex post** descriptive outcome clusters. Aggregate uncertainty at the market/replication level when market agents interact.

**Approved:** D8 four-lens reporting architecture and the separation between design and analysis layers. **Still unapproved:** operational metric formulas, welfare definitions, economic calibration, numerical parameters, learning algorithms and market equilibria.

### Next engineering milestone (technical, no new economic assumptions)

Implement a **data-only strategy registry** for approved L1–L7 catalogs and D8 analysis lenses, deterministic Cartesian-product enumeration, stable structured IDs, and compatibility/definition status fields. Unit tests should assert exactly 12,288 nominal strategy keys, four analysis lenses and 49,152 reporting keys, unique IDs, stable order and preservation of constituent layer labels. Registry generation is not an ABM simulation. Use this registry to prepare reproducible experiment metadata without treating any economic model as approved.

**References:** Varian, *Microeconomic Analysis*, 3rd ed.; Tirole, *The Theory of Industrial Organization* (1988); Acemoglu & Restrepo (2019), *Automation and New Tasks*, https://doi.org/10.1257/jep.33.2.3; Sutton & Barto, *Reinforcement Learning: An Introduction*, 2nd ed. (2018). These support the general economic and learning categories, not the specific factorial architecture.

**Implementation status at approval:** Documentation-only; registry and tests are proposed, not yet implemented.

## Verified Strategy Registry CI — Run 41658924679 (2026-11-03)

**GitHub Actions:** https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41658924679

- Commit: `cb199051b20fc5ee9a0b336b02b44d4c0d52cfdb` on `main`.
- `task-validation (3.11)`: **success**, `91 passed in 1.45s` (job 125996661992).
- `task-validation (3.12)`: **success**, `91 passed in 1.89s` (job 125996660994).
- Workflow explicitly includes `tests/test_task_layer_registry.py`.
- The registry enumerates `12,288` nominal strategy keys across L1–L7 and `49,152` scenario–analysis lens keys across D8, **without** simulating markets or economics.
- CI verifies implementation and enumeration only. Scientific specification/compatibility, parameter calibration, market equilibrium, welfare, learning and treatment effects remain unapproved or unimplemented.

**Next technical milestone:** Experiment Registry (market, base-firm, agent/clone, replication, random seed, round, strategy and analysis-lens provenance). Treat cells as experiment designs rather than concurrent firms. Preserve separate ex ante versus ex post clustering and status flags. No unapproved economic results should be generated.

## Verified Experiment Registry CI — Run 41762205634 (2026-11-04)

**Verified directly from GitHub Actions run and both job logs:** https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41762205634

- `main` commit: `84cac43089d9e2d9d079561b684d4d364fbb0119`
- Python 3.11 job `126352244505`: **success** — **95 passed in 1.50s**.
- Python 3.12 job `126352244772`: **success** — **95 passed in 1.65s**.
- Included `tests/test_task_experiment_registry.py`, which validates scenario provenance, base-firm/clone membership, market-regime consistency and cluster annotation behavior.
- The previous 91 tests increased to 95 tests in this verified run.
- **Scope boundary:** Passing unit tests validates the tested registry mechanics, not economic model assumptions, calibration, equilibrium, causal inference, learning behavior, welfare, or outcomes.
- Next technical milestone: Experiment Configuration (deterministic selection/configuration of scenario cells, market IDs, replication seeds and Monte Carlo manifests), while keeping economic parameter approval with the principal researcher and preserving the D1–D8 layer provenance.

## Verified Experiment Configuration CI — Run 41762621083 (2026-11-04)

- GitHub Actions: https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41762621083
- Verified run conclusion: **success** on `main` at commit `27e454b1dfcc9a9ce43f43e81565e964240531c5`.
- Python 3.11 (`task-validation` job `126353578605`): **100 passed in 1.71s**.
- Python 3.12 (`task-validation` job `126353578483`): **100 passed in 2.10s**.
- The workflow includes `tests/test_task_experiment_config.py` and validates deterministic manifest planning, subset filters, distinct run IDs, and reproducible seeds.
- **Interpretation:** Test success verifies implemented software behavior under the covered assertions; it is not evidence of economic equilibrium, firm optimization, AI causality, calibration, welfare, or scientific findings.
- **Next milestone:** Connect planning metadata to Experiment Registry and validate cross-layer market/population provenance, without running unsupported economic specifications.

## Verified Integrated Experiment Pipeline CI — Run 41763252598 (2026-11-04)

- GitHub Actions: https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41763252598
- Verified conclusion: **success** for `main` commit `3b97d529629034eef3ed0b9b5c4d99fdc44704c1`.
- Python 3.11 job `126355597801`: **104 passed in 1.74s**.
- Python 3.12 job `126355598013`: **104 passed in 1.57s**.
- Integrated `tests/test_task_experiment_pipeline.py`: deterministic plan-to-scenario registration, explicit mapping of clones to base firms, optional ex ante clusters with version provenance, and rejection of incomplete mappings.
- Compared to the previous verified run, coverage increased from 100 to 104 tests.
- **Scope boundary:** This validates software integration and the tested data contracts, not economic production assumptions, parameter calibration, equilibria, behavioral learning, AI treatment effects, causal identification, welfare or substantive findings.
- **Next research gate:** evaluate economic specification and compatibility of selected strategy-layer combinations before authorizing executable simulation and calibration.

## Verified Economic Specification Audit CI — Run 41763970128 (2026-11-04)

- GitHub Actions: https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41763970128
- Verified workflow: `completed`, **success** at `main` commit `5798274ef93013d74b42171faec7b4f1ebd6e0bd`.
- Python 3.11 job `126357882327`: **109 passed in 1.85s**.
- Python 3.12 job `126357882519`: **109 passed in 2.04s**.
- `tests/test_task_economic_audit.py` was included in both job logs. Five additional tests bring the previous 104 to 109.
- The data-only audit in `src/interfirm_abm/task_economic_audit.py` preserves all **12,288 nominal L1–L7 cells**, records unresolved economic specifications and flags selected cases for explicit researcher review. It does not prove incompatibility or approve any economic equations.
- The review remains **not equivalent to scientific validation**: equilibrium definitions, technology and cost parameterization, behavioral choice, AI treatment effects and welfare measurement still require economic specification and principal researcher approval.
- **Next research milestone:** draft a layer-by-layer economic decision table distinguishing existing approvals, unresolved model elements, proposed audit questions and literature-based theoretical rationale. Do not discard any nominal strategy cell or automatically declare it simulation-ready.

## Economic Decision Table — researcher approval gate (2026-11-04)

**Purpose and status:** This is a structured research-decision agenda, **not approval** of equations, parameters, equilibria or simulation results. It is derived from the previously approved D1–D8 catalog and the conservative `task_economic_audit.py` review. Preserve all **12,288 nominal L1–L7 cells**; the four D8 lenses create **49,152 potential reporting keys**, not additional simulated economies.

| Layer | Researcher-approved scope | Unresolved economic specification | Primary cross-layer concern | Status |
| --- | --- | --- | --- | --- |
| L1 — Within-task technology | Assignment, CES, Leontief, Hybrid | Formal technology for each task; task-specific productivity, substitutability and hybrid assignment; eligibility constraints | L1 × L2: distinct within-task vs across-task elasticities | Pending researcher approval |
| L2 — Cross-task aggregation | Linear, Leontief, CES | Final-output aggregator; task weights, units, essential tasks, substitution parameters | L1 × L2: no double-counting task output or confusing task activity with final output | Pending researcher approval |
| L3 — Input/cost regime | Flexible, Capacity, Adjustment, Investment | Factor prices, endowments, adjustment costs, capital accumulation, discounting and timing where relevant | L3 × L6: static vs dynamic optimization and state-dependent learning | Pending researcher approval |
| L4 — AI shock/adoption | Eligibility, Efficiency, Adoption Cost, Combined | Shock timing, treatment intensity, adoption decision and costs; separate availability from uptake | L4 × L1 × L3: feasible task automation and investment costs | Pending researcher approval |
| L5 — Market institution | Price-taking, Cournot, Price competition, Dynamic adaptive | Demand, price mechanism, rationing where needed, timing, strategic information and solution concept | L5 × L6: computed equilibrium is not identical to learning dynamics | Pending researcher approval |
| L6 — Decision/learning | Profit optimization, Trial-and-Error, Softmax, Rival imitation | Action space, observation set, objective/payoff, information precision, memory and updating rules | L6 × L5 × L3: coherent choice rules for market and capital regimes | Pending researcher approval |
| L7 — Population/market composition | Separate, Mixed, Clones, Stratified | Assignment rules, ex ante strata, clone mapping, effective agent count, demand scaling and sampling unit | L7 × L5: changes to competition and market size affect comparability | Pending researcher approval |
| D8 — Analysis lenses | Firm, Market, Welfare/Distribution, Learning/Transition | Operational metrics, denominators, baselines and missing-data treatment; welfare requires coherent demand/cost accounting | D8 reports the same runs; does not multiply economic strategies | Pending metric approval |

### Review order (workflow proposal; not a new researcher decision)

1. **Technology:** formalize L1 and L2 jointly, separating within-task production from final-output aggregation. Keep the existing 20-task data as capabilities, not as proof of a selected production equation.
2. **Feasible choice:** specify L3 and L4 input, adjustment, adoption and shock rules. Do not assume that AI availability guarantees adoption.
3. **Market and behavior:** specify L5 and L6 together, making the solution concept and learning/optimization benchmark explicit.
4. **Experimental identification:** specify L7 composition, market/replication unit and ex ante clusters before causal comparisons; separate markets, mixed markets and clone economies must not be pooled naively.
5. **Measurement:** specify D8 outcomes only where the model generates the necessary economic quantities. Do not equate profits with social welfare.

### Audit interpretation and researcher decision rights

- `task_economic_audit.py` flags selected combinations and lists required specifications. These are **review prompts**, not a proof of infeasibility, completeness or scientific validity.
- A populated specification field is not a researcher sign-off. An executable scenario requires separate explicit approval of equations, parameter values, timing, feasible actions and relevant solution concept.
- **No numerical calibration, economic outcomes, learning convergence, equilibrium, welfare or AI effect is established at this milestone.**
- Each strategy retains immutable L1–L7 identifiers and explicit unresolved status; do not drop cells to make results look complete.

### Theoretical anchors (scope, not evidence for simulated findings)

- Varian, Hal R. (1992), *Microeconomic Analysis*, 3rd edition: production, costs, optimization and market analysis.
- Acemoglu, Daron, and Pascual Restrepo (2018), “The Race between Man and Machine: Implications of Technology for Growth, Factor Shares, and Employment,” *American Economic Review*, 108(6), 1488–1542. https://doi.org/10.1257/aer.20160696
- Acemoglu, Daron, and Pascual Restrepo (2019), “Automation and New Tasks: How Technology Displaces and Reinstates Labor,” *Journal of Economic Perspectives*, 33(2), 3–30. https://doi.org/10.1257/jep.33.2.3
- Tirole, Jean (1988), *The Theory of Industrial Organization*: alternative market institutions and strategic competition.
- Sutton, Richard S., and Andrew G. Barto (2018), *Reinforcement Learning: An Introduction*, 2nd edition: trial-and-error and action-selection algorithms; methodological reference, not a claim of economic equilibrium.

**Implementation note:** This table documents research questions only. The previously verified economic-audit code and CI remain unchanged by this documentation update.

## L1 × L2 production technology — candidate equations and feasibility gate (2026-11-04)

**Research status:** Economic formulation for **discussion**, not a new approval, calibration or simulation. The researcher has approved **four L1 technology families × three L2 aggregators = 12 nominal technology cells**, but has **not approved numerical elasticities, weights, input prices, task requirements, automation rules, hybrid assignment, or a particular production equation**. The 20-task capability data remain a feasibility/accounting input, not evidence of an approved production function. Earlier aggregate CES assumptions (including `alpha=0.5` and common `A`) must **not** be carried over without explicit reinterpretation.

### Notation and distinct economic objects

For firm `i`, task `j ∈ {1,...,20}`, period `t`:

- `l_ijt >= 0`, `k_ijt >= 0`: labor and capital assigned to task `j`; `q_ijt`: task service/activity **before** aggregation; `Y_it`: **final** output.
- `a^L_ijt`, `a^K_ijt`: task-specific efficiencies; `e_ijt ∈ {0,1}`: capital/automation eligibility, when required by the selected technology.
- `q_ijt = f_j(l_ijt,k_ijt; technology, eligibility, parameters)`; `Y_it = G(q_i1t,...,q_i20t; aggregator, parameters)`. **Do not equate** a task's `q_j` with the firm's `Y`.
- A separate feasible set `sum_j l_ijt <= L_it`, `sum_j k_ijt <= K_it` applies **only** when the selected L3 regime imposes these resource endowments; other L3 regimes require their own economic definitions. No cost minimization or profit optimum follows from the equations alone.

### L1 candidate within-task technologies (NOT APPROVED EQUATIONS)

| L1 option | Candidate mathematical family | Economic interpretation / unresolved requirement |
| --- | --- | --- |
| Assignment | `q_j = a^L_j l_j` **or** `q_j = a^K_j k_j` depending on a feasible exclusive mode `m_j` | Task performed by one input type at a time; define mode-selection, eligibility, and switching cost; **not** the additive `a^L l+a^K k` convention |
| CES | `q_j = B_j [beta_j (a^L_j l_j)^rho_j + (1-beta_j)(a^K_j k_j)^rho_j]^(1/rho_j)` | Inputs potentially substitute within a task; define `beta_j`, `rho_j`, normalization, zero-input domain and capital eligibility. For the usual interior CES family, `sigma_j=1/(1-rho_j)`; this is a candidate parameterization, not an estimate |
| Leontief | `q_j = min{a^L_j l_j / b^L_j, a^K_j k_j / b^K_j}` | Both factors required in fixed proportions. If `e_j=0` forbids capital, this candidate would produce zero: a separate labor-only feasible regime or another interpretation is required; **do not silently override the contradiction** |
| Hybrid | `q_j=f_{h_j}(l_j,k_j)` where `h_j` selects an explicitly specified technology family for each task | Define whether the family assignment is fixed, firm-specific, task-specific or endogenously chosen, and whether switching incurs costs; no costless endogenous switching is assumed |

**Domain cautions:** CES needs explicit limiting cases for `rho=0` and boundary values; formula above is not universally defined at zero inputs when `rho<0`. Leontief's fixed-proportion coefficients and units must be defined. A zero-eligible-capital task cannot automatically be treated as capital-complementary.

### L2 candidate aggregation of 20 task services (NOT APPROVED EQUATIONS)

| L2 option | Candidate mathematical family | Economic meaning / pending choices |
| --- | --- | --- |
| Linear | `Y = sum_j w_j q_j` | Task services are additive substitutes; specify nonnegative weights, units, and whether a missing task can be compensated by others |
| Leontief | `Y = min_j {q_j / b_j}` | Every task is essential at a fixed recipe; define strictly positive requirements `b_j` and treatment of missing tasks |
| CES | `Y = B [sum_j w_j q_j^eta]^(1/eta)` | Imperfect task substitutability; specify weights, normalization, domain and `sigma_tasks=1/(1-eta)` where applicable. `eta` is **not** the within-task `rho_j` |

The proposed equations are **examples of families** rather than a single authorized structural model. Alternative normalizations may change scale, units, and implied marginal products. For meaningful comparisons, define what is held constant across L1 and L2 treatments (input budgets, task efficiencies, baseline output, cost environment and market demand) **before** attributing changes to technology.

### Twelve nominal L1 × L2 cells — review matrix

| L1 / L2 | Linear aggregation | Leontief aggregation | CES aggregation |
| --- | --- | --- | --- |
| Assignment | `L1=assignment|L2=linear` | `L1=assignment|L2=leontief` | `L1=assignment|L2=ces` |
| Within-task CES | `L1=ces|L2=linear` | `L1=ces|L2=leontief` | `L1=ces|L2=ces` |
| Within-task Leontief | `L1=leontief|L2=linear` | `L1=leontief|L2=leontief` | `L1=leontief|L2=ces` |
| Hybrid | `L1=hybrid|L2=linear` | `L1=hybrid|L2=leontief` | `L1=hybrid|L2=ces` |

**All twelve are retained as nominal catalog entries**, not declared executable. Each must be assessed for domain feasibility, input availability, task essentiality, identification and normalization. In particular, Leontief within-task technology plus automation-ineligible capital requires an explicit alternative regime or a formal infeasibility flag, not a fabricated positive output.

### Researcher decision gates before implementation

1. **Task technology:** Decide what labor-only, capital-only and joint-input task production mean, especially when capital is not eligible; approve whether L1 Leontief truly requires both factors.
2. **Technology parameters:** Approve productivity scales, CES shares/elasticities, Leontief coefficients, hybrid task assignments and parameter bounds; do not assume historical aggregate `alpha=0.5` applies.
3. **Aggregation:** Approve weights/requirements and final-output normalization, including whether every task is essential.
4. **Feasibility and counterfactual comparability:** Define baseline task output, factor resources/costs, zero-input handling, technology shock timing and the normalization used when comparing the twelve cells.
5. **Model verification:** Only after explicit sign-off, implement monotonicity, nonnegativity, domain, resource-feasibility, limiting-case and counterfactual tests. Do not call test success a causal result.

### Literature and theoretical scope

- Varian, Hal R. (1992), *Microeconomic Analysis*, 3rd ed.: production sets, substitutability, cost minimization and aggregation as standard microeconomic foundations.
- Acemoglu, Daron, and Pascual Restrepo (2018), “The Race between Man and Machine: Implications of Technology for Growth, Factor Shares, and Employment,” *American Economic Review*, 108(6), 1488–1542. https://doi.org/10.1257/aer.20160696
- Acemoglu, Daron, and Pascual Restrepo (2019), “Automation and New Tasks: How Technology Displaces and Reinstates Labor,” *Journal of Economic Perspectives*, 33(2), 3–30. https://doi.org/10.1257/jep.33.2.3

These references motivate microeconomic production and task-based automation; **they do not validate the specific 12-cell design or any unapproved parameterization**.

**Implementation status:** Documentation-only. No new economic production code, calibration, simulation, tests or CI workflow changes in this milestone.

## L1 × L2 technology review implementation — pending CI (2026-11-04)

- Added `src/interfirm_abm/task_technology_review.py`: enumerates the **12 nominal L1 × L2 technology cells**, records missing economic specifications, and emits conditional research-review flags for assignment, CES domains, Leontief input requirements, hybrid task mapping and cross-task aggregation.
- Added `tests/test_task_technology_review.py` with six unit tests for complete coverage, preservation of Leontief eligibility questions, distinct CES elasticities, task essentiality, researcher approval gate and input validation.
- Updated `.github/workflows/game1-task-validation.yml` to run the new tests on Python 3.11 and 3.12. Trigger commit: `cb00b897cb39bea848cc685222f129a858456802`; GitHub Actions: https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41765382612.
- **CI status at documentation time: in progress.** Do not claim tests passed until logs are checked.
- **Economic status:** data-only review; no production equations, task allocations, CES coefficients, AI eligibility interpretation, output results or equilibria have been approved or computed.
- **Next researcher gate:** resolve within-task Leontief versus automation-ineligible tasks and define the common output/parameter normalization before any numerical production comparison.

## Verified L1 × L2 Technology Review CI — Run 41765382612 (2026-11-04)

- GitHub Actions: https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41765382612
- Workflow completed successfully at `main` commit `cb00b897cb39bea848cc685222f129a858456802`.
- Python 3.11 job `126362416205`: **115 passed in 1.41s**.
- Python 3.12 job `126362415448`: **115 passed in 1.71s**.
- Both job logs explicitly include `tests/test_task_technology_review.py`; the new six tests increase the previous 109 to 115.
- Scope: the 12 nominal L1 × L2 cells are preserved and review flags cover input eligibility/Leontief requirements, distinct CES elasticity domains, hybrid assignment, and cross-task essentiality. The review does **not** calibrate production functions or prove economic feasibility, substitutability or AI effects.
- Pending researcher approval: definitions of automation-ineligible tasks under Leontief within-task technology; task/aggregate equation domains; cost and baseline normalization for comparisons.

## Production Feasibility and Normalization — alternatives for researcher decision (2026-11-04)

**Status: research alternatives only.** No choice below has been approved, implemented as a production model or simulated. The catalog remains 12 nominal L1×L2 technology cells and 12,288 nominal L1–L7 combinations.

### F1. Within-task Leontief and capital eligibility

A candidate strict two-input Leontief task is `q_j=min{aL_j L_j/bL_j, aK_j K_j/bK_j}` with positive coefficients. If eligibility prohibits all capital on task `j` and `K_j=0`, the formula implies `q_j=0`. This is a mathematical implication of essential complementary inputs, **not** an error that software should silently repair.

| Alternative | Technology interpretation | Economic consequence and open question |
| --- | --- | --- |
| F1-A: Switching technology | Before eligibility: a separate labor-only production mode; after eligibility: another technology (possibly Leontief) | Requires explicit technology switching and associated adoption/transition costs; cannot be described as unmodified strict Leontief throughout |
| F1-B: Strict two-input Leontief | Both capital and labor always essential | Some automation-ineligible tasks may be infeasible; clarify whether `eligibility` prohibits *all* capital or only *AI-enabled* capital |
| F1-C: Eligibility-dependent production set | Feasible technology set changes with task state, possibly permitting different production modes | Requires explicit state-contingent production correspondence and decision/timing rules; may overlap with L1 hybrid and L4 eligibility shock |

**Critical distinction:** Physical capital, AI-enabled capital and automation eligibility are not automatically the same concept. A task may require ordinary equipment while not being eligible for AI automation. The researcher must define the meaning of `K` and `eligibility` before choosing F1-A/B/C. None is preselected.

### F2. Comparability/normalization across technology cells

| Alternative | What is held fixed | Primary estimand or diagnostic | Limitation |
| --- | --- | --- | --- |
| F2-A: Fixed inputs | Same feasible K and L endowments and task-capability baseline | Difference in feasible output at fixed resources | Allocations and costs can differ; cannot infer profits or welfare |
| F2-B: Fixed target output | Same target final output and factor prices | Conditional cost or input requirement differences | Requires a coherent cost-minimization problem and feasibility across all cells |
| F2-C: Matched baseline calibration | Common pre-shock output or cost reference where feasible, then matched AI counterfactuals | Within-cell pre/post response conditional on calibration | May conceal structural level differences; calibration can be infeasible and must not force equality without disclosure |

**Comparability contract:** Record which parameters and endowments are common, which are technology-specific, units of task service and final output, pre-shock target, normalization method, feasibility failures, and whether market demand and firm identities are held constant. Preserve both raw and normalized outcomes; never substitute normalized output for realized production.

### Researcher approval questions

1. Does capital `K` mean **all physical capital**, **AI-capable capital only**, or separate categories? Does `eligibility=0` prohibit AI use only, or all capital use?
2. Should the strict Leontief task technology always require both inputs, or should eligibility alter the production mode/feasible set? Choose F1-A/B/C or refine them.
3. What is the primary comparison: fixed-input output (F2-A), conditional cost at fixed output (F2-B), or matched-baseline AI response (F2-C)? Multiple complementary diagnostics are possible but must be labeled separately.
4. What is the common baseline and which quantities are permitted to vary? Numerical values and normalization formulas remain pending.

### Theoretical foundations and scope

- Varian, Hal R. (1992), *Microeconomic Analysis*, 3rd ed.: production sets, Leontief complementarity, cost minimization and normalization.
- Acemoglu, Daron, and Pascual Restrepo (2018), “The Race between Man and Machine: Implications of Technology for Growth, Factor Shares, and Employment,” *American Economic Review*, 108(6), 1488–1542. https://doi.org/10.1257/aer.20160696
- Acemoglu, Daron, and Pascual Restrepo (2019), “Automation and New Tasks: How Technology Displaces and Reinstates Labor,” *Journal of Economic Perspectives*, 33(2), 3–30. https://doi.org/10.1257/jep.33.2.3

The literature supports examining task feasibility, substitution and automation; it does **not** establish that F1-A/B/C or F2-A/B/C is uniquely correct for this research design.

**Implementation:** Documentation-only. No new economic equations have been authorized for execution, and no new CI result is claimed.

## Executable Acemoglu–Restrepo-style task benchmark (2026-11-04)

**Researcher direction:** Use Acemoglu–Restrepo's task-based automation theory as the baseline and prioritize a playable/runnable Game 1 instead of repeated specification questions. `K` denotes capital (not AI itself); automation changes which tasks capital may perform. Tasks without capital eligibility can still be performed by labor. L1 CES/Leontief/Hybrid remain research extensions, **not** blockers for this baseline.

**Executable module:** `src/interfirm_abm/task_ar_benchmark.py`. Run from the installed repository root:

```bash
python -m interfirm_abm.task_ar_benchmark --output artifacts/game1_task_benchmark.csv --seed 2026
```

This creates a **200-row matched panel** (100 firms × pre/post phases) and prints aggregate output, labor, capital, cost, revenue, profit and automated-task counts. The same firm's task efficiencies and eligibility ordering persist across phases. Every task is produced by labor or, when eligible and cheaper, capital. No task becomes zero-output solely because automation is unavailable.

**Transparent illustrative closure, not calibrated economic evidence:**

- 100 firms, 20 tasks, fixed final-output target 20 per firm, equal task requirements; illustrative fixed-recipe task requirements used for a cost-comparison benchmark.
- Pre/post eligible-task shares 20%/60%; wage 1, capital rental rate 0.7, output price 1.5; deterministic seed 2026; task efficiencies sampled from documented uniform ranges. These are **example parameters** to make the game executable, **not** researcher-approved or empirically estimated values.
- Fixed output, exogenous factor/output prices, no market-clearing, no strategic competition, no investment/adoption adjustment costs and no welfare claims. Firm profit is accounting revenue minus factor costs. A lower cost when the eligible set expands is a mechanical consequence of feasible-set expansion under fixed prices and the cheapest-method rule; **not** a new empirical finding.
- All 12 L1×L2 technology families remain in the registry; the executable benchmark implements only a labor-versus-eligible-capital assignment variant. Do not call the benchmark a full implementation of all 12 technologies or 12,288 nominal strategies.

**Tests and CI:** `tests/test_task_ar_benchmark.py` adds six tests (matched panel, reproducibility, cost monotonicity under benchmark assumptions, labor-only fallback, accounting identity and parameter validation). Workflow updated at `bf12f42201d1f9a0afa185eec83b52f3a08e40be`; CI run https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41769338408 was **queued when recorded**, not yet verified successful.

**Theory:** Acemoglu & Restrepo (2018), *The Race between Man and Machine*, https://doi.org/10.1257/aer.20160696; Acemoglu & Restrepo (2019), *Automation and New Tasks*, https://doi.org/10.1257/jep.33.2.3. The implemented closure is a deliberately simplified pedagogical benchmark, not a reproduction of their full equilibrium model.

## Verified executable task-based benchmark CI — Run 41769338408 (2026-11-04)

- GitHub Actions: https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41769338408
- Verified status **completed/success** for commit `bf12f42201d1f9a0afa185eec83b52f3a08e40be` on `main`.
- Python 3.11 job `126375095555`: **121 passed in 1.87s**.
- Python 3.12 job `126375095823`: **121 passed in 1.71s**.
- Both job logs include `tests/test_task_ar_benchmark.py`; six added tests increase the verified count from 115 to 121.
- Executable simplified benchmark: `python -m interfirm_abm.task_ar_benchmark --output artifacts/game1_task_benchmark.csv` (100 firms, 20 tasks, two phases, illustrative fixed-price/fixed-output task assignment).
- These tests validate software behavior under the stated illustrative assumptions, **not** competitive market equilibrium, empirical calibration, causal effects, welfare, or full Acemoglu–Restrepo replication.
- Next implementation gate: integrate the same task technology into an explicit shared-market dynamic, keeping demand, price formation, and behavioral assumptions visible and separate from the theoretical benchmark.

## Researcher correction — population size follows strategy coverage (2026-11-04)

**Explicit researcher direction:** The original 100 firms were an early estimate, **not a permanent constraint**. As the research strategy catalog expanded, the simulation's population and experiment scope must adapt to represent the strategy catalog. Do not default new Game 1 experiments to 100 firms merely because earlier benchmarks used 100.

**Current scope:** 12,288 nominal L1–L7 strategy configurations. Use this as the **strategy coverage target**, and support an illustrative **one-agent-per-strategy roster of 12,288 agents** where the experimental market design makes that meaningful. Do **not** conflate a strategy configuration, a unique firm, an agent, a market or a Monte Carlo replication.

**Important qualification:** L7 itself encodes market-composition regimes (separate, mixed, clones, stratified). A one-agent-per-strategy roster is a catalog-level assignment proposal, **not** a claim that all 12,288 strategies can be placed simultaneously in one economically coherent market. A scenario must explicitly define market membership, compatible strategies, agent counts and the treatment of L7; the population may differ by regime and experiment.

**Engineering implications:**
- Remove fixed `100` assumptions from the default *research-scale experiment orchestration* and make population size/assignment configurable.
- Retain the previously verified 100-firm benchmark as a **small smoke test / pedagogical benchmark**, not the canonical research population.
- Preserve complete strategy coverage and report which cells are executable, unresolved or intentionally excluded from a particular run; do not silently pretend all 12,288 are economically executable.
- Keep task counts, baseline conditions, random seeds and market identities explicit, and report computational scale before launching large experiments.
- No new production, market, welfare or learning assumptions are approved by this population-size correction.

**Next implementation priority:** connect strategy IDs to agent rosters and market assignments through the existing experiment registry/pipeline; validate full 12,288-strategy coverage independently of economic execution.

## Game 1 architecture decision — strategies as players, 200-round common market (2026-11-04)

**Explicit researcher decision (supersedes prior fixed-firm/population framing):**

1. **Strategies are market players.** The strategy catalog provides player identities rather than merely assigning strategies to a preselected 100 firms. The earlier 100-firm profiles become **candidate initial-configuration inputs**, not a fixed number of firms/players.
2. **One common market per initial configuration.** All selected strategy-players participate in the **same market** and interact through the same market environment, not separate markets per strategy.
3. **Exactly 200 rounds per configuration.** Players repeatedly choose actions, produce/compete and obtain payoffs. At the end, rank players by realized benefit; the exact benefit functional (terminal profit, cumulative profit, discounted payoff or other utility) must be declared before reporting a winner.
4. **Sequential configurations.** Finish and record the 200-round market for initial configuration A; reset to the declared baseline and run configuration B, then C, etc. Track configuration ID, seed, player ID, round, economic model version, market results and ranking.
5. **Researcher-approved concept is not yet implemented as a full market simulation.** The 100-firm benchmark remains a technical smoke test only; it must not be presented as the new Game 1.

### Important catalog-level consistency issue

The current catalog contains **12,288 nominal L1–L7 combinations**, but L7 (`separate`, `mixed`, `clones`, `stratified`) was originally a **market-composition regime**, not a firm decision policy. Treating every nominal combination as a distinct simultaneous market player would duplicate each L1–L6 policy across four incompatible market-level labels. **Do not silently resolve this by treating L7 as firm behavior.** For implementation, preserve all 12,288 registry IDs and flag the player-identity projection as needing reconciliation: L1–L6 yield **3,072 distinct strategy policies**, while L7 must be assigned a coherent role in the new single-common-market architecture. This is a mathematical interpretation issue, not a request to revert to 100 firms.

### Executable game contract (implementation target, not claimed done)

- Outer loop: initial configuration `c` (from the former 100-firm initial profiles, with explicit configuration selection).
- Market setup: instantiate all economically coherent strategy-players and shared demand/price/factor environment for configuration `c`.
- Inner loop: `t = 1..200`; collect each player's action and feasible production; clear or update shared market under an explicitly recorded rule; compute and persist individual payoff and common market state; update learning/technology state.
- End of run: compute declared 200-round benefit metric, rank all players, report winner, ties, distributions and market-level outcomes; save machine-readable panel.
- Next configuration: reset or reseed as explicitly defined; never leak end states from one configuration into another unless the experiment intentionally studies carryover.
- A testable **simulation scaffold** may be built before all economic mechanisms are approved, but its outputs must be labeled illustrative and cannot claim valid equilibrium or scientific findings.

**Theoretical orientation:** Acemoglu & Restrepo (2018), https://doi.org/10.1257/aer.20160696, for task-based production and automation; Varian, *Microeconomic Analysis*, for firm choices; Tirole (1988), *The Theory of Industrial Organization*, for shared-market strategic interaction. These references do not establish the chosen 200-round experimental design.

## Implementation milestone — 200-round strategy-player shared-market scaffold (2026-11-04)

**Code:** `src/interfirm_abm/task_shared_market_game.py`, tests `tests/test_task_shared_market_game.py`, CI `.github/workflows/game1-task-validation.yml`.

**Run:**
```bash
python -m interfirm_abm.task_shared_market_game --configurations 1 --rounds 200 --output-dir artifacts/game1_shared_market
```

The runner enumerates **3,072 distinct L1–L6 strategy IDs** from the existing **12,288 L1–L7 registry**; L7 is not treated as a player's economic action. One configuration creates one shared-market panel with 3,072 players × 200 rounds = **614,400 player-round records**, plus 3,072 ranking rows. The `--configurations N` option executes N initial configurations sequentially, each starting afresh, with separate IDs and ranked outcomes. CSV outputs: `rounds.csv`, `ranking.csv`. For the 100 legacy initial configurations, these can eventually be supplied as scenario parameters, but the current CLI uses generated illustrative configurations and does **not** claim to import the original 100 firm profiles.

**Crucial limitation:** This milestone is a **software scaffold only**. It deliberately uses the **same fixed-quantity policy for every player**, a shared illustrative inverse-demand price, and a deterministic hash-derived proxy unit cost. L1–L6 labels are **not yet executed as distinct economic policies**. Thus any winner is an **arbitrary fixture ranking**, not a meaningful strategic/economic result. Output carries `execution_status=proxy_only_not_economic_strategy_execution`. Do not publish or interpret rankings as scientific findings, welfare results, equilibria or evidence of strategy superiority.

**Next gate:** implement actual task-based feasible production and heterogeneous strategy decisions within a common-market round, beginning with an explicitly defined economically coherent subset. Preserve unimplemented strategies in the roster with transparent execution-status metadata rather than silently assigning fake economics to them. Validate shared market clearing, payoff accounting and round-to-round state before interpreting any ranking.

**CI:** Workflow run https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41774802062 was queued when first checked; do not claim success without later verification.

## CI verification — 200-round shared-market scaffold (2026-11-04)

- GitHub Actions run: https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41774802062
- Status: **completed/success**; commit `99a658f2aa0502593a54e2e83733e8356b98b108`.
- Python 3.11 job `126392553567`: **126 passed in 2.37s**.
- Python 3.12 job `126392553322`: **126 passed in 3.10s**.
- Both logs include `tests/test_task_shared_market_game.py`; the test count grew from 121 to 126.
- This validates the software scaffold and declared proxy fixtures. The shared market is not yet a validated execution of heterogeneous L1-L6 economic strategies, a task-based equilibrium, or an evidence-backed ranking of optimal policies.


## Game 1 task aggregation implementation checkpoint — 2026-11-05

Following the researcher's clarification that the 20 tasks jointly contribute to final production, and instruction to continue after discussing Cobb–Douglas across tasks, the **diagnostic Game 1** now uses an equal-share, 20-task Cobb–Douglas aggregator:

`Y_i = exp((1/20) * sum_{j=1}^{20} log(q_ij))` for all strictly positive task activities, and `Y_i = 0` if any task activity is zero.

This is the `sigma=1` case of the existing task CES implementation in `src/interfirm_abm/task_aggregators.py`. It is applied consistently to **both** the action valuation and realized production in `src/interfirm_abm/task_multi_action_diagnostic.py`. The 100 approved firm-specific task productivity vectors and automation eligibility masks remain unchanged. Task shares `1/20` are a **baseline modeling assumption**, not parameters identified from the population CSVs. Alternative CES elasticities and task shares remain sensitivity analyses, not observed data.

**Scientific caveat:** The within-task additive `a_L L + a_K K` activity convention, allocation plans, demand/clearing, input prices, and behavioral valuation are still diagnostic and have not been approved as a complete economic model. This checkpoint does not change the global `research_validated: false` gate. No inference about equilibrium, welfare or AI effects is authorized by the simulation.



## Researcher decision: Acemoglu–Restrepo task execution — 2026-11-05

The principal researcher explicitly instructed us to discard the old within-task additive K+L production function and use the Acemoglu–Restrepo task-based foundation. The Game 1 task feasibility implementation now **rejects simultaneous positive K and L within the same task**. An ineligible task is labor-only; an eligible task may be carried out with labor-only `q=a_L L` or capital-only `q=a_K K`. A firm can still use both factors across different tasks. Diagnostic candidate plans were updated to obey this constraint.

The 20-task equal-weight Cobb–Douglas final-output aggregator remains separate. The existing 100-firm productivity and eligibility CSVs are unchanged.

**Scope and theory:** Pure-mode execution is a discrete implementation of task assignment by comparative cost, inspired by Acemoglu–Restrepo. It is not a claim to reproduce every assumption or equilibrium result of their continuous-task models. In particular, cost-minimizing task assignment under shared factor endowments, endogenous factor prices, automation-frontier changes, adoption costs, and labor-market equilibrium remain unresolved. The diagnostic market is not yet scientifically validated; `research_validated: false` remains mandatory.


## Strategy-generated decisions (diagnostic implementation, 2026-11-05)

The previous fixed action catalog (`labor_low`, `labor_high`, `capital_low`, `capital_high`, `balanced`) has been removed from the diagnostic runner. Each player now builds four *feasible, strategy-specific* task allocations using `task_strategy_actions.build_actions`. The four shared identifiers `effort_0..effort_3` represent comparable effort slots for lagged imitation; **the allocations behind those IDs can differ between players**. Therefore imitation currently copies an effort index, **not an exact rival's 20-task plan**.

- **L3 flexible:** equal task emphasis with candidate-specific eligible mode switching; **capacity:** prioritize tasks with higher available productivity; **adjustment:** vary task emphasis and mode using the length of own realized history; **investment:** prioritize capital-capable tasks and increase capital emphasis in higher-effort candidates. Investment is a **resource-allocation orientation**, not yet persistent capital accumulation.
- **L4 eligibility:** capital on all eligible tasks; **efficiency:** capital where capital productivity exceeds labor productivity; **adoption_cost:** capital only when productivity exceeds a diagnostic 1.25x hurdle; **combined:** uses a 1.10x diagnostic hurdle. These hurdles are *illustrative and not empirically calibrated*, not actual fixed adoption costs.
- **L5 competitive:** score output at lagged observed market price; **cournot:** apply an illustrative own-output price-impact term (0.01 per unit), **not** a solved Cournot equilibrium; **price:** submit candidate-specific reserve prices; **adaptive:** rank previously tried actions using own realized payoffs, with provisional valuations for untried actions.
- **L6 optimization:** highest *estimated* candidate score, not global optimum; **trial_error:** epsilon exploration; **softmax:** stochastic score-weighted choice; **imitation:** copy the highest lagged-payoff peer's *available action ID*; the previously approved Adaptive × Imitation tie-break remains.

All candidates obey Acemoglu–Restrepo-inspired task-level pure modes and firm-wide K/L endowments. The current effort fractions, hurdles, price expectations and market response remain diagnostic, **not researcher-approved economic parameters**. There is no endogenous investment stock, true adoption-cost accounting, solved Cournot best response, or complete strategy-specific information structure yet. `research_validated: false` must remain unchanged. The diagnostic run must not be described as scientific validation.


## A1–A6 economic audit — GitHub Actions #42051340277 (2026-11-06)

**Audit scope:** 100 configurations × 200 market rounds; 5,120,000 player-round observations. All numbers below were calculated from the workflow artifact `game1-100-configurations-200-rounds-diagnostic` (ID 13429476261). **No economic parameters, behavior rules, or production functions were changed.** This audit does not validate the economic model.

| Gate | Status | Verified finding | Research question / required follow-up |
| --- | --- | --- | --- |
| A1 — Persistent losses | Diagnosed, not resolved | Across 20,000 market rounds: mean revenue 3,095.0191; mean cost 8,688.2824; mean profit −5,593.2633; **0 rounds with positive aggregate profit**. Ratio of aggregate costs to aggregate quantity sold is **27.1742**, versus mean observed transaction price **10.1785**. | Determine whether negative payoffs are economically plausible given a coherent technology, prices and outside option. Do not tune prices/costs to force positive profit. |
| A2 — Price expectations | Mechanism mismatch identified | `score_action` defaults to price **2.0** before any observed transaction. Thereafter competitive/adaptive use the lagged market average; Cournot subtracts `0.01 × own_output`. Price strategy scores offers at reserve prices **1.5, 2.0, 2.5, 3.0** although realized sales use the market price. | Specify information/belief formation and separate reservation price from expected realized sale price. |
| A3 — Units | Not established | Canonical firm K/L stocks and task productivity coefficients have no validated common units with the demand intercept, output price or costs. | Specify physical units, accounting period, output units, capital services vs stock, and wages/rental rates. |
| A4 — Input costs | Explicit diagnostic assumption | `MixedMarket` is instantiated with `capital_unit_cost=1.`, `labor_unit_cost=1.`, and `extra_cost=lambda ...: 0.`; action valuation likewise computes `sum(K+L)`. | Determine economic meaning of endowments and opportunity cost of capital/labor; separately define adoption and investment costs before using those labels substantively. |
| A5 — 20-task production | Mathematical choice documented; economic choice pending | Each task is pure labor or eligible capital; task activity uses `a_L L + a_K K` on a feasible pure-mode allocation. Final output is the equal-weight 20-task CES geometric mean (`sigma=1`). Thus output is sensitive to low-activity tasks and has the same units as a task activity only under compatible normalization. | Establish task definitions, aggregation normalization and whether each task is essential. Do **not** claim this is the full Acemoglu–Restrepo production/general-equilibrium framework. |
| A6 — Demand and market clearing | Mechanical identity verified; economics pending | For all 20,000 market rounds, total quantity sold equals total quantity produced within numerical precision. Diagnostic clearing uses `P=max(0,(a-Q)/b)` with configuration-specific `a,b`, then reserve-price eligibility and proportional rationing. Observed prices range **6.5705–13.4677**, exceeding all currently offered reserve prices (maximum **3.0**), so the price strategy's bids do not constrain any sale in this run. | Decide whether firms are price takers, Cournot quantity setters, or price setters; define how offered prices influence actual transactions and how demand responds. |

**Interpretation:** A1 is an accounting consequence of the current joint assumptions, not a software arithmetic error. A2 and A6 contain a concrete mismatch between *valued* price offers and *realized* prices. A3–A5 are under-specified research choices. Since quantity sold equals quantity produced and every market round loses money, the candidate-set and technology/price/cost scaling need economic scrutiny before any ranking is interpreted causally.

**Next research checkpoint:** Write a dimensional analysis (task activity → output → price × quantity → cost) and an information-timing table (observed at decision time vs learned after clearing), then test counterfactual assumptions in **separately labeled scenarios** only after approval. Keep `research_validated: false`.


## Nine-strategy implementation checkpoint (2026-11-07)

Researcher-approved economic design: L3 = uniform, productivity-based, cost-adjusted; L4 = no automation, cost-based, profit-based (3 × 3 = 9 players). Shared action-value epsilon-greedy learning chooses shutdown or one of four budget caps (0.30, 0.48, 0.66, 0.84). The four caps are inherited provisional experimental settings, not empirically calibrated. Profit-based automation uses deterministic T01–T20 single-task flips, repeatedly accepting strict predicted-profit improvements, with L3 reallocation after each trial. Technology eligibility is fixed by the configuration. AI adoption fee is one-time per task; per-task changes in K and L determine adjustment costs. Price forecast uses last observed common price, starting at reference 1. All players receive the same realized inverse-demand market price and update exactly one chosen Q-value per round. Task mode persists through shutdown.

Implementation checkpoint: `src/interfirm_abm/game1_nine_strategy.py` contains a new experimental runner; `tests/test_game1_nine_strategy.py` adds focused tests; `.github/workflows/game1-nine-strategy.yml` provides a dedicated CI job. The old A6/256-player runner is retained for historical compatibility and is NOT the nine-strategy implementation. The new runner uses SciPy SLSQP for L3 optimization and explicitly raises on solver failure. Numerical convergence, economic distinguishability of all nine strategies, multi-seed robustness, 100-profile full sample, and GitHub CI success have NOT yet been verified. In particular, cost-based and profit-based divergence requires a feasible counterexample from the actual 20-task CES model.

**Research status: `research_validated: false`. Do not claim Game 1 complete until CI and economic validation pass.**

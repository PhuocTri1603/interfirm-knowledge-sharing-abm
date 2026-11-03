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

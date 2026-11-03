# Game 1 — Task-level production theory review

**Status:** Analytical review; **no theoretical choice approved**  
**Scope:** Milestone 5, Economic Model Validation  
**Authority:** [Theoretical charter](../../theoretical_charter.md)

## 1. The modeling question

For firm `i` and task `j`, distinguish (i) the set of technically feasible input bundles, (ii) task output, (iii) aggregation into final output, (iv) prices/costs, and (v) behavior under imperfect information. A firm's capital/labor intensity `K/L` is an outcome of feasible technologies, prices, resources, and decisions; it must not be programmed to rise following an AI shock.

The approved synthetic population has 100 firms with 20 tasks each. Its `automation_eligible` flag indicates a potential capital execution mode, **not** an adoption decision or a time-indexed AI shock.

## 2. Three candidate within-task representations

### A. Exclusive task assignment (pure modes)

`q_ij = aL_ij * L_ij` if assigned to labor; `q_ij = aK_ij * K_ij` if assigned to capital and eligible.

- Economic meaning: a task is assigned to one execution mode; a firm can reallocate tasks when technology makes capital feasible.
- Strength: transparent task-level displacement mechanism and unit-cost comparison.
- Limitation: cannot describe simultaneous capital–labor complementarity *within* one task.
- Implementation: `task_execution.py` already provides hypothetical pure-mode quotations; this is **not** approved as the final technology.

### B. Linear within-task substitution

`q_ij = aL_ij * L_ij + aK_ij * K_ij` where capital is allowed.

- Economic meaning: capital and labor are perfect substitutes in *task activity units* when both are feasible.
- Strength: supports mixed allocation and simple linear feasibility.
- Limitation: perfect substitution is a strong economic assumption; it can erase complementarity and create corner solutions.
- Implementation: `task_based_firm.py` uses this as **provisional accounting only**.

### C. Within-task CES

`q_ij = [alpha_ij * (aL_ij L_ij)^rho + (1-alpha_ij) * (aK_ij K_ij)^rho]^(1/rho)` for eligible tasks, with the limiting log form for `rho = 0`.

- Economic meaning: finite substitution elasticity between labor and capital *within a task*.
- Strength: allows imperfect substitution.
- Limitation: adds an unidentified elasticity and share parameter; task eligibility and zero-input cases require careful definitions. Not implied by the existing synthetic data.
- Implementation: **not implemented** as an approved model.

These are **alternative hypotheses about technology**, not an exhaustive list of feasible production sets.

## 3. Separate task aggregation from within-task technology

Possible across-task aggregation includes Leontief, weighted linear, or CES. These represent different requirements for joint task completion. A CES elasticity **across tasks** must not be interpreted as the elasticity of capital–labor substitution **within tasks**. Existing `task_aggregators.py` exposes computational alternatives; none is yet selected for scientific runs.

## 4. Economic interpretation of an AI shock

A defensible task-based shock can expand the set of tasks eligible for capital execution, change task-specific capital productivity, or change capital execution cost. These are **distinct treatments** and should not be conflated. In particular, simply switching an existing `automation_eligible` flag from 0 to 1 requires a defined pre/post timing rule and researcher approval.

No automatic adoption, profit improvement, labor displacement, or change in equilibrium is assumed. The effect depends on relative factor prices, resource endowments, task bottlenecks, costs of adopting/adjusting, and firms' information.

## 5. Questions requiring researcher approval before scientific simulation

1. Are tasks exclusive assignments to labor or capital, or can both inputs be used simultaneously within one task?
2. Which across-task aggregator best represents the economic production process and why?
3. Is capital endowment a fixed capacity, a rented input flow, or a stock that can be expanded? How is labor endowment interpreted?
4. What is the first AI treatment: expanded eligibility, improved capital task productivity, or reduced capital cost?
5. Are firms fully informed optimizers in Game 1, or do they experiment with limited information? The latter must be defined without borrowing Game 2 learning mechanisms implicitly.

## 6. Literature anchors and limits

- Acemoglu, D. & Restrepo, P. (2018). *The Race between Man and Machine: Implications of Technology for Growth, Factor Shares, and Employment*. **American Economic Review**, 108(6), 1488–1542. Task assignment and automation motivate the distinction between human and machine execution.
- Acemoglu, D. & Restrepo, P. (2019). *Automation and New Tasks: How Technology Displaces and Reinstates Labor*. **Journal of Economic Perspectives**, 33(2), 3–30. Automation and new task creation are distinct mechanisms.
- Varian, H. R. (1992). *Microeconomic Analysis*, 3rd ed. W. W. Norton. Production sets, feasible input choices, costs, and profit maximization provide the general microeconomic frame.

**Scope of support:** These works motivate task-based technology and microeconomic modeling; they do not identify the synthetic firms' task parameters, approve any of the three functional forms above, or validate simulation outcomes.

## 7. Governance decision

**No production function, task aggregator, AI shock, or behavioral rule is approved by this review.** Keep the charter and canonical data unchanged. The next research step is to resolve the technology representation before treating any simulation as an economic experiment.

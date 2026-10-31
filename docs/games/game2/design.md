# Game 2 — Competitive Learning: Research Design

> Status: DRAFT FOR RESEARCH REVIEW (2026-10-31). No Game 2 simulation, statistical result, or test is claimed. Game 1 baseline remains frozen and accepted with documented limitations.

## 1. Objective and boundary

**Research question:** Holding production technologies, budgets, experimental opportunities and random conditions constant, does access to publicly observable competitor performance improve a firm's learning efficiency relative to independent learning?

Game 2 introduces **observation of competitors**, not voluntary private knowledge sharing (Game 3). Market-price competition, endogenous AI investment and profit optimization are **not implemented in the accepted Game 1**; their inclusion in Game 2 is an unresolved scope decision, not an implicit assumption.

## 2. Baseline inherited from Game 1

- Four production functions: Cobb-Douglas, Leontief, Linear and CES; retain their existing parameters and feasible allocation range.
- The validated 100-firm matched-seed protocol and 50/100/200-round horizons remain the comparison benchmark.
- Each firm has a fixed budget and experiments with one candidate allocation per round; accept only strictly improved output.
- Game 1 Random and Guided policies must be retained as controls, without changing their implementations.

## 3. Information regimes (proposed, not yet approved)

**Control C0 — Independent:** each firm observes only its own history, exactly as Game 1.

**Treatment T1 — Public outcome observation:** firms see the previous round's public performance of other firms, with no access to rivals' private failed experiments or search algorithm internals. Exact public fields and whether capital/labor allocation is visible are decisions to resolve *before* implementation.

**Treatment T2 — Selective attention (optional extension):** firms choose which rival(s) to observe subject to the same information budget. Do not implement until a selection rule and observation costs are specified.

## 4. Mechanism and identification

An information treatment alone is not sufficient: specify an explicit decision rule mapping observed competitor data into the next candidate allocation. Separate (a) observing performance, (b) identifying an informative comparator, and (c) translating observed information into a candidate. Avoid treating the competitor's allocation as transferable without considering differences in production technology.

Use lagged public information (round t-1) to avoid contemporaneous leakage. Fix the same initial firm states, technologies, candidate opportunity counts and random schedules across control and treatment. If an extra competitor-inspired candidate is allowed, the control must receive the same number of candidate evaluations; otherwise the estimated treatment effect is confounded with experimentation intensity.

Primary estimand (per seed): difference in mean output efficiency at horizon H between treatment and matched control, averaged across independent seeds. Report seed-level paired 95% confidence intervals; firms within a seed are not independent replications.

## 5. Outcomes and diagnostics

- Primary: mean output efficiency at rounds 20, 50, 100 and 200.
- Secondary: time to 99% and 99.9% efficiency; acceptance rate; allocation distance to the technology-specific constrained optimum.
- Heterogeneity: treatment effect separately for Cobb-Douglas, Leontief, Linear and CES.
- Mechanism diagnostics: who observes whom; technology match/mismatch; how often observed information changes a proposed allocation; share of adopted competitor-inspired candidates.
- Guardrails: no use of future information, no changes to baseline economic equations, no fabricated observations or empirical generalization.

## 6. Hypotheses for testing (not established findings)

- H2.1: Competitor observation can improve output efficiency compared with matched independent learning when public signals contain transferable information.
- H2.2: The effect varies across production technologies and information-transfer rules.
- H2.3: Observation can be neutral or harmful when competitor information is irrelevant or misleading.

These hypotheses are provisional; no expected sign is imposed as a result.

## 7. Decisions required before coding

1. **Scope:** Is Game 2 limited to observational learning under the Game 1 output objective, or does it also introduce product-market competition and profit? The existing experimental_design.md describes the former.
2. **Public signal:** observe output alone, efficiency ranking, capital share, or some combination? Observing output alone cannot directly identify the rival's allocation.
3. **Comparator set:** same technology only, all firms, or a limited subset?
4. **Behavioral rule:** imitation, noisy imitation, guided search centered on observed allocation, or probabilistic mixture?
5. **Information budget:** how many competitors can be inspected per round, and whether inspection has cost?
6. **Timing:** update synchronously from t-1 snapshots or sequentially; default recommendation is lagged snapshots.
7. **Comparisons:** which Game 1 policy is the primary matched control (Random or Guided)?

## 8. Implementation gates

- Gate A: approve scope, public signals and behavioral mechanism.
- Gate B: formalize state variables, decision timing, treatment assignment and estimands.
- Gate C: add Game 2 code separately from Game 1 baseline; deterministic tests for information boundaries, budget equality and paired randomization.
- Gate D: pilot experiments, then multi-seed simulation and independent audits.
- Gate E: document findings and limitations in this same canonical file; only then consider a research visualization.

## 9. Source of design

Based on docs/proposals/experimental_design.md and docs/games/game1/research.md in branch experiment/game1-100-firms. This file distinguishes inherited project specifications from newly proposed design choices.
# Game 1 — Economic Foundations and Reconstruction Plan

**Status:** Theoretical reconstruction; economic assumptions pending researcher approval.  
**Authority:** [Theoretical Charter](../theoretical_charter.md)  
**Scope:** Game 1 only. Preserve existing algorithmic validation as historical technical work.

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

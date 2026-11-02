# Theoretical Charter — Interfirm Knowledge Sharing ABM

**Status:** Foundational research charter (v1.0)  
**Disciplinary orientation:** Economics  
**Scope:** Governs Games 1–3, future hypotheses, model assumptions, simulations, and research proposals.

## 1. Central research purpose

Investigate **when, why, and how voluntary cooperation emerges, persists, or collapses among competing firms pursuing their own economic interests**, with heterogeneous technologies and capabilities, especially under technological change associated with AI.

Cooperation must be an **endogenous outcome** of agents' decisions—not an outcome programmed into the model. The model must allow cooperation, non-cooperation, and the breakdown of cooperation.

## 2. Theoretical foundations

### Hal R. Varian — Microeconomic theory

Ground the firm and market environment in production technology, production possibility sets, feasible input combinations, resource constraints, costs, profits, and economically motivated choices. The simulation architecture should be extensible to a broad range of technologies permitted by production theory, rather than permanently restricted to Cobb–Douglas, Leontief, Linear, and CES.

A finite catalog of production functions must not be presented as exhaustive of all technologies allowed by general production-set theory. Distinguish production representations, technology properties, and behavioral assumptions.

### Robert Axelrod — Evolution of cooperation

Study how repeated interactions between self-interested agents can generate, sustain, or undermine cooperation. Axelrod's repeated-game framework is a theoretical inspiration, not a mandate to hard-code Tit for Tat or assume that cooperation is universally beneficial.

## 3. Three connected games

**Game 1 — Production and economic decisions.** Build a market of approximately 100 heterogeneous firms. Model feasible technologies, resource allocation, economic decisions, and outcomes before and after an AI-related technological change. Establish a sound economic baseline rather than treating algorithmic optimization diagnostics as final economic findings.

**Game 2 — Competition and learning.** Introduce economic interaction, market information, rival observation, experimentation, and strategic responses. Learning rules must correspond to defensible information and incentive assumptions, not merely parameter adjustments.

**Game 3 — Endogenous cooperation.** Allow firms to decide whether to share knowledge, with whom, under what costs and anticipated benefits, and whether to continue relationships. Study emergent cooperation networks and their effects on firm outcomes and market welfare without presupposing positive effects.

The three games are successive layers of **one research program**, not three disconnected algorithmic demonstrations.

## 4. Non-negotiable modeling principles

1. **Economics first.** Agent-based modeling and algorithms are research instruments, not the central contribution.
2. **No predetermined cooperation.** Do not encode mechanisms to guarantee the desired research conclusion.
3. **Economic foundations for behavior.** Decisions must be justified by incentives, information, opportunity costs, payoffs, and constraints.
4. **Theory-led scope.** Add a mechanism only when it addresses an explicit theoretical question or identified deficiency; avoid complexity for its own sake.
5. **Separate technical validation from scientific evidence.** Successful code execution, convergence, and algorithm comparisons are not automatically economic discoveries.
6. **Consistency across games.** Preserve and document baseline assumptions when extending the environment.
7. **Honest inference.** Simulation results are conditional on assumptions and are not automatically empirical evidence.
8. **No unapproved theoretical redirection.** Material changes to this charter require explicit researcher approval.

## 5. Mandatory review of future ideas

Before proposing or implementing a new model feature, experiment, algorithm, or hypothesis, answer:

1. Which part of this charter does it serve?
2. What economic theory or mechanism justifies it?
3. Is it necessary for the research question, or merely added complexity?
4. Could it implicitly predetermine cooperation or other desired outcomes?

If these questions cannot be answered, defer implementation and identify the unresolved theoretical issue.

## 6. Research governance

The researcher owns research questions, theoretical commitments, approval of assumptions, interpretation, and conclusions. The assistant supports literature examination, economic critique, mathematical consistency, implementation, tests, and documentation, while checking each change against this charter.

This document is the canonical theoretical charter. Update this file in place after explicit approval; use Git history rather than creating version-suffixed copies.

**Guiding statement:** Build an economic environment to discover **whether and when cooperation emerges**, not an environment engineered to ensure that it does.

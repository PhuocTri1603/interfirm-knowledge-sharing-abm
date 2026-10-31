---
name: research-documentation
description: Maintain canonical, source-aligned ABM research documentation with traceable assumptions, methodology, results and decision history.
---
# Research Documentation

## When to use
When writing or revising methods, research notes, model setup, results, interpretation, or project status.

## Procedure
1. Identify canonical file for each topic. For Game 1 use `docs/games/game1/research.md`; verified horizon report is `docs/games/game1/horizon_100_firms_results.md`.
2. Read current source and relevant P0 skills; distinguish **implemented default**, **experiment-specific override**, **researcher decision**, **planned extension** and **observed result**.
3. Describe initial firm construction, technology assignment, parameter values, feasible sets, information, decisions, state transitions and stopping rules with source references.
4. Keep a glossary and notation table; define units, indexes and percentages. Reconcile equations with Python functions and tests.
5. Cite experiment configuration, source revision, exact run/artifact and data analysis method for each result. Link evidence rather than duplicating unverified numbers.
6. Explain limitations and threats to validity; never conflate Game 1 independent learning with market competition, AI investment or knowledge sharing.
7. Update the canonical document in place. Preserve historical decisions; record changes and unresolved conflicts. Do not create competing draft/final copies without reason.
8. Review links, formatting, equations and source paths; request approval for changes that imply new economic assumptions.

## Output
Updated canonical document with scope, methods, evidence, limitations, provenance and change summary.

## Acceptance
A reader can trace each mechanism to code and each result to data; no contradictory defaults or unsupported features.

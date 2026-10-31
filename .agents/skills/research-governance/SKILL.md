---
name: research-governance
description: Protect approved research decisions, track model scope, resolve documentation conflicts, and require approval for changes to economic mechanisms.
---
# Research Governance

## Trigger
Use before any model, experiment, interpretation, documentation or roadmap change, and whenever sources conflict.

## Procedure
1. Identify the active branch, commit, target game, canonical documents and code sources.
2. Build a decision ledger: **confirmed by researcher / implemented in code / documented only / proposed / unresolved**. Never silently promote one category into another.
3. Compare requested action against established model decisions. Flag changes to firm count and composition, production technology, parameters, capital/labor budget, learning policy, acceptance, random streams, information sets, outcome definitions and experimental horizons.
4. For a change of economic meaning, present rationale, alternatives, predicted effects, migration/test plan and obtain explicit approval **before editing**.
5. For documentation-only corrections, preserve historical defaults and separately describe experiment-specific configurations.
6. Update the canonical document in place where possible. Record changed files, commit, verification status and unresolved questions.

## Guardrails
- Game 1: independent experimentation; firms choose K/L allocation under a budget and accept output improvements. No implemented profit optimization, AI investment decision, market competition or knowledge exchange in the Game 1 baseline.
- `Simulation` default 20 firms/50 rounds is not the 100-firm validation experiment.
- Do not present a Hicks-neutral productivity shock as automatically changing the theoretical optimal K/L mix.
- No claim of publication readiness from CI success alone.

## Completion
A change log clearly separates decisions, observations, assumptions and pending approvals. No unapproved mechanism change.

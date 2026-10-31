---
name: model-specification
description: Reverse-engineer and document ABM equations, firm initialization, parameters, decision rules and state transitions from the implemented Python code.
---
# Model Specification

## Trigger
Use for methods documentation, firm construction, equation changes, visualization semantics, or any disagreement between prose and code.

## Source inspection order
1. `src/interfirm_abm/simulation.py` (agent creation, technology assignment, seed, rounds, policy).
2. `src/interfirm_abm/firm.py` (initial state, budget, output, experiment, acceptance).
3. `src/interfirm_abm/production.py` and `production_optimum.py` (functions, parameter defaults, constrained optimum).
4. `src/interfirm_abm/learning.py` and `random_schedule.py` (candidate generation and matching).
5. Experiment scripts and metadata (override defaults); tests and canonical `docs/games/game1/research.md`.

## Required specification
- Agent index, number, type assignment, homogeneity/heterogeneity, initial capital share, budget, state, observed information.
- Explicit production functions with exact parameters from code; document units and feasible domain. Current defaults: Cobb-Douglas alpha=.7; Leontief kappa=.7; Linear alpha=.7; CES alpha=.7, rho=-.5.
- `K=B*s`, `L=B*(1-s)`, with initial `B=100`, `s=.5`; distinguish evolving allocation from fixed budget.
- Candidate share in [.05,.95]; Random uniform exploration; Guided global exploration probability .20 or local search around best observed candidate with normal radius .10, clipped to feasible bounds. Verify exact branch behavior and matched-randomness before publishing.
- Candidate output, strict improvement acceptance, state update, recorded trajectory, terminal outcomes.
- Separate *default* 20-firm/50-round settings from 100-firm, 100-seed horizon experiment. Explain cyclic technology assignment yields 25 of each at n=100.
- Clarify optimum is constrained to feasible share [.05,.95]; Linear optimum is a constrained boundary, not unconstrained 1.0.

## Verification matrix
For each equation, parameter or narrative claim, record code path/function, corresponding test, source revision, and whether observed in exported data. Mark unsupported statements as **unverified** rather than inventing.

## Completion
A reader can reconstruct one agent and one round from the documentation, and every specified mechanism maps to current source. No economic code changes.

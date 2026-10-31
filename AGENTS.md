# Research Agent Instructions

Scope: this repository is a research ABM, not a general application. Read this file before research, coding, documentation, experiment or GitHub tasks.

## Non-negotiable rules
1. **Do not change economic mechanisms without explicit researcher approval.** This includes production functions/parameters, agent initialization, budgets, decision/acceptance rules, information sets, random scheduling, treatments, metrics and time horizons. Propose changes separately, with motivation and anticipated consequences.
2. **Inspect actual source and branch before making claims.** Distinguish implemented behavior, historical documentation, proposed extensions and verified results. Never infer an implemented feature from README aspirations.
3. **Keep research provenance.** Identify branch, commit, configuration, seeds, software environment, workflow run and artifact for any quantitative result. Never invent simulation outputs or citations.
4. **Do not treat green CI as scientific validation.** Require model invariants, baseline comparisons, replication and interpretation checks.
5. **Preserve the canonical record.** Game 1: `docs/games/game1/research.md`; verified horizon report: `docs/games/game1/horizon_100_firms_results.md`. Do not silently overwrite decisions or multiply draft/final documents.
6. **Separate Game 1 from later games.** Current Game 1 is independent learning with output maximization and no explicit AI investment, product-market competition or knowledge sharing. A shared market productivity factor or AI mechanism must not be assumed implemented without code evidence.
7. **Review before committing.** State files changed, tests run/not run, and unresolved risks. Never claim tests passed unless executed or verified in CI. Prefer small, auditable commits on the active branch; do not merge into main without authorization.

## Repository conventions
- Python >=3.11; package `src/interfirm_abm/`; experiments `experiments/`; tests `tests/`; dependencies `pyproject.toml`.
- Run `python -m pytest -q` for Python changes. Preserve `.github/workflows/` and inspect logs and artifacts after execution.
- Game 1 source of truth: `src/interfirm_abm/simulation.py`, `firm.py`, `production.py`, `learning.py`, `random_schedule.py`, `production_optimum.py`.
- Simulation defaults (20 firms/50 rounds) differ from the verified 100-firm experiment (100 firms, 100 seeds, 50/100/200 rounds); always specify which is being discussed.

## P0 skill routing
Before a task, read all relevant files:
- `.agents/skills/research-governance/SKILL.md` — decisions, scope and approval.
- `.agents/skills/model-specification/SKILL.md` — equations, firm construction, code-to-doc consistency.
- `.agents/skills/literature-review/SKILL.md` — literature and references.
- `.agents/skills/experiment-design/SKILL.md` — hypotheses and treatment design.
- `.agents/skills/simulation-validation/SKILL.md` — verification and falsification tests.
- `.agents/skills/reproducibility/SKILL.md` — seeds, provenance and artifacts.

For multi-skill tasks, use governance first; then specification/literature; design; validation; reproducibility. Ask when decisions are ambiguous or approval is needed.

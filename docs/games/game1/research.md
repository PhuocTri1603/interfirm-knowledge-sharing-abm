# Game 1 — Independent Learning

> **Canonical research record.** Update this file in place as the research develops. Git commits record revisions; do not create parallel draft/final versions. Status checked against source files on 2026-10-31. **Not a claim that simulation runs or tests were executed during this documentation review.**

## 1. Research question and scope

**Question:** How do heterogeneous firms improve capital–labor allocations through independent experimentation, and how do alternative exploration policies affect their learning trajectories?

Game 1 is a **model baseline** for subsequent knowledge-sharing comparisons. In the implemented model, firms observe their own experiment histories; they do not exchange knowledge, compete in a product market, or optimize profit. The current code does not implement AI investment as a separate decision.

**Source:** [Simulation](../../src/interfirm_abm/simulation.py), [Firm](../../src/interfirm_abm/firm.py), [Project experimental design](../proposals/experimental_design.md).

## 2. Model specification

| Element | Current implementation | Evidence / status |
|---|---|---|
| Firms | 20 by default; firm IDs 1–20 | `Simulation.__init__` |
| Production technologies | Cobb-Douglas, Leontief, Linear, CES; assigned cyclically | `simulation.py`, `production.py` |
| Decision horizon | 50 rounds by default; one candidate per firm per round | `Simulation.run` |
| Budget | 100 per firm by default | `Firm`, `Simulation` |
| Initial capital share | 0.50 | `Firm` |
| Capital/labor | `K = budget × capital_share`; `L = budget × (1 − capital_share)` | `Firm.produce` |
| Allocation bounds | Candidates strictly between 0 and 1; exploration policy typically restricts to [0.05, 0.95] | `Firm.experiment`, `learning.py` |
| Objective/acceptance | Accept a candidate only when candidate output strictly exceeds current output | `Firm.experiment` |
| Random seed | 2026 by default | `Simulation.__init__` |
| Outcomes recorded | Firm-round experiment history and firm-level final summary | `Simulation.run`, `Simulation.summary` |

### Production functions

The current `production.py` uses the following default specifications, where `K` is capital and `L` is labor:

- **Cobb-Douglas:** `Y = K^0.7 × L^0.3`
- **Leontief:** `Y = min(K/0.7, L/0.3)`
- **Linear:** `Y = 0.7K + 0.3L`
- **CES:** `Y = [0.7K^(-0.5) + 0.3L^(-0.5)]^(-2)` for positive inputs; code also handles zero inputs.

These are implemented equations, not independently validated empirical estimates. The implementation documents constant returns to scale in capital and labor, and `tests/test_production.py` contains tests for that property. **Test presence is not a claim of a successful test run in this review.**

**Source:** [Production functions](../../src/interfirm_abm/production.py), [Production tests](../../tests/test_production.py).

## 3. Independent learning policies

| Policy | Candidate selection | Evidence |
|---|---|---|
| `random` | Uniform candidate in [0.05, 0.95] | `learning.py`, `simulation.py` |
| `guided` | With probability 0.20, random exploration; otherwise normal draw around the highest-output prior candidate (SD 0.10), clipped to [0.05, 0.95] | `learning.py` |
| `guided_initial` | Available with `matched_randomness=True`; similar guided search, but also considers the initial allocation 0.50 when it is at least as good as the best recorded candidate | `simulation.py` |
| Matched random numbers | Predetermined `exploration_draw`, `uniform_draw`, `normal_draw` for each firm–round | `random_schedule.py` |

**Important design interpretation:** Nondecreasing *accepted output* is mechanically guaranteed by the acceptance rule; it is not an independent empirical finding about firms. Failed candidates remain in experiment histories, which may affect guided search.

**Sources:** [Learning policies](../../src/interfirm_abm/learning.py), [Random schedule](../../src/interfirm_abm/random_schedule.py), [Firm tests](../../tests/test_firm.py).

## 4. Research interpretation and theoretical sources

| Statement | Classification | Source / review status |
|---|---|---|
| Trial-and-error can be represented as repeated candidate allocation and output feedback | **Our modeling choice** | Implemented in `firm.py` and `simulation.py`; academic theoretical citation **needed** |
| Four technologies have different capital–labor substitution structures | **Mathematical implication of chosen functions** | `production.py`; textbook citation and exact edition/page **needed** |
| Independent learning is a baseline for evaluating knowledge transfer | **Research design decision** | `docs/proposals/experimental_design.md`; not itself a simulation finding |
| Linear optimum reported by `production_optimum.py` is 0.95 | **Implementation convention requiring review** | Under the implemented increasing linear function, the unconstrained share optimum is at the upper boundary; clarify feasible domain and benchmark interpretation before treating 0.95 as a theoretical optimum |
| Learning policies may have different convergence speeds | **Hypothesis to test** | No verified Game 1 result linked in this record yet |

No academic source has been assigned a DOI, quotation, or page number without independent verification. Citations should be added as they are reviewed, rather than inferred.

## 5. Experiments, results, and reproducibility

| Item | Current status | Next evidence needed |
|---|---|---|
| Executable baseline | `python -m interfirm_abm.simulation` entry point is present in source (environment/install not checked) | Verify execution with recorded environment and commit |
| Unit tests | `tests/test_firm.py`, `tests/test_production.py` exist | Run tests and capture exact command, versions, pass/fail |
| Run-level outputs | `Simulation.run()` returns firm–round records; `summary()` returns per-firm metrics | Identify persisted artifacts, if any; do not infer their existence |
| Baseline results table | **Not yet verified** | Record run ID, commit SHA, seed, parameters, sample size, results file |
| Learning curves and charts | **Not yet verified** | Compute from verified run-level data and publish to Simulation Explorer |
| Monte Carlo robustness | **Not yet verified for Game 1** | Locate code/artifacts and document seeds and uncertainty intervals |

### Simulation run registry

Every actual run will receive a row below; do not enter hypothetical values as findings.

| Run ID | Commit | Policy / treatment | Firms × rounds | Seed(s) | Artifact link | Test/validation | Status |
|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | Awaiting verified artifacts |

## 6. Open issues for review

1. Identify all existing Game 1 experiment scripts and retained run artifacts before making claims about results.
2. Clarify whether allocation boundaries [0.05, 0.95] define the feasible economic domain and whether the linear benchmark at 0.95 should be labeled a constrained optimum.
3. Verify the difference between `guided` and `guided_initial` in matched comparisons.
4. Add reviewed academic references with stable links and exact locations when possible.
5. Document a reproducible run and use its data—not invented examples—to populate the interactive Simulation Explorer.

## Change tracking

Use **Git commit history** as the authoritative edit log for this file. Material changes to assumptions, hypotheses, definitions, or findings should be explained in commit messages. Do not maintain duplicate draft versions.

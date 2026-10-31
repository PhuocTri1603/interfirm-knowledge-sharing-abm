# Game 1 — Independent Learning

> **Canonical research record.** Update this file in place as the research develops. Git commits record revisions; do not create parallel draft/final versions. Status checked against source files on 2026-10-31. **Not a claim that simulation runs or tests were executed during this documentation review.**

## 1. Research question and scope

**Question:** How do heterogeneous firms improve capital–labor allocations through independent experimentation, and how do alternative exploration policies affect their learning trajectories?

Game 1 is a **model baseline** for subsequent knowledge-sharing comparisons. In the implemented model, firms observe their own experiment histories; they do not exchange knowledge, compete in a product market, or optimize profit. The current code does not implement AI investment as a separate decision.

**Source:** [Simulation](../../../src/interfirm_abm/simulation.py), [Firm](../../../src/interfirm_abm/firm.py), [Project experimental design](../../proposals/experimental_design.md).

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

**Source:** [Production functions](../../../src/interfirm_abm/production.py), [Production tests](../../../tests/test_production.py).

## 3. Independent learning policies

| Policy | Candidate selection | Evidence |
|---|---|---|
| `random` | Uniform candidate in [0.05, 0.95] | `learning.py`, `simulation.py` |
| `guided` | With probability 0.20, random exploration; otherwise normal draw around the highest-output prior candidate (SD 0.10), clipped to [0.05, 0.95] | `learning.py` |
| `guided_initial` | Available with `matched_randomness=True`; similar guided search, but also considers the initial allocation 0.50 when it is at least as good as the best recorded candidate | `simulation.py` |
| Matched random numbers | Predetermined `exploration_draw`, `uniform_draw`, `normal_draw` for each firm–round | `random_schedule.py` |

**Important design interpretation:** Nondecreasing *accepted output* is mechanically guaranteed by the acceptance rule; it is not an independent empirical finding about firms. Failed candidates remain in experiment histories, which may affect guided search.

**Sources:** [Learning policies](../../../src/interfirm_abm/learning.py), [Random schedule](../../../src/interfirm_abm/random_schedule.py), [Firm tests](../../../tests/test_firm.py).

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

### Repository audit — 2026-10-31

- **Confirmed executable entry point:** `src/interfirm_abm/simulation.py` defines `Simulation.run()`, `Simulation.summary()`, and a `__main__` block that prints a technology-level and overall summary. The module **does not write its run output to a persistent artifact** in that entry point.
- **Confirmed raw output schema:** firm-round records include `firm_id`, `round`, `technology`, `candidate_share`, `candidate_output`, `accepted`, `capital_share`, and `current_output`.
- **Confirmed summary schema:** `firm_id`, `technology`, `initial_output`, `final_output`, `final_capital_share`, `output_growth_pct`, and `accepted_experiments`.
- **Repository folders:** `experiments/` and `results/` exist, but their complete file inventories have **not** yet been retrieved in this audit. Their existence is **not** evidence of a retained Game 1 run.
- **No verified run registry entry yet:** no Game 1 artifact has been individually inspected and tied to its parameters, seed, and commit. Accordingly, no numeric Game 1 result is reported here.
- **Source links:** [Simulation entry point](../../../src/interfirm_abm/simulation.py), [Firm record schema](../../../src/interfirm_abm/firm.py), [Matched random schedule](../../../src/interfirm_abm/random_schedule.py).

### Experiment inventory — traced to Git history

The repository history identifies five early validation scripts. **Code existence and configured repetitions are not evidence that a particular run completed or that output files were retained.**

| Experiment | Purpose and design | Code | Evidence status |
|---|---|---|---|
| Validation 01 | Compare relative production responses at capital shares 0.25, 0.50, 0.70, 0.75; compute pairwise response-distance | [validation_01.py](../../../experiments/validation_01.py) | Executable source verified; numeric outputs not archived/verified |
| Validation 02 | Copy donor's grid-optimal capital allocation into another technology; 12 directed cross-technology pairs | [validation_02.py](../../../experiments/validation_02.py) | Executable source verified; mechanism check, **not** independent-learning outcome |
| Validation 03 | Deterministic donor-guided vs fixed independent candidate order, three trials per recipient | [validation_03.py](../../../experiments/validation_03.py) | Executable source verified; **not** a causal estimate or pure Game 1 comparison |
| Validation 04 | Donor-guided vs random candidate order; 1,000 random repetitions per donor–recipient pair; seed 2026 | [validation_04.py](../../../experiments/validation_04.py) | Source and [config](../../../results/validation_04/config.json) verified; numeric results not yet verified |
| **Validation 05** | **Game 1 matched Random vs Experience-Guided learning**; 100 seeds (2026–2125), 20 firms, 50 rounds; checkpoints 5, 10, 20, 50 | [validation_05.py](../../../experiments/validation_05.py) | Experiment design verified; executed result artifact not yet verified |

**Validation 05 output definitions:** `advantage_pct = 100 × (guided_output − random_output) / random_output` per matched firm–seed–checkpoint. The script aggregates mean advantages by seed and round, then by technology at round 50. It prints summaries when run directly; the inspected code does not persist a result file. The expected matched comparison size from the design is `100 seeds × 20 firms × 4 checkpoints = 8,000` paired rows, **conditional on successful execution**, not an observed count.

**Provenance:** [initial ABM commit](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/commit/26bdefac00e0be696965b2f11f9ffd9a11979d2c) added validations 01–04 and Validation 04 config; [matched-learning commit](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/commit/5703d173a5a54035587ec0788ef453548afa8628) added Validation 05. This is a **traceable experiment inventory**, not a verified results inventory.

### Automated reproducibility workflow

[Game 1 validation workflow](../../../.github/workflows/game1-validation.yml) was added on branch `docs/research-consolidation` in commit [`b4daf048`](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/commit/b4daf0485e3868304b6143df868dca122768603c). It is configured to:

1. Install Python 3.11 and project dependencies.
2. Execute the existing pytest suite.
3. Run `python -m experiments.validation_05 --export-dir results/validation_05`.
4. Check 8,000 expected matched rows, no missing values, 100 seeds, 20 firms, four checkpoints, and positive random-policy outputs.
5. Capture the exact source SHA and installed environment; upload the CSV/JSON outputs as a GitHub Actions artifact (90-day retention).

**Verification status:** workflow file committed; a successful workflow run, test log, downloadable artifact, and actual Game 1 numeric results have **not** yet been verified. The workflow's artifact is temporary and should not be confused with permanent research archival. The `.gitignore` excludes generated CSV files, so successful execution will not by itself add numeric outputs to Git history.

## 6. Open issues for review

1. Identify all existing Game 1 experiment scripts and retained run artifacts before making claims about results.
2. Clarify whether allocation boundaries [0.05, 0.95] define the feasible economic domain and whether the linear benchmark at 0.95 should be labeled a constrained optimum.
3. Verify the difference between `guided` and `guided_initial` in matched comparisons.
4. Add reviewed academic references with stable links and exact locations when possible.
5. Document a reproducible run and use its data—not invented examples—to populate the interactive Simulation Explorer.

## Change tracking

Use **Git commit history** as the authoritative edit log for this file. Material changes to assumptions, hypotheses, definitions, or findings should be explained in commit messages. Do not maintain duplicate draft versions.

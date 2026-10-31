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

### Export contract smoke test

[Export test](../../../tests/test_validation_05_export.py) was added in commit [`3b31c087`](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/commit/3b31c087f21da751cbaa97d77fc0ea19b493e2e7). It constructs a **synthetic two-row fixture** to check the four output files, aggregation arithmetic, and metadata. This fixture is **not** a research result. The test's presence does not establish that it has passed in GitHub Actions.

**GitHub Actions visibility limitation:** the available commit-to-workflow lookup only returns pull-request-triggered runs; an empty response cannot establish whether a push-triggered run happened. Thus the execution status remains **unverified**, not `failed` or `not run`. Inspect the [Actions page](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/workflows/game1-validation.yml) for a completed run, test log, and downloadable artifacts before promoting any result to the run registry.

### Verified Simulation Run Registry — Validation 05

| Field | Verified value |
|---|---|
| GitHub Actions run | [41161569703](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41161569703) |
| Run conclusion | **Success**; GitHub job and all test, experiment, export-validation, upload steps successful |
| Source commit | `3b31c087f21da751cbaa97d77fc0ea19b493e2e7` |
| Branch | `docs/research-consolidation` |
| Artifact | `game1-validation-05-3b31c087f21da751cbaa97d77fc0ea19b493e2e7`, ID `13027112148` |
| Artifact digest | `sha256:c927eb7f2929b9662a395c0fcec4039cc42df6a00731e0f467f5d80ce53c0c52` |
| Artifact availability at inspection | Not expired; GitHub expiration set to **2027-01-29** |
| Input design | 100 seeds (2026–2125), 20 firms, 50 rounds, policies random/guided, common random numbers |
| Verified paired observations | **8,000**; four checkpoints × 100 seeds × 20 firms |
| Files inspected | `paired_observations.csv`, `seed_round_summary.csv`, `summary_by_round.json`, `metadata.json`, `source_commit.txt`, `environment.txt` |
| Measurement | `100 × (guided_output − random_output) / random_output` per firm/seed/checkpoint |

#### Numeric results reproduced directly from downloaded paired observations

| Checkpoint | Mean firm-level advantage (%) | Seeds with positive mean advantage (of 100) |
|---|---:|---:|
| 5 | -1.8556 | 19 |
| 10 | -0.0032 | 49 |
| 20 | +1.1697 | 97 |
| 50 | +0.5893 | 100 |

**Round 50, by technology** (mean firm-level advantage; 500 matched firm-seed observations per technology):

| Technology | Guided advantage (%) |
|---|---:|
| CES | +0.0472 |
| Cobb-Douglas | +0.0332 |
| Leontief | +1.1568 |
| Linear | +1.1199 |

**Interpretation:** Guided exploration is initially weaker on average than random exploration; by round 20 and round 50 the average advantage is positive. All 100 *seed-level averages* are positive at round 50; **this does not imply every individual firm benefited**. Technology-level advantages differ substantially. These are model-internal Monte Carlo outcomes, **not empirical evidence of real-world firms**, and not estimates of the effect of inter-firm knowledge sharing: both policies use only their own histories.

**Cautions:** Seed-level performance correlation is controlled by common random numbers; uncertainty quantification and robustness to firm counts, search-radius, exploration probability, production-function parameters, and longer horizons are still outstanding. In particular, a positive average at a checkpoint alone is not a formal hypothesis test. Store/archive the downloaded artifact before its expiry if long-term traceability is required.

### Statistical follow-up — seed-level uncertainty and heterogeneous outcomes

Recalculated from the **verified** artifact `paired_observations.csv` and `seed_round_summary.csv` associated with GitHub Actions [run 41161569703](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41161569703), source commit `3b31c087f21da751cbaa97d77fc0ea19b493e2e7`.

For each checkpoint, first average the firm-level `advantage_pct` across 20 firms **within each seed**, then compute the across-seed mean and standard deviation. The reported 95% intervals are **approximate two-sided Student-t confidence intervals** `mean ± t_(0.975,99) × SD(seed mean) / sqrt(100)`, using `t_(0.975,99) ≈ 1.984`. These characterize variability across simulated seeds **conditional on this model and parameterization**, not sampling uncertainty about real firms.

| Round | Mean advantage (%) | SD of seed means (pp) | Approx. 95% CI (%) | Seeds with positive mean |
|---|---:|---:|---|---:|
| 5 | -1.8556 | 1.8913 | [-2.2309, -1.4804] | 19 / 100 |
| 10 | -0.0032 | 1.7692 | [-0.3542, +0.3478] | 49 / 100 |
| 20 | +1.1697 | 0.7617 | [+1.0186, +1.3208] | 97 / 100 |
| 50 | +0.5893 | 0.2645 | [+0.5368, +0.6418] | 100 / 100 |

At round 50, the **firm-level** distribution shows important heterogeneity. Each technology has 500 observations (5 firms per seed × 100 seeds).

| Technology | Mean advantage (%) | Median advantage (%) | Fraction of firm-seed pairs with strictly positive advantage |
|---|---:|---:|---:|
| CES | +0.0472 | +0.0091 | 75.2% |
| Cobb-Douglas | +0.0332 | +0.0083 | 72.8% |
| Leontief | +1.1568 | +0.5517 | 71.2% |
| Linear | +1.1199 | +0.7724 | 100.0% |

**Interpretation and hypotheses, not yet established mechanisms:** Leontief's kink and Linear's boundary-favoring optimum may make search policies behave differently from the smooth interior-optimum technologies. Confirming that explanation requires analyzing the distribution of capital shares, distance-to-optimum, and policy-specific trajectories; the checkpoint artifact contains **outputs only**, not the full trial-by-trial search histories. The positive result in 100/100 seeds at round 50 applies to **seed-level means**, not to every firm. The approximate confidence intervals are descriptive conditional on the chosen seeds/model; multiple-checkpoint comparisons, parameter sensitivity, and longer-horizon tests remain open.

**Next analysis:** retain full firm-round histories for both policies in a future run; compare allocation convergence and the rate of accepted improvements. Investigate the decline in mean advantage from round 20 to 50 and whether random exploration catches up. Avoid interpreting this Game 1 policy comparison as a test of inter-firm knowledge sharing.

### Follow-up experiment: firm-level learning trajectories (pending verification)

Added [`experiments/game1_mechanism_trajectories.py`](../../../experiments/game1_mechanism_trajectories.py) in commit `cd3ce5f6`, and integrated it into the existing [GitHub Actions workflow](../../../.github/workflows/game1-validation.yml) in commit `dc8184c9`. This **new** experiment records all firm-round observations for both learning policies with common random numbers (100 seeds × 20 firms × 50 rounds × 2 policies = **200,000 expected rows**, yielding **100,000 expected matched pairs**). It exports `firm_round_trajectories.csv`, `paired_firm_round.csv`, `mechanism_by_technology_round.csv`, and `metadata.json` to `results/game1_mechanism/` as a GitHub Actions artifact.

**Research objective:** compare the dynamics of accepted candidate allocations, actual capital shares, and output paths, with particular attention to the round-20-to-round-50 decline in Guided advantage and heterogeneity across technologies. The file does **not** compute distance to an optimal capital share; that requires a separately audited technology-specific optimum definition and careful handling of Linear's boundary optimum.

**Status:** code and workflow changes committed; **no successful run or numerical findings from this new experiment have yet been verified**. The prior Validation 05 findings remain unchanged. Full histories are descriptive; they do not by themselves identify the causal mechanism.

### Verified mechanism run — full firm-round trajectories

**Provenance:** [GitHub Actions run 41162166751](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41162166751), **completed successfully**, source commit `dc8184c91ec5c9bd5eee116520875285b7e3b190`. Artifact `game1-validation-05-dc8184c91ec5c9bd5eee116520875285b7e3b190`, ID `13028125423`. Downloaded ZIP was inspected directly. The experiment generated **200,000 firm-round-policy records** (10 columns) and **100,000 matched firm-round pairs** (9 columns), with 100 seeds, 50 rounds, and **zero missing cells** in both datasets. **Zero decreases** in within-firm output trajectories (expected because improvements alone are accepted). This is a simulation, not external firm data.

#### Dynamic comparison

| Round | Mean firm-level Guided advantage (%) | Firm-seed pairs with Guided advantage > 0 (%) | Mean Guided-minus-Random capital share |
|---|---:|---:|---:|
| 1 | 0.0000 | 0.00 | 0.00000 |
| 5 | -1.8556 | 36.80 | -0.03539 |
| 10 | -0.0032 | 54.35 | -0.01235 |
| 20 | +1.1697 | 72.10 | +0.00907 |
| 30 | +0.9200 | 77.20 | +0.00875 |
| 40 | +0.7011 | 78.15 | +0.00745 |
| 50 | +0.5893 | 79.80 | +0.00597 |

The reduction from **+1.1697% at round 20** to **+0.5893% at round 50** coexists with an *increase* in the fraction of matched firms benefiting from Guided (72.1% to 79.8%). Thus, mean advantage and breadth of benefit move differently: a smaller mean gap does not imply fewer benefiting firms.

#### Round 50 — production technology and allocation

| Technology | Guided mean output | Random mean output | Guided mean capital share | Random mean capital share | Guided acceptance rate in round 50 | Random acceptance rate in round 50 |
|---|---:|---:|---:|---:|---:|---:|
| CES | 52.89011 | 52.86523 | 0.63750 | 0.63684 | 2.8% | 2.8% |
| Cobb-Douglas | 54.28547 | 54.26750 | 0.69960 | 0.69913 | 2.4% | 1.4% |
| Leontief | 99.32890 | 98.22514 | 0.69723 | 0.69311 | 2.4% | 2.0% |
| Linear | 68.00000 | 67.25442 | 0.95000 | 0.93136 | 0.0% | 2.8% |

Across **all 50 rounds**, accepted experiments account for **9.532%** of Guided trials and **7.101%** of Random trials. This is a descriptive comparison, not a randomized intervention on an isolated mechanism.

**Mechanism interpretation (supported descriptively, not causally identified):** At round 50, Guided Linear firms have reached the allowed upper allocation bound `capital_share = 0.95` on average (indeed mean output is exactly 68), and their round-50 acceptance rate is 0%; Random Linear firms still accept improvements (2.8% at round 50) and are closer to catching up. This is consistent with **convergence/catch-up** as a contributor to the declining advantage. Leontief also exhibits a larger remaining output gap than smooth interior-optimum Cobb-Douglas/CES. Formal mechanism identification would require counterfactual variations of exploration probability, step size, bounds, and production technology while holding other factors fixed.

**Important distinction:** `capital_share` is the actual accepted allocation, not the trial `candidate_share`; these must not be conflated. The Linear optimum under the **constrained search interval** is `0.95`; the unconstrained theoretical maximum is at share `1.0`. No unverified optimum-distance claim is made for CES here.

## 6. Open issues for review

1. Identify all existing Game 1 experiment scripts and retained run artifacts before making claims about results.
2. Clarify whether allocation boundaries [0.05, 0.95] define the feasible economic domain and whether the linear benchmark at 0.95 should be labeled a constrained optimum.
3. Verify the difference between `guided` and `guided_initial` in matched comparisons.
4. Add reviewed academic references with stable links and exact locations when possible.
5. Document a reproducible run and use its data—not invented examples—to populate the interactive Simulation Explorer.

## Change tracking

Use **Git commit history** as the authoritative edit log for this file. Material changes to assumptions, hypotheses, definitions, or findings should be explained in commit messages. Do not maintain duplicate draft versions.

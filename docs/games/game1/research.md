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

### Literature review — foundational evidence and model-assumption audit (2026-10-31)

**Scope and search.** Targeted foundational-source search on 2026-10-31 across American Economic Association/JSTOR, Oxford Academic, publisher or institutional book records, PubMed and USGS. This is a **focused foundation review**, not a systematic or exhaustive novelty review. Bibliographic records and accessible abstracts/primary texts were checked; full-book chapter-level claims were not independently verified. The purpose is to distinguish established theoretical frameworks from our own Game 1 parameterization.

#### Evidence matrix

| Research strand | Verified work | What it supports | What it **does not** establish for Game 1 |
|---|---|---|---|
| Cobb-Douglas production | Cobb & Douglas (1928), *A Theory of Production* | Historical foundation for analyzing output as a function of capital and labor | Does not calibrate our `alpha=0.70`, fixed `B=100`, or firm population |
| Input substitutability / CES | Arrow, Chenery, Minhas & Solow (1961), *Capital-Labor Substitution and Economic Efficiency* | Explicit comparison of fixed coefficients and Cobb-Douglas substitution assumptions; motivation for a more flexible constant-elasticity form | Does not establish our `rho=-0.50` or equal counts of four technologies |
| Fixed coefficients / Leontief | Leontief (1941), *The Structure of American Economy, 1919–1929*; Arrow et al. (1961) | Historical fixed-input-coefficient tradition and contrast with substitutable inputs | Does not validate the exact two-input normalization `min(K/.7,L/.3)` for observed firms |
| Bounded rationality | Simon (1955), *A Behavioral Model of Rational Choice* | Behavioral alternatives to assuming fully informed optimization | Does not prescribe our Gaussian local search or exploration probability |
| Evolutionary firm behavior | Nelson & Winter (1982), *An Evolutionary Theory of Economic Change*; Nelson & Winter (2002), *Evolutionary Theorizing in Economics* | Firms represented through routines, search, learning and selection instead of assuming instantaneous optimization | Our rule “accept only strictly higher output” is a simplified researcher-specified mechanism, not an exact implementation of their theory |
| Agent-based computational economics | Tesfatsion (2002), *Agent-Based Computational Economics: Growing Economies from the Bottom Up* | A methodological framework for computational economic systems with autonomous evolving agents | Game 1 firms do **not** interact, so this is a restricted independent-learning ABM baseline, not evidence of emergent interfirm network dynamics |
| Transparent ABM reporting | Grimm et al. (2006), *A Standard Protocol for Describing Individual-Based and Agent-Based Models* | ODD categories: purpose, state variables/scales, process scheduling, design concepts, initialization, input, submodels | Reporting transparency does not itself validate economic realism or empirical fit |
| ABM verification and analysis | Railsback & Grimm (2019), *Agent-Based and Individual-Based Modeling*, 2nd ed. | Practical methods for documenting, testing, and analyzing adaptive ABMs | Does not certify that our particular code and experiments are correct |

#### Interpretation for the four production functions

Game 1 compares technologies with distinct *mathematical* substitution properties. Under the chosen forms, Leontief has fixed proportions; Cobb-Douglas has unit elasticity of substitution; Linear represents perfect substitutes; CES has constant elasticity `sigma=1/(1-rho)`, which is `2/3` at `rho=-0.5`. The CES value is **less than one**, so our parameterization is more complementary than Cobb-Douglas, but not perfectly complementary. These properties follow from the specified functions; they are not estimates from industry data. For the Linear technology, the reported optimal share `0.95` is a **feasible-set boundary benchmark**, not the unrestricted optimum.

The code deliberately uses the same `alpha=.7` in Cobb-Douglas, Linear and CES, and `kappa=.7` in Leontief. **Equal numeric parameters do not imply identical economic meaning across functions**. Initial equal `K=L=50` does not imply equal initial output. The four-group 25/25/25/25 assignment is an experimental balancing choice rather than an observed industry composition.

#### Interpretation for adaptive learning

Simon (1955) and Nelson & Winter (1982, 2002) motivate studying firms that adapt under limited information rather than directly calculating their optimum. Our Game 1 operationalizes this with repeated output-feedback experiments, strict improvement acceptance, and policy-specific candidate search. **Random and Guided are algorithms designed by this project**, not named treatments copied from those papers. In particular, `exploration_probability=.20`, `search_radius=.10`, the normal search kernel, the 100-firm population, and horizons 50/100/200 are **researcher design choices** awaiting sensitivity/robustness justification; no reviewed paper is claimed to calibrate them.

Nelson & Winter study evolutionary processes that include organizational and industry dynamics; Game 1 isolates a simpler **within-firm independent learning** mechanism. Tesfatsion's agent-based economics provides a wider methodological context, but interactions and knowledge exchange are reserved for later games. It would be inaccurate to cite these works as empirical evidence that our Guided policy will outperform Random.

#### Research gap — provisional, not yet a novelty claim

A *candidate contribution* is to examine how **production-technology heterogeneity changes the relative learning trajectories of independently experimenting firms under matched randomness**, before introducing observation or interfirm knowledge sharing. The reviewed foundational works motivate the ingredients but **do not establish that no earlier paper studied this exact comparison**. Before any claim of originality, perform a targeted contemporary search for firm learning/search on heterogeneous production landscapes, adaptive resource allocation, local-versus-global exploration and computational experiments using common random numbers. Record close competitors and null/contradictory evidence.

#### ODD-style reporting checklist for Game 1

| ODD element | Existing evidence | Remaining work |
|---|---|---|
| Purpose | Section 1 of this canonical record | Tie explicitly to testable estimands |
| State variables and scales | Firm ID, technology, budget, share, current output, history; rounds | Clarify simulation time is an abstract decision round |
| Process overview and scheduling | `Simulation.run`, sequential firm iteration per round | Document lack of interfirm interaction and consequences |
| Design concepts | Trial-and-error search, limited observation, output feedback | Link mechanisms and hypotheses without overclaiming |
| Initialization | Verified 100-firm protocol above | State calibration limitations |
| Input data | Synthetic initial parameters and seeded random schedule | Explicitly say no observed firm microdata |
| Submodels | Production, candidate selection, acceptance, constrained optimum | Include tests, invariants and output schema |

#### Verified references (metadata checked; no unverified page-specific quotations)

1. Cobb, C. W., & Douglas, P. H. (1928). A theory of production. *The American Economic Review, 18*(1, Supplement), 139–165. https://www.jstor.org/stable/1811556
2. Arrow, K. J., Chenery, H. B., Minhas, B. S., & Solow, R. M. (1961). Capital-labor substitution and economic efficiency. *The Review of Economics and Statistics, 43*(3). https://msuweb.montclair.edu/~lebelp/ACMSCapLabSubREAS1961.pdf (accessible paper; DOI not independently checked here)
3. Leontief, W. (1941). *The Structure of American Economy, 1919–1929: An Empirical Application of Equilibrium Analysis*. Harvard University Press. https://books.google.com/books?id=cm_HAAAAMAAJ
4. Simon, H. A. (1955). A behavioral model of rational choice. *The Quarterly Journal of Economics, 69*(1), 99–118. https://doi.org/10.2307/1884852
5. Nelson, R. R., & Winter, S. G. (1982). *An Evolutionary Theory of Economic Change*. Harvard University Press. https://books.google.com/books?id=uRm5AAAAIAAJ
6. Nelson, R. R., & Winter, S. G. (2002). Evolutionary theorizing in economics. *Journal of Economic Perspectives, 16*(2), 23–46. https://doi.org/10.1257/0895330027247
7. Tesfatsion, L. (2002). Agent-based computational economics: Growing economies from the bottom up. *Artificial Life, 8*(1), 55–82. https://doi.org/10.1162/106454602753694765
8. Grimm, V., Berger, U., Bastiansen, F., et al. (2006). A standard protocol for describing individual-based and agent-based models. *Ecological Modelling, 198*(1–2), 115–126. https://doi.org/10.1016/j.ecolmodel.2006.04.023
9. Railsback, S. F., & Grimm, V. (2019). *Agent-Based and Individual-Based Modeling: A Practical Introduction* (2nd ed.). Princeton University Press. https://doi.org/10.2307/jj.28274141

**Review status:** Foundational source identities and relevance checked; parameter calibration **not supported**; exhaustive prior-art/novelty review **pending**; full-text scrutiny of every chapter **pending**. This update is documentation-only: no Python tests or new simulations were run.

### Focused adjacent-literature comparison — scope-limited Game 1 review (2026-10-31)

**Purpose and boundary.** This review is strictly for understanding and accurately documenting **existing** Game 1 independent-learning mechanisms. It does **not** propose a new mechanism, hypothesis, research gap, contribution, or paper claim. Sources were selected by targeted searches for exploration–exploitation, organizational adaptation, experiential search, and computational knowledge replication; publisher article pages and available abstracts were checked on 2026-10-31. The table is **not** an exhaustive systematic review.

| Source and verified bibliographic record | Claim supported by publisher abstract | Relevance to existing Game 1 | Material difference / what cannot be claimed | Evidence depth |
|---|---|---|---|---|
| March (1991), *Exploration and Exploitation in Organizational Learning*, *Organization Science* **2**(1), 71–87, DOI [10.1287/orsc.2.1.71](https://doi.org/10.1287/orsc.2.1.71) | Organizational learning involves tension between exploring new possibilities and exploiting existing knowledge, with different time horizons and trade-offs. | Conceptual background for Guided's mixture of global exploration and history-based local search. | March's paper models organizational learning and ecological/competitive processes, not this code's exact `0.20` exploration probability, Gaussian kernel, or output acceptance rule. | Publisher abstract and metadata verified; not a full replication |
| Levinthal (1997), *Adaptation on Rugged Landscapes*, *Management Science* **43**(7), 934–950, DOI [10.1287/mnsc.43.7.934](https://doi.org/10.1287/mnsc.43.7.934) | Organizational adaptation can be path-dependent when interactive attributes generate multiple local peaks. | Useful **contrast** with local adaptive search and the significance of initial conditions. | Game 1 uses a one-dimensional allocation share and fixed, standard production functions, **not** Levinthal's multi-attribute rugged landscape. Do not claim its landscape has multiple local optima or use his results as direct predictions. | Publisher abstract and metadata verified |
| Gavetti & Levinthal (2000), *Looking Forward and Looking Backward: Cognitive and Experiential Search*, *Administrative Science Quarterly* **45**(1), 113–137, DOI [10.2307/2666981](https://doi.org/10.2307/2666981) | Computer simulations compare forward-looking cognitive maps with backward-looking experiential search; representations guide search. | Context for learning from prior observed action–outcome pairs. | Guided in Game 1 is **experience-guided local search**, not a forward-looking cognitive model or mental representation of the production function. | Publisher abstract, metadata and institutional author-hosted paper located |
| Rivkin (2001), *Reproducing Knowledge: Replication Without Imitation at Moderate Complexity*, *Organization Science* **12**(3), 274–293, DOI [10.1287/orsc.12.3.274.10106](https://doi.org/10.1287/orsc.12.3.274.10106) | Agent-based simulation examines strategy complexity, replication versus imitation, and information advantages. | Background for **future** interfirm knowledge-related work; relevant mainly as a boundary for Game 1. | Game 1 includes **neither imitation nor knowledge replication nor interfirm information exchange**; this is not direct support for the Game 1 algorithm. | Publisher abstract and metadata verified |

**Code-to-literature interpretation (without new assumptions).**
- **Random:** independent uniform search over the candidate capital-share interval. It is a project-defined benchmark, not a reproduction of March's model.
- **Guided:** project-defined combination of uniform global proposals and normal local proposals centered on the best previously evaluated candidate; the candidate can have been rejected. This is **experience-guided**, not a modeled cognitive map.
- **Strict improvement:** candidate allocation is accepted only if its output strictly exceeds current output; this mechanically guarantees nondecreasing accepted output. The cited organizational-learning works do not validate this specific rule.
- **Production landscape:** a fixed, one-dimensional share-to-output mapping under the four specified production functions. Do not import multi-peak NK-landscape dynamics from Levinthal or Rivkin.
- **Interfirm knowledge:** absent from Game 1. Literature on imitation and transfer should be reserved for the separately approved scope of later games/paper work.

**Source and assumption status.** General organizational learning and adaptive search: **literature-backed conceptual context**. Exact Random/Guided algorithms, `exploration_probability=.20`, `search_radius=.10`, acceptance rule, 100-firm balanced sample, and 50/100/200-round horizons: **implemented researcher choices**, not externally calibrated. Empirical realism of parameters and cross-industry representativeness: **unverified**.

**Explicitly deferred.** Novelty assessment, new research questions, theoretical extensions, alternative algorithms, knowledge-sharing mechanisms, and manuscript-level contributions are **outside this Game 1 documentation task**. Do not silently promote this review into a paper proposal.

**Verification status.** Four publisher records checked; abstract-level interpretation used unless noted; no Python code or experiment changed, no tests or simulations run for this documentation-only review.

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

### Mechanism audit extension — distance to constrained optimum (pending run)

The trajectory experiment was extended in commit `e9625bbe` to export, for each firm–round, `optimal_share`, `optimal_output`, absolute `share_distance_to_optimum`, and `output_efficiency_pct = 100 × current_output / optimal_output`. Its technology–round summary now includes mean allocation distance and mean output efficiency; paired observations include Guided-minus-Random differences in both measures. The optimum is defined **within the search interval [0.05, 0.95]**, so Linear uses 0.95, whereas the unconstrained optimum of the increasing Linear technology lies at 1.0. For CES, the analytical formula is implemented in [`production_optimum.py`](../../../src/interfirm_abm/production_optimum.py).

An independent numerical audit was added in commit `521715cc`: [`tests/test_game1_optimum_audit.py`](../../../tests/test_game1_optimum_audit.py) compares each technology's analytical optimum against a dense 9,001-point feasible grid, with a tolerance for discretization.

**Verification status:** changes committed, but **the new tests and updated trajectory output have not yet been verified in a completed Actions run**. Previously reported results from run 41162166751 refer to the earlier experiment version and remain separate.

**Planned interpretation:** evaluate whether Guided's early advantage corresponds to faster reduction in distance-to-optimum, and whether Random catches up later. An association between allocation distance and output does not independently establish a causal mechanism because both derive from the same production function.

### Verified constrained-optimum convergence experiment — 2026-10-31

**Source of truth:** [GitHub Actions run 41162502564](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41162502564), successful, source commit `521715cce192e15764fd5689ba771feee72640c5`. Artifact `game1-validation-05-521715cce192e15764fd5689ba771feee72640c5` (ID `13027672664`). Direct inspection of the artifact confirms 200,000 history rows (14 columns) and 100,000 paired rows (15 columns), zero missing cells, and zero output-efficiency values exceeding 100% (within numerical tolerance). Automated tests including the numerical optimum audit passed in this run.

**Feasible capital share interval:** [0.05, 0.95]. Constrained optimal shares and maximum outputs with budget 100:

| Technology | Optimal capital share | Optimal output |
|---|---:|---:|
| CES | 0.637578 | 52.893572 |
| Cobb-Douglas | 0.700000 | 54.288145 |
| Leontief | 0.700000 | 100.000000 |
| Linear | 0.950000 | 68.000000 |

**Mean output efficiency**, defined as `100 × current_output / technology_specific_constrained_optimal_output`:

| Round | Guided (%) | Random (%) | Guided minus Random (percentage points) |
|---|---:|---:|---:|
| 5 | 91.41525 | 93.33992 | -1.92466 |
| 10 | 96.04648 | 96.24937 | -0.20288 |
| 20 | 99.18220 | 98.12602 | +1.05618 |
| 50 | 99.82936 | 99.25927 | +0.57008 |

**Mean absolute capital-share distance from the technology-specific constrained optimum:**

| Round | Guided | Random | Guided minus Random |
|---|---:|---:|---:|
| 5 | 0.12278 | 0.09420 | +0.02858 |
| 10 | 0.05859 | 0.05383 | +0.00477 |
| 20 | 0.01273 | 0.02788 | -0.01515 |
| 50 | 0.00257 | 0.01180 | -0.00924 |

**Round-50 efficiency by technology:**

| Technology | Guided efficiency (%) | Random efficiency (%) | Guided distance | Random distance |
|---|---:|---:|---:|---:|
| CES | 99.99345 | 99.94641 | 0.00316 | 0.00917 |
| Cobb-Douglas | 99.99508 | 99.96197 | 0.00318 | 0.00919 |
| Leontief | 99.32890 | 98.22514 | 0.00393 | 0.01021 |
| Linear | 100.00000 | 98.90356 | 0.00000 | 0.01864 |

**Interpretation:** At rounds 5 and 10, Guided has lower mean efficiency and larger mean distance to the optimum; by rounds 20 and 50, the ranking reverses. Both policies approach high efficiency by round 50, consistent with diminishing headroom for further output gains. Linear Guided reaches the constrained optimum by round 50. These findings support a **descriptive convergence explanation**, not a separately identified causal mechanism. Output efficiency and optimum distance are derived from the same fixed production functions; their agreement is not independent causal confirmation. Robustness to exploration rate, neighborhood width, firm heterogeneity, and horizon is still required.

### Verified 100-firm initialization and decision protocol — code audit (2026-10-31)

**Scope and evidence.** This subsection applies `model-specification`, `research-documentation`, and `research-audit` to the actual Game 1 implementation. It documents code behavior; it does not introduce a new economic mechanism or imply new simulation execution. Sources: [simulation](../../../src/interfirm_abm/simulation.py), [firm](../../../src/interfirm_abm/firm.py), [production](../../../src/interfirm_abm/production.py), [learning](../../../src/interfirm_abm/learning.py), [random schedule](../../../src/interfirm_abm/random_schedule.py), [optimum](../../../src/interfirm_abm/production_optimum.py), [horizon experiment](../../../experiments/game1_mechanism_trajectories.py), and [verified run report](horizon_100_firms_results.md).

**Default versus experimental configuration.** `Simulation.__init__` defaults to 20 firms, 50 rounds, seed 2026 and budget 100. The separate horizon experiment invokes 100 firms, 100 seeds (2026 through 2125), 50/100/200 rounds, two policies (`random`, `guided`) and `matched_randomness=True`. The 100-firm experiment is not the simulator's default. The researcher selected this simulated population size; it is not an empirically estimated number of firms.

**Agent construction.** At initialization, `Simulation` creates agents with `firm_id=i+1` and `technology=TECHNOLOGIES[i % 4]`, where `TECHNOLOGIES = ["Cobb-Douglas", "Leontief", "Linear", "CES"]`. For 100 firms this produces 25 agents per technology. Every agent starts with `budget=100`, `capital_share=0.50`, empty experimental history and `current_output=produce(0.50)`. The model does not sample initial budgets or firm-specific productivity parameters. Firms differ by production technology, not by randomly drawn initial resources.

**Allocation and production.** With budget `B=100` and current capital share `s`, `K=B*s`, `L=B*(1-s)`. Initially `K=L=50`; both can change after accepted experiments while `K+L=B` remains fixed. Production functions and exact default parameters:

| Technology | Implemented production function | Default parameters | Feasible optimal capital share in the benchmark |
|---|---|---|---|
| Cobb-Douglas | `K^alpha * L^(1-alpha)` | `alpha=0.70` | `0.70` |
| Leontief | `min(K/kappa, L/(1-kappa))` | `kappa=0.70` | `0.70` |
| Linear | `alpha*K+(1-alpha)*L` | `alpha=0.70` | `0.95` (constrained; unconstrained optimum at 1.0) |
| CES | `[alpha*K^rho+(1-alpha)*L^rho]^(1/rho)` | `alpha=0.70`, `rho=-0.50` | `r/(1+r)`, `r=(alpha/(1-alpha))^(1/(1-rho))` |

The feasible benchmark is defined on the policy's share interval `[0.05,0.95]`. The underlying `Firm.experiment` accepts any share strictly inside `(0,1)`; the narrower bounds come from candidate-generation policies. Therefore the benchmark is **policy-feasible**, not an unrestricted technological maximum. These parameter values are modeling choices; this code inspection is not empirical calibration.

**One round, one agent.** For each round `t=1,...,T` and each firm in ID order, the simulation obtains a candidate share. Under matched randomness, a pre-generated schedule provides `exploration_draw`, `uniform_draw`, and `normal_draw` for every `(t, firm_id)`. Random proposes `s'=0.05+0.90*uniform_draw`. Guided proposes the same global-uniform draw when history is empty or `exploration_draw<0.20`; otherwise it finds the historical candidate with highest `candidate_output` and proposes `clip(best_share+0.10*normal_draw,0.05,0.95)`. Note that the best historical *candidate* may have been rejected; the code does not restrict this search to accepted experiments. Each agent evaluates `Y(s')`; it accepts iff `Y(s')>current_output`, updating its share and current output only then. Both successful and unsuccessful candidates enter the history. The exported record includes `firm_id`, `round`, `technology`, `candidate_share`, `candidate_output`, `accepted`, `capital_share`, and `current_output`.

**Comparison design.** For each seed the experiment instantiates independent Random and Guided simulations with identical firm initialization and the same pre-generated firm-round random draws. Policies are paired by `seed`, `round`, `firm_id`, and `technology`. The expected history size is `100 seeds * 100 firms * T rounds * 2 policies`; the expected paired size is half that. Reusing matched draws reduces avoidable simulation noise; it does not make outcomes statistically independent across firms in the same seed.

**Interpretive boundaries.** Game 1 does not implement firm-specific capital prices, endogenous budgets, AI investment as a separate choice, a product market, profit maximization or interfirm knowledge exchange. Monotonic accepted output is guaranteed by the strict acceptance rule; it should not be reported as an emergent empirical discovery. A common multiplicative productivity shock, where used in a future scenario, would not by itself change the optimal share with unchanged functions and budget.

**Audit status.** PASS (code-to-document traceability for the statements above); NOT RUN (new Python tests or Monte Carlo runs during this documentation edit); OPEN (external scholarly grounding of modeling assumptions and independent website visualization). The separate horizon results report records earlier executed validation and should not be conflated with tests run for this documentation-only change.

## 6. Open issues for review

1. Identify all existing Game 1 experiment scripts and retained run artifacts before making claims about results.
2. Clarify whether allocation boundaries [0.05, 0.95] define the feasible economic domain and whether the linear benchmark at 0.95 should be labeled a constrained optimum.
3. Verify the difference between `guided` and `guided_initial` in matched comparisons.
4. Add reviewed academic references with stable links and exact locations when possible.
5. Document a reproducible run and use its data—not invented examples—to populate the interactive Simulation Explorer.

## Change tracking

Use **Git commit history** as the authoritative edit log for this file. Material changes to assumptions, hypotheses, definitions, or findings should be explained in commit messages. Do not maintain duplicate draft versions.

### Game 1 sensitivity analysis — registered design (pending results)

The sensitivity experiment is implemented in [`experiments/game1_sensitivity.py`](../../../experiments/game1_sensitivity.py), with configurable exploration probability and search radius in `Simulation`, parameter tests in [`tests/test_game1_sensitivity.py`](../../../tests/test_game1_sensitivity.py), and a dedicated GitHub Actions sensitivity job. [Run 41162810655](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41162810655) was **in progress when checked**; no numerical sensitivity result is claimed here.

The predeclared design uses 100 seeds (2026–2125), 20 firms, 100 rounds, matched Random and Guided schedules, and checkpoints 5, 10, 20, 50, 100. The nine one-factor-at-a-time settings are baseline (exploration probability 0.20, search radius 0.10), exploration probabilities 0.05/0.10/0.40/0.60 at radius 0.10, and search radii 0.03/0.05/0.20/0.30 at probability 0.20. Expected matched observations: 90,000. Outputs are `paired_sensitivity.csv`, `seed_sensitivity.csv`, `summary_sensitivity.csv`, and `metadata.json`.

The planned checks are whether the Guided advantage at rounds 20 and 50 persists across parameter settings, whether the gap narrows at round 100, and how the magnitude and seed-level variability respond to exploration versus local search width. These parameter sweeps test **robustness of this simulated model**, not external validity or causal identification of real firms' learning.

### Verified sensitivity results — GitHub Actions run 41162810655

**Evidence:** [successful run 41162810655](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41162810655), commit `28b9630103d3efe2fb49f3d02966fd04a1adf7bc`, artifact `game1-sensitivity-28b9630103d3efe2fb49f3d02966fd04a1adf7bc` (ID `13027758627`). Direct ZIP/CSV inspection confirmed 90,000 matched firm–seed–checkpoint–scenario observations, 100 distinct seeds, nine scenarios, and zero missing values. The original baseline at checkpoints 5–50 reproduces the earlier Validation 05 mean advantages.

**Mean firm-level output advantage of Guided over Random (%)**, averaging matched firm-level percentage differences first within seed and then across 100 seeds:

| Scenario | Round 5 | Round 10 | Round 20 | Round 50 | Round 100 |
|---|---:|---:|---:|---:|---:|
| Baseline (p=.20, radius=.10) | -1.8556 | -0.0032 | +1.1697 | +0.5893 | +0.2915 |
| Exploration p=.05 | -2.4708 | -0.9485 | +0.9168 | +0.6157 | +0.3062 |
| Exploration p=.10 | -2.2917 | -0.5550 | +1.0733 | +0.6214 | +0.3060 |
| Exploration p=.40 | -1.0348 | +0.4707 | +1.1499 | +0.5689 | +0.2833 |
| Exploration p=.60 | -0.4805 | +0.5185 | +0.9760 | +0.5092 | +0.2596 |
| Search radius=.03 | -4.0792 | -3.3587 | -0.7504 | +0.6228 | +0.3478 |
| Search radius=.05 | -3.2879 | -2.0799 | +0.3612 | +0.6626 | +0.3308 |
| Search radius=.20 | -0.2362 | +1.2703 | +1.1841 | +0.4667 | +0.2318 |
| Search radius=.30 | +0.1550 | +1.0254 | +0.8458 | +0.3547 | +0.1675 |

At round 50, the seed-mean advantage is positive in **92–100 of 100 seeds** depending on configuration (baseline: 100/100). At round 100, **92–100 of 100 seeds** are positive (baseline: 100/100). These are **seed-aggregated** outcomes, not counts of individual firms. At round 100, baseline seed-level standard deviation of the advantage is approximately **0.132 percentage points**.

**Interpretation and limits:** The Guided advantage at round 50 is positive under all nine prespecified parameter scenarios, but at round 20 it is negative with search radius .03. This indicates robustness of the *sign* at round 50 within the tested parameter grid, but not parameter-invariant speed of learning. Baseline mean advantage shrinks from +.5893% at round 50 to +.2915% at round 100, consistent with catch-up but not proof of equal asymptotic outcomes. This is one-factor-at-a-time sensitivity within a fixed model, not empirical validation, independent causal identification, or exhaustive robustness across parameter interactions.

### Factorial sensitivity — interaction test (pending run verification)

The prior one-factor-at-a-time sensitivity analysis cannot estimate parameter interactions. A complete **5 × 5 factorial design** was therefore added in [`experiments/game1_factorial_sensitivity.py`](../../../experiments/game1_factorial_sensitivity.py), with numerical structure tests in [`tests/test_game1_factorial_sensitivity.py`](../../../tests/test_game1_factorial_sensitivity.py) and a separate reproducibility workflow job. Source commits: `3df01403` (experiment), `8904af78` (tests), `d1965261` (CI).

Exploration probabilities: **0.05, 0.10, 0.20, 0.40, 0.60**. Search radii: **0.03, 0.05, 0.10, 0.20, 0.30**. All 25 combinations are run for 100 seeds (2026–2125), 20 firms, 100 rounds, and checkpoints 5/10/20/50/100. The Random benchmark is run **once per seed** and reused across the 25 Guided configurations, retaining the same matched schedule. Expected export: **250,000 paired firm–seed–checkpoint–parameter observations**.

The experiment saves `paired_factorial.csv`, `seed_factorial.csv`, `summary_factorial.csv`, `seed_interaction_contrast.csv`, and `metadata.json`. The prespecified interaction contrast at each checkpoint is **[advantage(0.60, 0.30) − advantage(0.05, 0.30)] − [advantage(0.60, 0.03) − advantage(0.05, 0.03)]**, calculated at the seed level. Positive values mean that increasing exploration probability has a more positive effect on Guided's relative advantage at the wider radius; negative values mean the reverse. This is an interaction **within the computational model**, not empirical causal identification.

**Status:** committed; numerical factorial findings and successful workflow completion **not yet verified**. The earlier one-factor-at-a-time results remain the only verified sensitivity evidence until the new artifact is inspected.

### Verified 5 × 5 factorial interaction results — 2026-10-31

**Provenance:** [GitHub Actions run 41163519868](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41163519868), successful, source commit `d19652616db396d0b83d046c68702b07d0e55b24`. Artifact `game1-factorial-d19652616db396d0b83d046c68702b07d0e55b24`, ID `13028770124`. ZIP/CSV files were inspected directly: 250,000 matched observations, 12,500 seed–scenario–checkpoint aggregates, 125 scenario–checkpoint summaries, 500 seed–checkpoint interaction contrasts, 100 seeds, **zero missing cells** in paired observations.

**Fraction of the 25 parameter configurations with positive mean Guided advantage:** round 5: 7/25; round 10: 12/25; round 20: 20/25; round 50: 25/25; round 100: 25/25. Positive mean across seeds does **not** mean every seed or firm benefits.

**Round-20 mean Guided-minus-Random output advantage (%), rows = exploration probability, columns = search radius:**

| p / radius | .03 | .05 | .10 | .20 | .30 |
|---|---:|---:|---:|---:|---:|
| .05 | -3.547 | -1.281 | +0.917 | +1.214 | +0.885 |
| .10 | -2.339 | -0.457 | +1.073 | +1.176 | +0.863 |
| .20 | -0.750 | +0.361 | +1.170 | +1.184 | +0.846 |
| .40 | +0.263 | +0.868 | +1.150 | +1.027 | +0.767 |
| .60 | +0.526 | +0.832 | +0.976 | +0.885 | +0.695 |

At round 50, the mean advantage ranges from **+0.2237% to +0.6626%** across 25 scenarios; at round 100, from **+0.1522% to +0.3502%**. The baseline `p=.20, radius=.10` reproduces the earlier result: **+1.1697%** at round 20, **+0.5893%** at round 50, **+0.2915%** at round 100.

**Prespecified corner interaction contrast** (percentage points): `[advantage(.60,.30)-advantage(.05,.30)]-[advantage(.60,.03)-advantage(.05,.03)]`.

| Round | Mean contrast (pp) | Approx. 95% seed-level CI (pp) |
|---|---:|---:|
| 5 | -3.6952 | [-4.0569, -3.3336] |
| 10 | -5.3112 | [-5.6845, -4.9379] |
| 20 | -4.2624 | [-4.6509, -3.8739] |
| 50 | -0.4478 | [-0.5689, -0.3268] |
| 100 | -0.0011 | [-0.0254, +0.0232] |

Intervals are descriptive uncertainty across 100 independent simulation seeds, using `mean ± 1.984 × seed-level SD/√100` (approximate t interval). The negative interaction in early rounds means increasing exploration probability is **more beneficial when the local search radius is narrow**; by round 100 the corner contrast is effectively zero at this resolution. This does not imply that the main effects or every other possible interaction are zero. Results establish sensitivity and nonadditivity **within the specified ABM**; they do not identify effects in observed firms. The corner contrast is only one predeclared summary of the full 5 × 5 response surface.

### Independent artifact audit — cross-horizon and economic invariants (2026-10-31)

**Scope:** Documentation-only independent read of GitHub Actions artifacts 13031790079 (50 rounds), 13031585631 (100), 13030944570 (200), all generated at source commit `40266bf38b644bb169fcb5d1358f9649ab7085cb`. No model code, algorithm, or economic parameter was changed.

**Cross-horizon verification, keyed by observation and tolerance 1e-10:**
- 50 vs 100: 500,000 paired rows and 1,000,000 firm-history rows matched.
- 50 vs 200: 500,000 paired rows and 1,000,000 firm-history rows matched.
- 100 vs 200: 1,000,000 paired rows matched.
- 100 vs 200: full 2,000,000 firm-history row comparison **not yet certified**. An order-insensitive row-hash check did not match; a targeted seed-2026 numeric comparison matched within ~5e-14, indicating that float representation can affect hashing. This is **unresolved**, not proof of either divergence or equivalence. A complete tolerance-based keyed comparison is required.

**Independent economic recalculation, all 2,000,000 paired rows (4,000,000 policy outputs), using fixed budget B=100 and existing production equations:**

| Technology | Feasible optimum capital share | Optimal output |
|---|---:|---:|
| Cobb-Douglas | 0.7000000000 | 54.2881452690 |
| Leontief | 0.7000000000 | 100.0000000000 |
| Linear | 0.9500000000 | 68.0000000000 |
| CES | 0.6375775139 | 52.8935719008 |

Maximum absolute error between recomputed and exported output: `4.2633e-14`; output efficiency percentage: `8.5265e-14`; distance to optimum share: `2.1077e-16`. Across both policies: **zero** allocation shares outside `[0.05,0.95]`, **zero** efficiencies above 100% (tolerance 1e-8), **zero** negative outputs.

**Interpretation:** The 200-round output and efficiency fields are arithmetically consistent with the approved production functions and constrained optima. This is a model-internal consistency check, **not** external empirical validation or proof of a novel mechanism. The 100-vs-200 full-history check remains open. No website work or Game 2 mechanism was introduced.

### Resolution: complete 100-vs-200 history audit (2026-10-31)

**Status: PASS.** Independent re-comparison of the original GitHub Actions artifacts `13031585631` (100 rounds) and `13030944570` (200 rounds) from source commit `40266bf3`. For each seed–policy block, the first 100 rounds of the 200-round artifact were compared with all 100 rounds of the 100-round artifact. This checked **2,000,000 firm-history rows, all 14 CSV columns**, preserving and checking firm, round, seed and policy identities.

- Zero mismatches in IDs, technology labels, policy labels, acceptance booleans, candidate shares, accepted shares, optimal shares, and share distances.
- Maximum absolute candidate/current output difference: `4.973799150320701e-14`.
- Maximum absolute efficiency difference: `9.947598300641403e-14`.
- **Zero mismatches at absolute tolerance `1e-10` (relative tolerance 0) across all 14 columns.**
- The earlier raw fingerprint mismatch was sensitive to floating-point representation; it is **resolved** by exhaustive numeric and categorical comparisons. Do not interpret a nonidentical byte hash as a simulation discrepancy.
- The previously verified 50-vs-100 and 50-vs-200 history checks, plus all three pairwise comparisons of paired firm-round records, remain unchanged.

**Audit boundaries:** This establishes cross-horizon consistency of exported trajectories; it is not evidence of real-world calibration, external validity, or publication readiness. Further methodological/statistical audit may be required before closing Game 1. No code, model parameters, or learning mechanism changed in this audit.

### Statistical-method audit of existing Game 1 results (2026-10-31)

**Scope:** Independent recalculation from the downloaded 200-round paired artifact `13030944570`, source commit `40266bf3`, with no code or model changes. The goal is to audit **existing descriptive results and their interpretation**, not to propose a paper contribution. There are 100 simulation seeds, each containing 100 firms (25 per technology), evaluated at 200 rounds. All reported 95% intervals below use a two-sided Student-t interval across **100 seed means**; they quantify seed-to-seed Monte Carlo variability conditional on fixed model parameters, not real-world uncertainty. When all seed means are identical, report the degenerate descriptive interval [0,0] rather than an undefined t interval.

| Round | Mean Guided advantage (% relative to Random) | 95% seed-level t interval | Seeds with positive advantage |
|---|---:|---:|---:|
| 1 | 0.0000 | [0.0000, 0.0000] | 0/100 |
| 5 | -1.8472 | [-2.0197, -1.6747] | 3/100 |
| 10 | -0.1833 | [-0.3214, -0.0451] | 42/100 |
| 11 | +0.0599 | [-0.0767, +0.1964] | 54/100 |
| 20 | +1.0386 | [+0.9724, +1.1048] | 100/100 |
| 50 | +0.6019 | [+0.5816, +0.6221] | 100/100 |
| 100 | +0.2939 | [+0.2822, +0.3055] | 100/100 |
| 200 | +0.1439 | [+0.1396, +0.1482] | 100/100 |

**Critical interpretation:** Round 11 is only the **first positive aggregate point estimate**, not a confidently established crossover: its 95% interval includes zero. At round 20 the mean is positive across all 100 seeds. The first positive *per-seed* round varies from 2 to 18 (median 11), so a single exact crossover time is not an invariant. These pointwise intervals do **not** adjust for selecting rounds post hoc or for simultaneous inference across 200 rounds.

**Technology heterogeneity at round 200** (mean relative advantage, 95% seed-level t interval): CES +0.003024% [0.002720,0.003327]; Cobb-Douglas +0.002029% [0.001861,0.002197]; Leontief +0.299476% [0.283629,0.315322]; Linear +0.270979% [0.260492,0.281466]. All 100 seed-level technology averages are positive in each group. Technology differences are descriptive for the four chosen functions and parameters; **do not** attribute them solely to elasticity of substitution.

**Threshold attainment at round 200:** The Guided minus Random percentage-point difference in firms attaining at least 95% efficiency is 0.00 pp [0.00,0.00]; at least 99% is +3.31 pp [2.99,3.63]; at least 99.9% is +24.32 pp [23.62,25.02]. These are **paired seed-level differences**, not differences in mean efficiency. The exact [0,0] at 95% is a degenerate observed simulation result, not proof of general equality under other configurations.

**Limitations and boundary of the completed audit:** (1) Firms within a seed are not treated as independent Monte Carlo replications; (2) policy comparison is paired on common seed/firm identifiers and matched random schedules, but different conditional branches may consume the same draws differently; (3) no adjustment for multiple rounds/technologies was made, so intervals are descriptive pointwise intervals; (4) the 100 seeds do not vary structural production parameters, firm composition, or learning hyperparameters; (5) no observed firm data are used, so empirical validity and generalizability remain unverified; (6) deterministic nondecreasing accepted output is imposed by the strict-improvement acceptance rule and is **not** an independently discovered economic finding; (7) reaching an efficiency threshold by round 200 is not universal convergence, and time-to-threshold observations may be right-censored. No additional algorithm or hypothesis is introduced.

**Status:** Statistical interpretation and seed-level interval arithmetic for the listed outcomes: **PASS**. Robustness to alternate structural assumptions and external validity: **NOT TESTED**; these are limits of the fixed baseline, not automatic prerequisites for extending Game 1. Full history and cross-horizon audit are separately recorded above. The audit script and machine-readable results are available in the conversation artifacts; this GitHub commit is documentation-only.

# Game 1 — Heterogeneous firms: empirical findings and literature alignment

**Status:** Simulation completed and CI verified; literature alignment is theoretical/contextual, not a claim of exact empirical replication.  
**Branch:** `experiment/game1-heterogeneous-firms`  
**Source commit:** `797361d5c804ac03b9baabf2bb187f08408c7bf2`  
**CI:** [GitHub Actions run 41204620746](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41204620746) (all 3 horizon jobs successful; 241 tests passed per job).  
**Experiment:** `experiments/game1_heterogeneous.py`; 100 firms, 25 per production family, 100 learning seeds (2026–2125), fixed population seed 2026, Random vs Guided with matched randomness, 50/100/200 rounds. Productivity fixed at A=1; 50 firms have alpha<0.5 and 50 alpha>0.5. 

## 1. Measurement and observed results

Firm efficiency (%) = 100 × final firm output / that firm's own feasible optimal output (capital-share bounds [0.05, 0.95]). Reported treatment effect is the **paired difference in efficiency percentage points**, Guided minus Random, averaged first over firms within a learning seed and then across 100 learning seeds. This is **not** a percent change in output.

| Rounds | Mean Guided − Random (pp) | Seed-level SE (pp) | Approximate normal 95% CI (pp) |
|---:|---:|---:|---|
| 50 | +0.4821336 | 0.0107227 | [0.4611170, 0.5031502] |
| 100 | +0.2417890 | 0.0048230 | [0.2323358, 0.2512422] |
| 200 | +0.1213950 | 0.0026522 | [0.1161967, 0.1265933] |

**Source:** `summary.json` printed in GitHub Actions logs for the three horizon jobs; associated CSVs and metadata are retained as workflow artifacts.

### Finding F1 — Guided learning outperforms random learning at the measured horizons

All three paired mean differences are positive and the model-conditional, seed-level approximate 95% confidence intervals exclude zero. **Interpretation:** exploiting own search history can improve allocation efficiency under these specific production functions, decision rules and sampling assumptions. **Not established:** universal superiority for all learning algorithms, parameter choices or real firms.

### Finding F2 — The relative advantage shrinks with longer search

The advantage decreases from +0.4821 pp (50 rounds) to +0.2418 pp (100) to +0.1214 pp (200), a roughly halving pattern when the horizon doubles. This is a **descriptive pattern at only three measured horizons**, not a fitted convergence law. The experiment reports terminal differences, not the mechanism causing them. In particular, a declining gap does **not** mean Guided's absolute efficiency falls.

### Finding F3 — A positive gap remains at 200 rounds

The mean difference is +0.1214 pp with approximate 95% CI [0.1162, 0.1266]. This is a conditional simulation result; no assertion of a permanently positive asymptotic gap is warranted.

### Finding F4 — Approximate halving across doubling horizons

Ratios of observed mean gaps are close to one-half at 50→100 and 100→200. This may motivate a new test of horizon scaling, but **three points cannot establish a general mathematical rate**. Do not describe this as a discovered universal law.

## 2. Literature alignment — calibrated claims only

| Simulation finding | Literature | What is supported / not supported |
|---|---|---|
| F1: Guided > Random at measured horizons | Nelson & Winter (1982); March (1991) | Consistent with organizational adaptation and learning from experience. Neither source proves this particular algorithm will beat the Random benchmark in every setting. |
| F2: advantage diminishes as rounds increase | March (1991); Levinthal (1997) | Consistent with exploration–exploitation tradeoffs and adaptive search. These sources do **not** establish the specific decreasing trajectory or its cause in this model. |
| F3: positive residual advantage at 200 rounds | Nelson & Winter (1982); March (1991) | Compatible with the value of accumulated learning, but not evidence of an asymptotically persistent advantage. |
| F4: gap roughly halves when horizon doubles | No directly matching literature established in this review | Treat as a simulation-specific descriptive regularity pending more horizons, seeds, alternative populations and model comparisons. |

### References

1. Nelson, R. R., & Winter, S. G. (1982). *An Evolutionary Theory of Economic Change*. Harvard University Press.
2. March, J. G. (1991). Exploration and exploitation in organizational learning. *Organization Science, 2*(1), 71–87. https://doi.org/10.1287/orsc.2.1.71
3. Levinthal, D. A. (1997). Adaptation on rugged landscapes. *Management Science, 43*(7), 934–950. https://doi.org/10.1287/mnsc.43.7.934

**Reference scope:** These are conceptual/theoretical comparisons, not papers that reproduce our exact heterogeneous-firm experiment. No claim is made that a systematic literature review has established novelty or consensus.

## 3. What has not yet been established

- **Production-family heterogeneity:** Although 25 firms per Cobb–Douglas, Leontief, Linear and CES family were simulated, the new experiment's aggregate CI logs do not report within-family treatment effects. Do not transfer results from the earlier homogeneous-parameter experiment to this one.
- **Capital/labor orientation:** No reported effect breakdown by alpha stratum yet.
- **Population robustness:** All 100 learning replications use the same population seed 2026. The intervals reflect learning-seed variability **conditional on that population**, not population uncertainty.
- **Mechanism and convergence:** Terminal outcomes alone do not demonstrate why the advantage shrinks, prove full convergence, or rule out alternative learning dynamics.
- **External validity:** No causal claim about actual firms or inter-firm knowledge transfer; Game 1 models independent learning.

## 4. Research assessment

The aggregate findings are **compatible with established learning and adaptive-search literature**, rather than independently demonstrating a novel economic mechanism. The potential contribution of the broader project remains in whether **heterogeneous production structures change the benefits of independent learning, competitive observation and voluntary inter-firm knowledge sharing**. Those later claims require separate Game 1 subgroup analysis and Games 2–3 experiments.

**Next validation:** analyze artifact-level outcomes by production family and alpha stratum; test multiple population seeds and additional horizons before claiming a scaling law or generalizable heterogeneity effect.


## 5. Additional verified subgroup findings — run 41208233687

**Provenance:** https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41208233687 ; source commit `6d35db1d2648f48c97649dd20a9d39ea99d8477c`; 241 passing tests per horizon and successful `Analyze heterogeneity by technology and alpha strata` step. Log output from `experiments/analyze_game1_heterogeneous.py`; archived `subgroup_summary.json` in each artifact (50: `13045251660`, 100: `13045641439`, 200: `13045171930`). These are **seed-aggregated descriptive point estimates**; subgroup uncertainty, contrast tests and independent recalculation from raw files remain pending.

| Family (Guided − Random, efficiency pp) | 50 | 100 | 200 |
|---|---:|---:|---:|
| Leontief | 1.065522 | 0.546084 | 0.281898 |
| Linear | 0.794978 | 0.403008 | 0.198807 |
| CES | 0.038901 | 0.010860 | 0.002806 |
| Cobb-Douglas | 0.029134 | 0.007204 | 0.002069 |

**F5:** The Guided advantage is strongly associated with production-function family in the simulated fixed population, largest for Leontief and Linear. Do not attribute the difference solely to substitution elasticity without controlled counterfactuals. These results differ from the historical homogeneous-parameter report and should not be pooled across experiments.

| Alpha stratum (Guided − Random, efficiency pp) | 50 | 100 | 200 |
|---|---:|---:|---:|
| strong_labor | 0.631088 | 0.314019 | 0.168610 |
| strong_capital | 0.595552 | 0.295946 | 0.143731 |
| moderate_labor | 0.334795 | 0.182395 | 0.085785 |
| moderate_capital | 0.345235 | 0.164263 | 0.081658 |

**F6:** Strongly labor-/capital-oriented alpha strata have greater average Guided advantage than moderate strata at each observed horizon. The comparisons can be confounded by technology-family composition and the chosen alpha distributions. No formal cross-group contrasts or multi-population robustness yet.

### New evidence and next tests
- Verify exact subgroup CIs and arithmetic directly from artifact CSV/JSON, not just CI text.
- Estimate within-family effects of alpha orientation/strength (family × stratum) to disentangle composition.
- Repeat independent population seeds; then test fixed-alpha-controlled, family-specific search landscapes.
- The literature statements in §2 remain conceptual; F5/F6 currently are not independently matched against a direct empirical study.



### Literature support for F5 and F6

**Evidence standard:** The following sources support theoretical mechanisms or adjacent research questions; they do **not** directly reproduce the four-family ranking or the strong-versus-moderate alpha differences. These are interpretive connections, not empirical validation or established novelty.

- **F5 — production-function heterogeneity and learning advantage.** Levinthal (1997) studies adaptation on rugged landscapes and explains why search performance depends on the structure of the problem. March (1991) discusses exploration/exploitation trade-offs in organizational learning. Neither paper directly compares Guided and Random search across Cobb–Douglas, CES, Leontief and Linear production functions. Production-function curvature, kinks and feasible optima are plausible mechanisms to test, not established causes from these runs.
- **F6 — alpha orientation/strength and learning advantage.** The same adaptive-search framework provides indirect motivation for the importance of starting positions and opportunity landscapes. It does **not** predict the observed strong-alpha > moderate-alpha ordering in this experiment. Family composition and baseline distance to the optimum require within-family controls.
- **Novelty boundary:** Existing learning/search literature is consistent with heterogeneous performance; the precise simulated rankings remain conditional findings, pending multi-population robustness and independent literature comparison.

**References**
1. March, J. G. (1991). Exploration and exploitation in organizational learning. *Organization Science*, 2(1), 71–87. https://doi.org/10.1287/orsc.2.1.71
2. Levinthal, D. A. (1997). Adaptation on rugged landscapes. *Management Science*, 43(7), 934–950. https://doi.org/10.1287/mnsc.43.7.934
3. Rivkin, J. W. (2000). Imitation of complex strategies. *Management Science*, 46(6), 824–844. https://doi.org/10.1287/mnsc.46.6.824.11940

**Documentation policy:** Every future simulation finding should include (a) quantitative observation and provenance, (b) mechanism hypothesis, (c) direct/indirect/absent literature support, (d) limitations and falsification tests, and (e) verifiable full references. Never equate theoretical consistency with direct replication.


## 6. F7 — Within-production-family alpha-strength contrasts (2026-10-31)

**Artifact and CI provenance:** GitHub Actions run [41209080758](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41209080758), source commit `f4faf8e78dce70d6384710f10cf79931be3cf131`, workflow `game1-heterogeneous-horizons.yml`. All horizon jobs (50, 100, 200 rounds) passed 241 tests and subgroup-analysis and export steps. Artifacts: 50 rounds `13045623552`, 100 rounds `13045442487`, 200 rounds `13046030465`. Source: `experiments/analyze_game1_heterogeneous.py`; `subgroup_summary.json` (section `within_technology_strength_contrast`). Listed point estimates independently checked against job logs, **not yet independently recalculated from underlying CSVs**.

Contrast per family and learning seed: mean(Guided minus Random efficiency in percentage points | strong alpha stratum) minus mean(Guided minus Random efficiency in percentage points | moderate alpha stratum). Averages and nominal normal-approximation intervals use the 100 matched learning-seed contrasts. The population is fixed at seed 2026; uncertainty across population draws is not represented.

| Production function | 50 rounds (pp) | 100 rounds (pp) | 200 rounds (pp) |
|---|---:|---:|---:|
| CES | +0.019874 | +0.002336 | +0.000857 |
| Cobb-Douglas | +0.015543 | +0.002694 | +0.000673 |
| Leontief | +0.070384 | +0.024164 | +0.043135 |
| Linear | +0.987419 | +0.497421 | +0.245131 |

**F7 (descriptive):** Within all four production-function families, strong alpha strata have a greater *mean* Guided advantage than moderate strata at every analyzed horizon. The magnitude is concentrated in Linear firms, suggesting an important interaction between production technology and alpha orientation. This is not a claim of statistical significance or causal identification; subgroup confidence interval endpoints are stored in the artifacts and remain to be independently inspected. In particular the smaller CES/Cobb-Douglas differences must not be described as significant without uncertainty checks. The contrast can also reflect distance from optima, the geometry of the feasible share interval, and the specified random/guided algorithms.

### Literature support and boundaries

- **Theoretical / indirect:** Levinthal (1997) argues that adaptation depends on the structure of the fitness landscape; this motivates comparing search rules across different production-function geometries.
- **Theoretical / indirect:** March (1991) examines exploration and exploitation in organizational learning, supporting the study of heterogeneous learning outcomes across decision environments.
- **Related computational mechanism:** Rivkin (2000) studies imitation of complex strategies; it speaks to the importance of problem complexity for learning but **does not directly test** our strong-versus-moderate alpha contrasts.
- **Direct verification:** No cited paper establishes the numerical ordering in this simulation. Do not claim direct literature replication or originality without targeted systematic review.

**Full references**

1. March, J. G. (1991). Exploration and exploitation in organizational learning. *Organization Science*, 2(1), 71–87. https://doi.org/10.1287/orsc.2.1.71
2. Levinthal, D. A. (1997). Adaptation on rugged landscapes. *Management Science*, 43(7), 934–950. https://doi.org/10.1287/mnsc.43.7.934
3. Rivkin, J. W. (2000). Imitation of complex strategies. *Management Science*, 46(6), 824–844. https://doi.org/10.1287/mnsc.46.6.824.11940

**Open validation gates:** Extract and independently recompute CSV-derived contrasts and seed-level intervals; distinguish effects of strength from absolute alpha and distance-to-optimum; vary population seeds; avoid simultaneous or empirical-firm inference from model-conditional intervals.


### F7 nominal 95% confidence intervals — verified run 41209602330

**Source:** [GitHub Actions 41209602330](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41209602330), source commit `689398eae79de03f8740f29b1b81889f48414156`; job logs and subgroup artifact JSON (`within_technology_strength_contrast`). All three jobs succeeded with 241 passed tests per job. Artifact IDs: 50=`13045383255`, 100=`13046090992`, 200=`13045896634`. CIs are nominal normal-approximation 95% intervals using 100 paired learning-seed contrasts; fixed population seed=2026, not across-population uncertainty and no multiple-comparison adjustment.

| Technology | 50 rounds contrast [95% CI] pp | 100 rounds contrast [95% CI] pp | 200 rounds contrast [95% CI] pp |
|---|---|---|---|
| CES | +0.019874 [+0.012564, +0.027185] | +0.002336 [+0.000239, +0.004434] | +0.000857 [+0.000266, +0.001448] |
| Cobb-Douglas | +0.015543 [+0.008790, +0.022296] | +0.002694 [+0.001347, +0.004040] | +0.000673 [+0.000310, +0.001036] |
| Leontief | +0.070384 [-0.069812, +0.210580] | +0.024164 [-0.037592, +0.085921] | +0.043135 [+0.007365, +0.078904] |
| Linear | +0.987419 [+0.909657, +1.065180] | +0.497421 [+0.459952, +0.534890] | +0.245131 [+0.226854, +0.263409] |

**Interpretation:** All mean contrasts are positive. Nominal 95% intervals exclude zero for Linear, CES and Cobb-Douglas at all three horizons, and for Leontief only at 200 rounds. Thus the earlier F7 wording should be understood as a descriptive sign pattern rather than universal statistically distinguishable effects. CES and Cobb-Douglas magnitudes at 200 rounds are especially small in economic terms. This is exploratory analysis; inference is conditional on the single fixed population, and intervals do not account for simultaneous tests or alternative population seeds.

**Literature support (indirect only):** March (1991) explains exploration/exploitation in organizational learning; Levinthal (1997) studies adaptation on rugged fitness landscapes; Rivkin (2000) examines imitation of complex strategies. These motivate examining heterogeneous search performance; none directly confirms the observed family-specific alpha-strength contrasts. Full bibliographic entries and DOI links are given in the F7 Literature section above.

**Next validation:** Independently recompute CIs from artifact CSVs; vary population seed and report across-population uncertainty; assess whether the strong-minus-moderate contrast reflects distance to the feasible optimum and family-specific search geometry.


## 7. Pre-registered population-seed sensitivity protocol (pending execution)

**Question:** Are F5 (technology ranking) and F6/F7 (strong-minus-moderate alpha effects within technology) robust to independently generated heterogeneous firm populations, rather than just the fixed population seed 2026?

**Scope and governance:** Exploratory robustness replication of the existing Game 1 experiment. No change to firm production functions, budgets, candidate search, acceptance rule, Random/Guided policies, learning-seed matching, technology quotas or horizons. Changing the population seed changes only the population draw. Do not describe a successful pipeline as independent statistical validation.

**Design:** Keep 100 firms, 25 per production technology, four alpha strata with existing quota rules, 100 matched learning seeds 2026–2125, 50/100/200 rounds. Population seeds: `2026, 2027, 2028, 2029, 2030` (five pre-specified draws). Each population is evaluated with identical learning-seed IDs and matched policies. Preserve outputs separately under `results/population_sensitivity/population_<seed>/horizon_<rounds>/`; do not overwrite historical artifacts. Original population 2026 serves as the reference.

**Primary outcomes:** (1) family-specific mean Guided-minus-Random efficiency in percentage points, (2) within-family Strong-minus-Moderate contrasts in percentage points, (3) ranking stability of family effects, especially Linear/Leontief versus CES/Cobb-Douglas. Secondary: overall mean advantage, absolute Guided and Random efficiency levels, and sign stability across horizons.

**Uncertainty and independence:** Compute per-learning-seed paired differences within each population first. Summarize per-population effects separately, then report dispersion and range **across five population draws**. Reusing learning seeds across populations may induce correlation; do not treat 500 population×learning-seed observations as 500 independent populations. Five draws give exploratory sensitivity, not a precise population-level confidence interval. Existing 95% CIs conditional on one population remain separate.

**Validation gates:** Run smoke tests on small seed counts; verify 100 firms/25 per technology, quotas, 20,000 final and 10,000 paired rows per full population×horizon, unique seed/firm keys, correct alpha strata, and matched Random/Guided comparisons. Preserve source SHA, dependency versions, seeds, raw CSVs, subgroup summaries, and CI artifact IDs. Compare population=2026 to previously published results within numeric tolerance. Do not claim robustness if ranking/sign reverses; report all reversals.

**Literature and interpretation:** March (1991) and Levinthal (1997) motivate heterogeneity in adaptive search; Nelson & Winter (1982) motivates firm-level evolutionary heterogeneity. None directly establishes population-seed invariance. Bibliography and DOI for March/Levinthal are listed above; Nelson, R. R., & Winter, S. G. (1982). *An Evolutionary Theory of Economic Change*. Harvard University Press. This protocol is methodological, not a new finding.

**Status:** protocol registered, experiment not yet executed. Because the expanded experiment uses 5 populations × 3 horizons × 100 learning seeds, it should be implemented as a separate, manually dispatched workflow with a smoke-test gate and no automatic execution on documentation commits.


## 8. Population-seed sensitivity — full Monte Carlo results (2026-10-31)

**Provenance:** [GitHub Actions run 41210955389](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41210955389); workflow definition commit on main `99b1a89f9a5894c22b966a5fa6216efb0290efeb`; checkout branch `experiment/game1-heterogeneous-firms`. Each of 15 matrix jobs completed successfully, reported **241 passed tests** and `learning_seeds=100`, and uploaded a separate artifact (see run's artifacts tab). Five population seeds `2026,2027,2028,2029,2030`, horizons `50,100,200`; policies Random/Guided matched within learning seed; no economic mechanism change. **Source of numeric estimates: CI job logs; they have not yet been independently recomputed from downloaded CSVs.**

### F5: technology-family Guided minus Random advantage across populations

All entries in percentage points (pp), each an average over 100 matched learning seeds in the given population.

| Population seed | Horizon | Leontief | Linear | CES | Cobb-Douglas |
|---|---:|---:|---:|---:|---:|
| 2026 | 50 | 1.065522 | 0.794978 | 0.038901 | 0.029134 |
| 2027 | 50 | 1.084781 | 0.747117 | 0.033941 | 0.036045 |
| 2028 | 50 | 1.038166 | 0.796234 | 0.040531 | 0.025848 |
| 2029 | 50 | 1.060544 | 0.776572 | 0.042786 | 0.029170 |
| 2030 | 50 | 0.980919 | 0.725821 | 0.037831 | 0.031414 |
| 2026 | 100 | 0.546084 | 0.403008 | 0.010860 | 0.007204 |
| 2027 | 100 | 0.600572 | 0.382583 | 0.010081 | 0.008713 |
| 2028 | 100 | 0.551906 | 0.404219 | 0.010948 | 0.007282 |
| 2029 | 100 | 0.578986 | 0.393120 | 0.011554 | 0.007519 |
| 2030 | 100 | 0.546681 | 0.366493 | 0.010977 | 0.009739 |
| 2026 | 200 | 0.281898 | 0.198807 | 0.002806 | 0.002069 |
| 2027 | 200 | 0.298658 | 0.189096 | 0.002651 | 0.002190 |
| 2028 | 200 | 0.294370 | 0.200971 | 0.002660 | 0.001851 |
| 2029 | 200 | 0.292757 | 0.192325 | 0.002838 | 0.002016 |
| 2030 | 200 | 0.285503 | 0.177439 | 0.002778 | 0.002425 |

**F5 sensitivity conclusion:** Leontief > Linear > both CES and Cobb-Douglas is preserved in all 15 cells; CES versus Cobb-Douglas may reverse and must not be described as stable. All family effects are positive in the tested cells; magnitudes shrink with longer horizons. These are model-conditional, descriptive across only five independently drawn populations.

### F7: within-family Strong minus Moderate Guided advantage

Values (pp), one estimate per population seed; selected table at the 200-round horizon:

| Technology | pop=2026 | pop=2027 | pop=2028 | pop=2029 | pop=2030 |
|---|---:|---:|---:|---:|---:|
| Linear | +0.245131 | +0.218565 | +0.212059 | +0.229574 | +0.155182 |
| Leontief | +0.043135 | +0.075178 | +0.023144 | +0.007525 | +0.053706 |
| Cobb-Douglas | +0.000673 | +0.000845 | +0.000601 | +0.000926 | +0.000922 |
| CES | +0.000857 | +0.000673 | +0.000676 | +0.001030 | **-0.000199** |

**F7 sensitivity conclusion:** Linear has positive contrasts at all 15 population-by-horizon combinations, with nominal learning-seed 95% CIs excluding zero in all 15. Cobb-Douglas point estimates are also positive in all 15 but often economically tiny; nominal CI exclusions are not multiple-comparison adjusted. Leontief point contrasts are positive across all 15 but its conditional learning-seed CIs include zero in many cells. CES turns negative at population 2030/horizon 200, with nominal CI [-0.000774, +0.000375] including zero. **Thus strong-orientation superiority must not be stated as universal** across technology, horizon, and population draw.

**F6 status:** Earlier pooled-stratum findings do not by themselves isolate production technology; interpret alongside the within-family F7 results rather than as a broad causal effect of alpha.

### Inference and literature support

Each population has the same fixed quotas and the same learning-seed IDs, giving a controlled sensitivity design but not empirical sampling of real firms. Across-population uncertainty is based on only **five population draws**; learning-seed 95% CIs are **conditional on each population**. Do not treat 500 population×learning-seed combinations as 500 independent population replicates, infer population-level significance from these CIs, or ignore multiple comparisons. This is exploratory computational robustness evidence, not identification or proof of universal behavioral laws.

**Indirect theoretical support (not replication of numerical findings):**
- March, J. G. (1991). Exploration and exploitation in organizational learning. *Organization Science*, 2(1), 71–87. https://doi.org/10.1287/orsc.2.1.71 — exploration/exploitation motivates alternative adaptive search policies but does not predict our specific signs or magnitudes.
- Levinthal, D. A. (1997). Adaptation on rugged landscapes. *Management Science*, 43(7), 934–950. https://doi.org/10.1287/mnsc.43.7.934 — landscape geometry supports studying production-function differences, without validating our ranking.
- Nelson, R. R., & Winter, S. G. (1982). *An Evolutionary Theory of Economic Change*. Harvard University Press — theoretical rationale for heterogeneous firm behavior and evolutionary adaptation, not numerical evidence for F5/F7.
- Rivkin, J. W. (2000). Imitation of complex strategies. *Management Science*, 46(6), 824–844. https://doi.org/10.1287/mnsc.46.6.824.11940 — computational study relevant to learning complexity, but does not directly test these within-production-family alpha contrasts.

**Outstanding audit gates (updated after Section 9):** Independent raw-CSV recomputation and population-range reporting are completed in Section 9. Search-geometry mechanisms, multiplicity implications and website provenance are still pending. Game 1 heterogeneous extension **not signed off**.


## 9. Independent raw-artifact audit — PASSED (2026-10-31)

**Audit run:** https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41212931829
**Original simulation run:** https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41210955389
**Audit method:** `experiments/audit_game1_population_artifacts.py` independently recomputes matched Guided-minus-Random effects and normal-approximation 95% seed-level intervals using the Python standard library, and checks original subgroup summaries. Workflow downloaded 15 original artifacts, validated 150,000 paired rows / 300,000 final rows and unique keys, and uploaded `audit_report.json`. The audit job completed successfully with the marker `INDEPENDENT AUDIT PASSED`. The numeric results below are taken from its recomputation logs, not copied from the earlier subgroup-analysis logs.

### Overall mean efficiency advantage, across five population seeds

Unit: **percentage points** (Guided minus Random). Range is the minimum-to-maximum *population-level point estimate*, **not** a 95% confidence interval.

| Horizon | Cross-population mean | Minimum | Maximum |
|---|---:|---:|---:|
| 50 | +0.470812735 | +0.443996250 | +0.482133625 |
| 100 | +0.243426467 | +0.233472502 | +0.250487330 |
| 200 | +0.121805504 | +0.117036540 | +0.124962992 |

### F5 independently verified mean/range across populations

Each cell is `mean [minimum, maximum]` in pp.

| Family | 50 rounds | 100 rounds | 200 rounds |
|---|---|---|---|
| Leontief | 1.045986 [0.980919, 1.084781] | 0.564846 [0.546084, 0.600572] | 0.290637 [0.281898, 0.298658] |
| Linear | 0.768144 [0.725821, 0.796234] | 0.389885 [0.366493, 0.404219] | 0.191728 [0.177439, 0.200971] |
| CES | 0.038798 [0.033941, 0.042786] | 0.010884 [0.010081, 0.011554] | 0.002747 [0.002651, 0.002838] |
| Cobb-Douglas | 0.030322 [0.025848, 0.036045] | 0.008091 [0.007204, 0.009739] | 0.002110 [0.001851, 0.002425] |

The F5 hierarchy **Leontief > Linear > CES and Cobb-Douglas** holds across all 15 population×horizon combinations, but CES vs Cobb-Douglas is not invariant.

### F7 independently verified population variation

Strong-minus-Moderate within-family contrasts; each cell is `mean [minimum, maximum]` across population seeds in pp.

| Family | 50 rounds | 100 rounds | 200 rounds |
|---|---|---|---|
| Linear | 0.859993 [0.690723, 0.987419] | 0.436069 [0.345948, 0.497421] | 0.212102 [0.155182, 0.245131] |
| Leontief | 0.126608 [0.069159, 0.264867] | 0.051565 [0.011585, 0.088919] | 0.040537 [0.007525, 0.075178] |
| CES | 0.015830 [0.006469, 0.026549] | 0.003219 [0.002336, 0.005902] | 0.000607 [-0.000199, 0.001030] |
| Cobb-Douglas | 0.017071 [0.012611, 0.023932] | 0.003650 [0.002694, 0.004898] | 0.000794 [0.000601, 0.000926] |

For 200 rounds, F7 point estimate is positive in 5/5 populations for Linear, Leontief and Cobb-Douglas, but 4/5 for CES. The 2030-CES point estimate is -0.000199 pp, with its within-population nominal CI covering zero. These are **descriptive sensitivity results** over five population draws, not population-level inference. The audit reproduces conditional learning-seed CIs; it does not implement a new five-population confidence interval, multiplicity correction, or a mechanism-identification test.

**Audit status change:** The original independent raw-CSV recalculation and across-population range reporting gates have now **passed**. Remaining issues are mechanism / search geometry interpretation, multiple testing / substantive materiality, and independent website provenance and visualization checks. **Heterogeneous Game 1 remains conditionally validated, not globally signed off.**

**Literature support and interpretation:** This audit is a computational consistency check, not a new literature claim. March (1991, doi:10.1287/orsc.2.1.71), Levinthal (1997, doi:10.1287/mnsc.43.7.934), Rivkin (2000, doi:10.1287/mnsc.46.6.824.11940), and Nelson & Winter (1982) remain conceptual support only; they do not empirically validate numerical effects or establish causal mechanisms in this simulation.


## 10. Alpha-extremity diagnostic — descriptive association (2026-11-01)

**Run:** https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41261382309
**Source:** independently audited full experiment artifacts from run 41210955389. The diagnostic groups firms by absolute distance `|alpha - 0.5|` into **near** [0,0.1], **intermediate** (0.1,0.2], and **extreme** (0.2,0.4]. Reported numbers are means of per-population effects, across five population draws and 100 matched learning seeds per draw; min–max ranges in log refer to population point estimates, *not confidence intervals*. The diagnostic workflow succeeded and uploaded artifact `game1-alpha-geometry-diagnostic-6d642d963dc866385b24fe0d1f8afc17d7330933` (artifact ID 13065671080).

### Guided minus Random efficiency advantage by alpha-extremity band

Each table entry is in percentage points; column order is near / intermediate / extreme.

| Horizon | Technology | Near | Intermediate | Extreme |
|---|---|---:|---:|---:|
| 50 | CES | 0.030567 | 0.044777 | 0.047338 |
| 50 | Cobb-Douglas | 0.021445 | 0.028434 | 0.043686 |
| 50 | Leontief | 0.980150 | 1.106245 | 1.101820 |
| 50 | Linear | 0.320948 | 0.817764 | 1.381076 |
| 100 | CES | 0.009210 | 0.011258 | 0.012957 |
| 100 | Cobb-Douglas | 0.006193 | 0.007280 | 0.011271 |
| 100 | Leontief | 0.538032 | 0.561798 | 0.606505 |
| 100 | Linear | 0.163129 | 0.418118 | 0.695670 |
| 200 | CES | 0.002431 | 0.002588 | 0.003303 |
| 200 | Cobb-Douglas | 0.001698 | 0.001809 | 0.002845 |
| 200 | Leontief | 0.269558 | 0.297693 | 0.318543 |
| 200 | Linear | 0.081435 | 0.198853 | 0.344897 |

**Interpretation:** Absolute alpha-extremity is positively associated with Guided-minus-Random efficiency in Linear, CES, and Cobb-Douglas, and generally in Leontief; Leontief at 50 rounds has an intermediate estimate (1.106245 pp) slightly above extreme (1.101820 pp). The pronounced Linear difference at 100 rounds is 0.695670 / 0.163129 ≈ 4.26 in relative magnitude, but all effects are descriptive, model-conditional and should be interpreted in absolute percentage points rather than ratios alone.

**Mechanism NOT identified:** Alpha-extremity is not the measured initial distance-to-optimum, not a measure of landscape curvature or Leontief kink proximity, and not a randomized causal treatment. The same five fixed-quota population seeds were analyzed, and unequal band sizes can matter. No baseline-distance matching, geometric derivative decomposition, multiplicity correction, or out-of-sample firm distribution has been established. **Do not conclude alpha extremity causes the learning-policy advantage or explains the family ranking.** The appropriate next test is to calculate firm-level initial optimality gap and feasible optimum allocation from the **existing production functions without changing the simulation**, then examine whether alpha-extremity still predicts the policy gap after stratifying on initial optimality gap; report where those terms overlap mechanically and avoid causal language.

**Literature support (conceptual only):** March (1991), *Organization Science* 2(1), 71–87, doi:10.1287/orsc.2.1.71, and Levinthal (1997), *Management Science* 43(7), 934–950, doi:10.1287/mnsc.43.7.934, motivate adaptive search and landscape sensitivity, but do not predict these band-specific numbers or identify the mechanism.


## 11. Initial optimality gap diagnostic — PASSED (2026-11-01)

**Run:** https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41262695753. Original paired data: run 41210955389. Analytical script: `experiments/diagnose_game1_initial_gap.py`. GitHub Actions successfully processed 5 population seeds × 3 horizons × 4 production functions = 60 diagnostic cells and uploaded artifact ID `13064954927`. No production function, behavioral rule, or random seed was changed.

The starting capital share is `s0=0.5`. The optimum `s*` is determined by `optimal_capital_share`, and `Y*` by `optimal_output`. Define `initial_gap_pp = 100 * (1 - Y(s0)/Y*)`. The measure reflects *remaining initial efficiency potential*, not distance in capital-share units. Alpha extremity, share-distance and this output-efficiency gap are distinct descriptors; all are mathematically tied to technology and alpha, so they must not be interpreted as causally independent covariates.

### Association between initial efficiency gap and learning advantage

Table reports **mean within-population firm-level Pearson r** between initial gap and firm's across-learning-seed mean `Guided - Random` efficiency advantage. Each population has 25 firms per technology; values are averaged across five populations. These are **not** pooled-firm correlations or inferential confidence intervals.

| Production family | 50 rounds | 100 rounds | 200 rounds |
|---|---:|---:|---:|
| Linear | 0.989938 | 0.987281 | 0.982209 |
| Cobb-Douglas | 0.771042 | 0.796574 | 0.772178 |
| CES | 0.469291 | 0.470527 | 0.435426 |
| Leontief | 0.292394 | 0.274866 | 0.372533 |

### Mean Guided-minus-Random advantage by initial-gap tertile

Values are **percentage points**, aggregated across five populations, with tertiles defined *within each technology and population*. They are descriptive comparisons, not controlled interventions.

| Horizon | Technology | Low gap | Medium gap | High gap |
|---|---|---:|---:|---:|
| 50 | CES | 0.024677 | 0.044423 | 0.047285 |
| 50 | Cobb-Douglas | 0.018748 | 0.029046 | 0.043157 |
| 50 | Leontief | 0.939778 | 1.089180 | 1.108925 |
| 50 | Linear | 0.247431 | 0.691694 | 1.364592 |
| 100 | CES | 0.008542 | 0.011120 | 0.012988 |
| 100 | Cobb-Douglas | 0.005944 | 0.007085 | 0.011242 |
| 100 | Leontief | 0.525893 | 0.564881 | 0.603716 |
| 100 | Linear | 0.127124 | 0.348971 | 0.693194 |
| 200 | CES | 0.002386 | 0.002578 | 0.003275 |
| 200 | Cobb-Douglas | 0.001673 | 0.001852 | 0.002806 |
| 200 | Leontief | 0.266863 | 0.288004 | 0.317013 |
| 200 | Linear | 0.062364 | 0.171310 | 0.341330 |

**Interpretation:** Higher initial efficiency gap is associated with a greater Guided advantage across all four production technologies, with especially strong near-monotone relationship in Linear; strong but smaller relationship in Cobb-Douglas, weaker in CES, and weakest in Leontief at the 100-round horizon. The coefficients and gaps represent within-model descriptive patterns only. They neither establish a causal mediation claim nor identify a general law of firm adaptation.

**Important mechanical constraint:** Under this specific allocation model with `s0=0.5`, Linear has `s*=0.05` or `0.95` for every `alpha != 0.5`. Thus share-distance has zero within-family variation, and its Pearson correlation is correctly undefined (`null` in the diagnostic); the substantial Linear gap variation arises from variation in output loss due to alpha, *not* variation in share distance. Likewise, `s*=alpha` for Cobb-Douglas and Leontief, so share distance mechanically coincides with alpha extremity. This distinction limits causal interpretation of regression controls.

**Next mechanism test:** Under the existing models, derive/simulate policy-specific search paths and candidate distributions by production function and initial gap. For Linear, test whether the location of the boundary optimum interacts with Guided's local search radius and 20% uniform exploration; for Leontief, assess kink proximity; for smooth CES and Cobb-Douglas, assess diminishing marginal gains near smooth optima. Record hypotheses and estimates without changing Game 1's economic rules. Because 15 population/horizon cells and many subgroup contrasts were inspected, document exploratory status and multiplicity risks; avoid population-level inference from only five population draws.

**Literature framing (conceptual, not numerical replication):** March (1991), *Organization Science* 2(1), 71–87, https://doi.org/10.1287/orsc.2.1.71; Levinthal (1997), *Management Science* 43(7), 934–950, https://doi.org/10.1287/mnsc.43.7.934; Rivkin (2000), *Management Science* 46(6), 824–844, https://doi.org/10.1287/mnsc.46.6.824.11940. These works motivate adaptive search and search-geometry dependence; none directly verifies this simulation's correlations or technological ranking.

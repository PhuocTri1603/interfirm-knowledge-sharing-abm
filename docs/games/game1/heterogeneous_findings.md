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

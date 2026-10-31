# Game 1 — 100-firm horizon validation and results

**Status:** Verified simulation and descriptive analysis; not yet a causal claim about real firms.  
**Source revision:** `40266bf38b644bb169fcb5d1358f9649ab7085cb`  
**GitHub Actions:** [Run 41171674224](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41171674224) (completed: success; all three jobs).  
**Branch:** `experiment/game1-100-firms`.

## 1. Scope and unchanged mechanisms

Game 1 models **independent learning**, not inter-firm knowledge sharing. It retains 100 firms (25 each of Cobb-Douglas, Leontief, Linear, CES), initial capital share 0.5, budget 100 per firm, and the existing Random versus Guided learning mechanisms, acceptance rule, production functions, parameters, and matched-randomness implementation. The design uses 100 seeds (2026–2125), two policies and horizons 50, 100, 200 rounds. No production or learning rule was changed to scale the experiment. These horizons are simulation decision rounds, not calendar periods.

The optimum is **technology-specific under the feasible capital-share interval [0.05, 0.95]**. For Linear, the constrained optimum is 0.95; the unconstrained optimum would be at 1.0. Hence all reported efficiencies are relative to the *feasible* optimum.

## 2. Execution and integrity checks

| Horizon | Firm-round rows (two policies) | Paired firm-round rows | GitHub job |
|---|---:|---:|---|
| 50 | 1,000,000 | 500,000 | success |
| 100 | 2,000,000 | 1,000,000 | success |
| 200 | 4,000,000 | 2,000,000 | success |

Three artifacts were uploaded: `13031790079` (50), `13031585631` (100), and `13030944570` (200). Their metadata confirm 100 firms, 100 seeds, 25 firms per technology, and the expected row counts. All 224 unit tests passed in each job. A separate post-run analysis of the 200-round paired CSV found no missing paired values, no declines in accepted output for either policy, and no efficiency above 100% (within numerical tolerance). Overlapping technology-round mean outputs are equal across horizons to floating-point precision (maximum difference about 1.42e-14), supporting cross-horizon reproducibility.

**Data retention:** GitHub Actions artifacts are retained for 90 days. The source commit, environment and metadata files are included in each artifact. Archive artifacts separately if longer-term research reproducibility is needed.

## 3. Measurement and inference

- **Output efficiency (%)** = 100 × actual output / feasible technology-specific optimum.
- **Guided advantage (%)** = 100 × (Guided output − Random output) / Random output, averaged over paired firm–seed observations. This is *not* the same as the difference in average efficiency.
- **Reached 99% (%)** = share of 10,000 firm–seed trajectories at the stated round with efficiency ≥99%.
- **Time to threshold** = first round at which a trajectory reaches a given efficiency threshold; trajectories not reaching it by round 200 are **right-censored**.
- **Confidence interval** for mean advantage: average within each seed first (100 independent simulation replications), then apply a two-sided t interval across 100 seed means. Firms within a seed must not be treated as 100 independent experiments. The interval reflects simulation-seed variability **conditional on the model**, not real-world external validity.

## 4. Aggregate results

| Round | Random efficiency % | Guided efficiency % | Random ≥99% | Guided ≥99% | Guided advantage % |
|---|---:|---:|---:|---:|---:|
| 1 | 86.4393 | 86.4393 | 7.43% | 7.43% | 0.0000 |
| 5 | 93.4988 | 91.5648 | 29.41% | 30.27% | -1.8472 |
| 10 | 96.3827 | 96.0397 | 45.14% | 55.96% | -0.1833 |
| 20 | 98.1802 | 99.1265 | 59.78% | 81.32% | +1.0386 |
| 50 | 99.2539 | 99.8360 | 75.52% | 94.76% | +0.6019 |
| 100 | 99.6353 | 99.9243 | 87.80% | 99.09% | +0.2939 |
| 150 | 99.7588 | 99.9504 | 93.62% | 99.84% | +0.1936 |
| 200 | 99.8192 | 99.9619 | 96.67% | 99.98% | +0.1439 |

The mean firm-paired advantage becomes positive at round **11**. At round 200 the mean advantage is **+0.14388%**, with seed-level 95% t interval **[+0.13959%, +0.14816%]**. Random is stronger in early mean output, while Guided overtakes and maintains a small advantage as both policies approach the optimum. Mean output is a different criterion from the share of firms reaching a threshold: at round 10, Guided has a higher ≥99% attainment rate despite lower mean efficiency.

## 5. Production-function heterogeneity

| Technology | Guided advantage at round 50 | At round 100 | At round 200 | Random ≥99% at round 200 | Guided ≥99% at round 200 |
|---|---:|---:|---:|---:|---:|
| CES | +0.0460% | +0.0119% | +0.0030% | 100.00% | 100.00% |
| Cobb-Douglas | +0.0313% | +0.0080% | +0.0020% | 100.00% | 100.00% |
| Leontief | +1.2463% | +0.6040% | +0.2995% | 89.16% | 99.92% |
| Linear | +1.0838% | +0.5516% | +0.2710% | 97.52% | 100.00% |

The largest remaining gaps occur in Leontief and Linear. This is **descriptive heterogeneity under the chosen function parameters**, not proof that substitution elasticity alone causes the gaps.

## 6. Time to first reach an efficiency threshold

| Threshold | Policy | Reached by round 200 | Median first round among those reaching |
|---|---|---:|---:|
| 95% | Random | 100.00% | 4 |
| 95% | Guided | 100.00% | 6 |
| 99% | Random | 96.67% | 12 |
| 99% | Guided | 99.98% | 9 |
| 99.9% | Random | 62.33% | 22 |
| 99.9% | Guided | 86.65% | 12 |

**Important:** These medians are conditional on having reached the threshold by round 200; do not interpret them as uncensored population medians when many trajectories are censored. In particular, 99.9% is not reached by 37.67% of Random and 13.35% of Guided trajectories by round 200. Therefore, **200 rounds do not establish universal convergence**.

At the 99% threshold, Leontief reaches by round 200 in 89.16% (Random) vs 99.92% (Guided); Linear 97.52% vs 100%. At the 99.9% threshold, Leontief reaches in 19.44% (Random) vs 46.60% (Guided), showing why an explicit convergence criterion matters.

## 7. Findings and limits

1. The planned 100-firm baseline is implemented and all 50/100/200-round runs pass validation.
2. Both learning policies monotonically improve each firm's accepted output under the current acceptance rule.
3. Guided is initially worse on average but overtakes Random, with a diminishing long-run advantage.
4. Learning-policy differences vary substantially across the four fixed production-function specifications.
5. At round 200, near-optimality at **99%** is widespread but not universal; at **99.9%** it is far from universal, especially for Leontief.

**Limitations:** Model outputs are simulated, not field evidence; firm function parameters are fixed in this experiment; 100 seeds are Monte Carlo replications, not observed firms; these results concern independent learning only and must not be interpreted as a knowledge-sharing effect. No AI market shock, endogenous market competition or cooperation effect is identified by this particular horizon comparison. The initial common market-wide technology factor `A_t` and dynamic K/L decisions should not be conflated.

## 8. Reproducibility and stage completion

Reproduce from source revision `40266bf3` using `python -m experiments.game1_mechanism_trajectories --firms 100 --seeds 100 --rounds <50|100|200> --export-dir <folder>`. Inspect `metadata.json`, `firm_round_trajectories.csv`, `paired_firm_round.csv`, `mechanism_by_technology_round.csv`, `source_commit.txt`, and `environment.txt` in each artifact.

**Stage status: COMPLETE** for scale-up, workflow correction, reproducible execution, data integrity checks, and descriptive results. No transition to Game 2 or change to Game 1 mechanisms is implied by this report.

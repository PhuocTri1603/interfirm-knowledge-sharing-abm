# Game 2 — Competitive learning from public performance

**Status:** Existing implementation identified; baseline audit and integration pending (2026-11-02). This document records what is already in the repository; it does not introduce new economic assumptions.

## Research motivation

Firms may observe rival performance and adjust learning behavior. The principal researcher's motivations include fear of falling behind, reducing independent discovery costs, and finding market opportunities. These are motivations, **not** claims that the present code already implements all three.

## Existing source implementation

- `src/interfirm_abm/public_information.py`: public snapshots expose `round`, `firm_id`, `technology`, and `output`. Private allocations and trial histories are excluded. At round t, a firm observes the end-of-round t−1 snapshot.
- `src/interfirm_abm/competitive_learning.py`: a performance-triggered exploration rule raises the probability of global exploration from 0.20 to 0.40 when a firm's own output growth is below the mean growth of other firms with the same technology. The values 0.20/0.40 are **existing code defaults**, not newly selected values.
- `src/interfirm_abm/competitive_simulation.py`: `CompetitiveSimulation` offers `information_only` (observe without behavioral response) and `performance_triggered` (adjust exploration probability). It inherits matched randomness and the `guided_initial` learning rule from Game 1's `Simulation`. A growth signal is available from round 3 onward using the two completed previous snapshots.
- `docs/proposals/experimental_design.md`: states the intended treatment distinction: Game 1 own history, Game 2 public competitor performance, Game 3 voluntary exchange of detailed histories at a cost. It calls for matched initial conditions, equal experimental opportunities and common random conditions.

## Exact scope and non-claims

The **current code** is a competitive-information *learning* prototype, not an implemented product-market competition model. It has no endogenous market-clearing price, rival-induced sales displacement, strategic pricing, profit maximization, or direct copying of rival private input decisions. It does not establish that learning from rivals is economically beneficial. The inherited `CompetitiveSimulation` defaults are 20 firms / 50 rounds, whereas the completed heterogeneous Game 1 research uses 100 firms / 100 rounds; **the two are not yet comparable without integration work**.

## Implementation workstream, without changing economic choices

1. Preserve the existing public-information contract and the two existing policies as the initial Game 2 baseline.
2. Add compatibility with the frozen 100-firm heterogeneous Game 1 population and matched-seed controls while preserving existing default behavior.
3. Add tests for information leakage, temporal look-ahead, matching, and unchanged baseline behavior.
4. Compare the existing `information_only` and `performance_triggered` treatments using matched conditions; report simulation outputs descriptively, not as causal evidence about real firms.
5. Leave market prices, profits, rival selection, knowledge content and voluntary sharing for their respective pre-existing design decisions and later modules. Do not silently implement unapproved variants.

## Interpretation protocol

Keep output-efficiency outcomes distinct from profits or welfare. Verify baseline equivalence before treatment comparisons. Report negative, null and positive outcomes. Existing literature may motivate interpretation but does not validate numeric simulation results.

**Next technical step:** integrate and test the existing Game 2 prototype against the Game 1 100-firm baseline.

## Implementation checkpoint — 2026-11-02

The existing `CompetitiveSimulation` constructor now accepts `heterogeneous_population` and `population_seed` and passes them unchanged to the Game 1 `Simulation` base class. Its original 20-firm/50-round defaults and existing 0.20/0.40 decision rule are preserved. Tests were added to require **exact** equality of the 100-firm `information_only` control against the frozen Game 1 `guided_initial` baseline for two population seeds, and to check lagged observations, 99 visible rivals, reproducibility and invalid-population rejection. These are code-level assertions; CI outcome has **not yet been inspected**.

The pre-existing `.github/workflows/game1-heterogeneous-tests.yml` already triggers on push to this research branch and runs the full pytest suite. No manual workflow dispatch is required for these commits. Next: verify CI outcome and then build a matched, population-seed-replicated Game 2 experiment reporting output-efficiency differences with the information-only control. Any numerical findings remain conditional on the existing behavior rule and should not be described as market-competition or welfare effects.

## Matched Game 2 experiment — implementation checkpoint (2026-11-02)

**CI verification of the previous integration:** The branch push test suite completed successfully in [Actions run 41410478046](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41410478046).

**New experiment:** `experiments/game2_heterogeneous.py` compares the two **pre-existing** policies, `information_only` and `performance_triggered`, using exactly matched 100-firm populations, 100 rounds, and learning seeds. It exports final firm-level efficiency, paired differences, seed-family summaries, per-round information summaries and a JSON summary. `tests/test_game2_heterogeneous.py` checks row counts, summary accounting and deterministic reproducibility.

**Automatic pilot workflow:** `.github/workflows/game2-heterogeneous-pilot.yml` runs on relevant pushes to the research branch, with five population seeds (2026–2030) and 20 matched learning seeds per population. The smaller initial seed count is a **pilot validation stage**, not final precision or external validity. The workflow runs pytest first and uploads per-population artifacts. This workflow was added on the research branch; its execution and numerical outcomes remain **unverified** until a run is inspected.

**Economic interpretation:** This treatment changes *search behavior conditional on observed relative output growth*. It does not implement market rivalry in prices, profits, or demand, and does not measure welfare. The outcome is simulated productive efficiency relative to a firm-specific feasible optimum. Population draws, rather than learning-seed repetitions, delimit independent population-level generalization.

## Verified pilot execution — 2026-11-02

The five-population matched pilot **completed successfully** in [GitHub Actions run 41412796193](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41412796193), with successful matrix jobs for population seeds 2026–2030. Five separate downloadable result artifacts are present; the companion branch pytest run also passed. This verifies execution and artifact generation, **not** an economic treatment effect. No numerical direction, magnitude, confidence interval, or claim of welfare improvement is inferred from green CI status.

Next analysis gate: extract the five `summary.json` and paired seed-family tables, aggregate effects at the **population seed** level (n=5 independent sampled populations; 20 learning seeds per population), and inspect the sign and heterogeneity of simulated productive-efficiency differences. Within-population learning seeds are repeated stochastic runs, not independent sampled economies. Do not substitute a learning-seed standard error for uncertainty across sampled populations.

## Pilot results inspected — 2026-11-02

Source: `game2-cross-population-41414939636` artifact from [Actions run 41414939636](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41414939636). The ZIP contains `cross_population_summary.json`, `population_overall_effects.csv`, `population_family_effects.csv`, and `all_seed_family_effects.csv`. All five population runs, the aggregate job, and pytest completed successfully.

Design: 5 independent population seeds (2026–2030), 20 matched learning seeds per population, 100 firms and 100 rounds per matched policy. Estimand: final firm productive efficiency, `performance_triggered - information_only`, in **percentage points**, averaged within learning seed and then population. Both policies use the same initial population and random schedule.

| Production family | Mean difference (pp) | Across-population SE (pp) |
| --- | ---: | ---: |
| All firms | -0.0037021584 | 0.0006446664 |
| CES | -0.0003002099 | 0.0000949138 |
| Cobb-Douglas | -0.0001961767 | 0.0000546151 |
| Leontief | -0.0143122471 | 0.0025906055 |
| Linear | 0.0000000000 | 0.0000000000 |

Overall per-population effects (pp): 2026: -0.0041433830; 2027: -0.0049409107; 2028: -0.0012181828; 2029: -0.0038927718; 2030: -0.0043155437. The normal-approximation interval reported by the pipeline is [-0.0049657046, -0.0024386122] pp; **n=5 populations is too small to treat this normal interval as a robust inferential claim**. No empirical or welfare inference is warranted.

**Economic interpretation and follow-up:** The existing performance-triggered rule produces a small negative end-of-horizon productive-efficiency difference relative to the information-only control. Leontief dominates the magnitude; Linear is zero at the reported precision. These observations do not identify why the difference arises. Follow-up diagnostics should inspect trigger frequency, within-round exploration behavior, the path of efficiency (not only terminal efficiency), and whether effects persist under longer horizons or different predetermined learning seeds. The model has no search cost or price/profit competition, so this is not a claim about economically optimal experimentation or market welfare.

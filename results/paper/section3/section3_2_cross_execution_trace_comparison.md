# Section 3.2 — Cross-execution trace comparison (2026-11-12)

## Provenance

- Baseline-matching trace: [run 43207912859](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/43207912859), artifact 13940801384.
- Baseline-diverging traces: [run 43219989053](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/43219989053), artifacts 13945401983, 13945851749, 13944842673.
- The original archived game is commit `c614b86d9192a57fb402b4772b3c3bb6bf80b79f`, F011, sigma 0.5, seed 11.
- Historical archive has no optimizer traces. This comparison contrasts **two replay executions**, not replay against the historical optimizer trajectory.

## First differences in downloaded trace CSVs

The baseline-matching and baseline-diverging replays both executed **9,154 optimizer calls** and their first SLSQP solution-vector hash difference occurs at **call #2**, **round 1**, `L3=productivity|L4=profit_based`, candidate #1. Both return success and have 17 iterations, 357 function evaluations. Objective values differ only at approximately `2.21e-12` (`-0.6599999991628791` versus `-0.6599999991606703`). The matching run's `x_hash=2de6d65e098889ccc580`; diverging run's `x_hash=4182867c5ccdff779299`. These are hashes of raw float64 arrays; a hash mismatch does not establish economically meaningful discrepancy.

The first nonidentical candidate output is **candidate #14, round 4**, `L3=cost_adjusted|L4=profit_based`: matching `q=0.4199356877401872`, diverging `q=0.4199356393947669` (absolute difference `4.83454203e-8`); matching cost `0.2055350007746227`, diverging cost `0.2055349163318298` (difference `8.44427929e-8`). Both select the same mode bitmask `1001100000000000010` and have 36 SLSQP calls, indices 65–100. Subsequent market price at round 5 differs by about `5.37e-9` (matching `1.6866738124733125`; diverging `1.6866738178450258`).

The first archived gate mismatch occurs **candidate #36, round 8**, same strategy: matching `q=0.922386678228658`, diverging `q=0.9223870620939844` (difference `3.83865326e-7`); matching cost `0.4098650726739683`, diverging `0.4098657325918641` (difference `6.59917896e-7`). Both use mode bitmask `1001100000000000010` and candidate #36 encompasses SLSQP calls 229–248.

The first **different SLSQP iteration count** appears at **call #119, round 5**, `cost_adjusted|profit_based`, candidate #20: 31 vs 28 iterations; function evaluations 674 vs 615. This is later than the first raw solution-vector difference, but earlier than the strict gate mismatch.

The pip-frozen package environments in both replay artifacts are **byte-for-byte identical**. The older passing trace did not record optimizer initial-point hashes; the newer failing traces do. Therefore one **cannot** conclude that the first differing solver call received identical inputs. A controlled paired experiment with full input fingerprints, BLAS thread/runtime configuration and exact objective/bounds/constraint fingerprints is needed to identify the underlying numerical source.

## Scientific interpretation and restrictions

- Cross-execution floating-point differences are observed. Feedback propagation through market prices is consistent with the sequence, but a root cause (SLSQP, BLAS, OS/runtime, or other) is **not proven**.
- Neither run establishes global optimality or the correctness of the original archived allocation.
- Do not increase gate tolerances or silently replace the original archived experiment.
- Section 3.2 descriptive archived results may be retained with appropriate caveats; task-level mechanism interpretation and Figures 3.4–3.6 remain blocked until the reproduction gate and independent accounting checks pass.
- `research_validated=false`.

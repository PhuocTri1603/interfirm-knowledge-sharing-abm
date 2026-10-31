---
name: reproducibility
description: Make every ABM result traceable to source revision, parameterization, random seeds, environment, workflow and immutable artifacts.
---
# Reproducibility

## Trigger
Use for every simulation run, published figure/table, GitHub Actions workflow, artifact download or research result.

## Procedure
1. Record repository, branch, full commit SHA, command, Python and dependency versions, platform, experiment name and execution timestamp.
2. Store complete configuration: n_firms, technology counts, budget, initialization, policy, exploration probability, search radius, matched_randomness, seeds and rounds.
3. Save raw firm-round data, paired comparisons, aggregates, metadata and schema; never silently replace prior outputs.
4. Use stable seed lists and paired designs. Compare overlapping horizons using identical initial state and random schedules; report tolerances.
5. Verify checksums or other integrity markers where available, expected/observed row counts, uniqueness and missingness; document provenance for every figure and claim.
6. Inspect GitHub Actions job outcomes and logs. Archive artifacts externally before retention expiry; link exact run and artifact IDs.
7. Document reproduction commands and any dependencies on private repository access. Do not claim independent reproducibility unless another run is performed.
8. Distinguish reproducibility of code/data from validity of the economic assumptions and generalizability.

## Current reference case
Game 1 verified horizon run: `41171674224`; source commit `40266bf38b644bb169fcb5d1358f9649ab7085cb`; 100 firms, 100 seeds, 50/100/200 rounds; documented in `docs/games/game1/horizon_100_firms_results.md`. These identifiers are historical provenance, **not** defaults for future runs.

## Completion
A third party with repository access can locate code, reconstruct configuration, rerun the experiment and reconcile outputs with documented tolerances.

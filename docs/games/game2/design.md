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

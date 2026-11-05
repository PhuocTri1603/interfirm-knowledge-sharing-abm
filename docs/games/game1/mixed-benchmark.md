# Game 1 — Why Mixed Market is the benchmark

**Status:** Design rationale; not a calibrated or validated economic result.

## Research question and identification

The primary question is which L1–L6 strategy obtains the largest cumulative
profit over 200 rounds when all 3,072 strategy players interact in the same
product market. For each of the 100 initial profiles, all strategies receive
the same exogenous initial resource endowments and face the same market demand.
Technology and learning behavior remain strategy-specific. The 100 original
firm profiles are *initial environments*, not additional players.

## Why one shared market?

Cournot quantity competition provides a parsimonious industrial-organization
reference: firms choose quantities simultaneously, aggregate quantity determines
a common product price, and profits depend on rivals' output. This captures
strategic externalities absent from separate, isolated profitability tests.
The dynamic learning tournament is **Cournot-style**, not an assertion that
agents calculate Cournot-Nash best responses or converge to equilibrium.

Tesfatsion (2006) emphasizes agent-based economies as dynamic systems of
interacting agents with strategic rivalry, learning and market power. Vives
(2008) explicitly analyzes Cournot homogeneous-product markets in the context
of innovation and competitive pressure. These support a shared-price
benchmark, **not** the claim that a mixed market must be the most realistic
or welfare-optimal structure.

## Market mechanism

At round t each player chooses a feasible task allocation based on information
available before round t. The task technology produces q_i,t; aggregate
Q_t = sum_i q_i,t; a researcher-specified inverse demand gives P_t = P(Q_t);
and realized profit is pi_i,t = P_t q_i,t - r K_i,t - w L_i,t.
Payoff feedback is released only after all players have decided. This is
the existing dynamic market runner's accounting convention.

Winner within configuration c: argmax_i sum_(t=1)^200 pi_i,c,t.
Compare winner frequencies and profit distributions across the 100 profiles;
record concentration and total market profit as additional outcomes.
The winner criterion is not equivalent to consumer or total welfare.

## Limits and controls

- **Demand scale:** 3,072 simultaneously active strategies can make a fixed
  inverse demand degenerate. Demand parameters must be specified and sensitivity
  tested; do not assume a numeric intercept or slope without justification.
- **Counterfactuals:** Separate, Clones, and Stratified alter market composition,
  so market size, number of active competitors, total initial resources, and
  demand normalization must be reported. Their outcomes cannot automatically
  be interpreted as causal effects of market organization.
- **Technology:** Original Cobb-Douglas, Leontief, Linear and CES profiles do
  not uniquely determine 20-task productivity vectors. Explicit mappings
  and theoretical assumptions are required.
- **Learning:** No L1–L6 label should be treated as a working behavioral
  mechanism until its policy implementation is specified and tested.
- **Stochastic comparisons:** Pairing random seeds across counterfactual runs
  can improve comparability, but cannot replace replication and sensitivity
  analysis.

## Sources

1. Tesfatsion, L. (2006). Agent-Based Computational Economics: A Constructive
   Approach to Economic Theory. *Handbook of Computational Economics*, 2.
   https://doi.org/10.1016/S1574-0021(05)02016-2
2. Vives, X. (2008). Innovation and Competitive Pressure.
   *The Journal of Industrial Economics*. https://doi.org/10.1111/j.1467-6451.2008.00356.x
3. Tesfatsion, L., & Judd, K. L. (Eds.). (2006).
   *Handbook of Computational Economics, Volume 2: Agent-Based Computational
   Economics*. Elsevier. https://shop.elsevier.com/books/handbook-of-computational-economics/tesfatsion/978-0-444-51253-6

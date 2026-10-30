# Game 3B — H2: Technological Similarity and Knowledge Compatibility

## Status
Simulation findings, 100 matched Monte Carlo seeds (2026–2125).
These are model-based results, not empirical evidence about real firms.

## Research Hypotheses

**H2a — Technological Similarity**

Knowledge transfer between firms sharing the same production
technology is more likely to generate successful learning outcomes.

**H2b — Knowledge Compatibility**

The effectiveness of inter-firm knowledge transfer depends more
strongly on the compatibility of transferred knowledge with the
recipient's production technology than on technological similarity
alone.

## Simulation Design

- Four production technologies: Cobb-Douglas, Leontief, Linear, CES.
- 20 firms, 50 rounds, 100 matched random seeds.
- Knowledge is represented by a capital-allocation share.
- Counterfactual evaluation considers eligible accepted knowledge
  from all four source technologies within the same recipient state.
- Source records are drawn from prior rounds and exclude the recipient.
- The observed adjustment to the transferred allocation is held fixed
  across counterfactual source records.
- 29,575 complete recipient states; 1,990,118 knowledge-level
  counterfactual evaluations.
- Inference aggregates matched comparisons by state and then seed.

## H2a: Unmatched Counterfactual Results

Same-technology minus cross-technology:

- Acceptance probability: +0.027200.
  95% CI [+0.025115, +0.029285].
- Mean realized output gain: +0.098577.
  95% CI [+0.087034, +0.110120].
- Both p < 0.001.

Excluding Linear entirely:

- Acceptance probability: +0.007765, p < 0.001.
- Mean output gain: +0.013710, p = 0.0114.

The comparison without Linear changes the composition of the
cross-technology source group.

## H2b: Knowledge-Distance Matching

Source knowledge distance:
abs(source_share - recipient_optimal_share).

Candidate distance:
abs(candidate_share - recipient_optimal_share).

Signed candidate distance:
candidate_share - recipient_optimal_share.

Source-distance matching across bin widths 0.005, 0.010 and 0.020
produced acceptance differences close to zero, none statistically
significant at 5%.

Within the retained states, unmatched acceptance differences remained
approximately +0.0258 to +0.0268. After matching they were close to zero.
Thus, sample-state exclusion alone does not account for the attenuation.

At bin width 0.005:

- Source-distance matching:
  acceptance difference -0.000012, p = 0.9848;
  output-gain difference +0.005971, p = 0.1194.
- Absolute candidate-distance matching:
  acceptance difference +0.000734, p = 0.0372;
  output-gain difference +0.004034, p = 0.1022.
- Signed candidate-distance matching:
  acceptance difference -0.000289, p = 0.2883;
  output-gain difference -0.000328, p = 0.0849.

Signed-distance matching retained 28,260 recipient states.

## Signed-Distance Matching by Recipient Technology

CES:
- Acceptance difference -0.000960, p = 0.2446.
- Output-gain difference -0.000051, p = 0.3825.

Cobb-Douglas:
- Acceptance difference +0.000211, p = 0.7189.
- Output-gain difference +0.000052, p = 0.4327.

Leontief:
- Acceptance difference -0.000310, p = 0.5669.
- Output-gain difference -0.001294, p = 0.0997.

Linear:
- Acceptance difference -0.000087, p = 0.2782.
- Output-gain difference +0.000128, p = 0.4833.

No recipient technology shows a statistically significant difference
at the unadjusted 5% level after signed-distance matching.

## Interpretation

Unmatched same-technology knowledge is more likely to improve recipient
output in this simulation. This association is strongly attenuated
when comparing transferred allocations with similar compatibility
to the recipient's production technology.

The results are consistent with a knowledge-compatibility mechanism.
They do not establish causal mediation or equivalence of source types.

## Limitations

1. Compatibility is measured using the recipient's known mathematical
   optimum, which firms need not observe.
2. Production functions and acceptance rules are deterministic.
   Compatibility and transfer effectiveness are mechanically related.
3. Knowledge consists of a single capital-allocation parameter,
   not a complete technology, routine or organizational practice.
4. Counterfactuals reuse observed adjustments, which may be affected
   by clipping at feasible allocation boundaries.
5. Matching changes weights over knowledge records and distance bins.
6. Repeated source records and recipient states are not independent;
   statistical comparisons aggregate by seed.
7. Statistical tests are exploratory and not adjusted for multiple
   comparisons.
8. Failure to reject a difference is not evidence of equivalence.

## Next Research Direction

Study whether firms can learn to evaluate the compatibility of
external knowledge using observable performance and limited
information, without knowing the recipient's optimal allocation.

This would extend the model from ex-post compatibility analysis
toward endogenous organizational learning.

## Data Files

- results/game3_monte_carlo/h2_exhaustive_counterfactual_100_seeds.csv
- results/game3_monte_carlo/h2_knowledge_level_counterfactual_100_seeds.csv.gz
- results/game3_monte_carlo/h2_distance_matched_100_seeds.csv
- results/game3_monte_carlo/h2_knowledge_compatibility_100_seeds.csv

# Game 1 — Preliminary statistical equivalence of A–B contrasts

Status: **APPROVED_PRELIMINARY_STATISTICAL_EQUIVALENCE_AB** (approved economic margins and preliminary A–B audit; not full research validation)
Recorded: 2026-11-15
Research validation: **false**

## Evidence
- Original archive: Actions run 42463803820.
- Instrumented observational data: Actions run 43593085278.
- Statistical equivalence audit: Actions run 43659921894; artifact `game1-statistical-equivalence-audit` (14139706920).
- 100 technology profiles, three task-substitution elasticities (sigma 0.5, 1, 2), nine strategies, 200 rounds; paired cluster bootstrap with 4,000 resamples at the technology-profile level.
- Strategy A: `L3=cost_adjusted|L4=profit_based`.
- Strategy B: `L3=productivity|L4=profit_based`.

## Preliminarily equivalent comparisons
The difference between replay and archive in the **terminal cumulative-profit gap A–B** has the following paired mean differences and 90% bootstrap confidence intervals:

| Sigma | Mean replay-minus-archive difference | 90% bootstrap CI |
| --- | ---: | --- |
| 0.5 | 0.0000219067 | [-0.0000030450, 0.0000535107] |
| 1.0 | 0.0000087174 | [-0.0000092617, 0.0000304128] |
| 2.0 | 0.0026744039 | [-0.0010087338, 0.0086277503] |

All three CIs lie within the **researcher-approved** equivalence margin ±4 cumulative-profit units. All three differences in the A–B contrast across sigma pairs (0.5→1, 1→2, 0.5→2) also satisfy the researcher-approved ±8 margin using 90% bootstrap CIs.

Terminal winner agreement and complete nine-strategy ranking agreement: 300/300 profile–sigma cases. Mean Kendall's tau: 1 for each sigma.

## Interpretation and limitations
This is evidence of **preliminary statistical equivalence of the replay-versus-archive A–B contrasts under candidate economic materiality margins**, not proof of exact numerical equivalence or general statistical reproducibility. The equivalence decision is conditional on accepting the candidate margins, which are approved by the principal researcher as operational economic materiality thresholds; independent justification and sensitivity analysis remain desirable. The bootstrap CI-inclusion method is an approximate equivalence test, not a parametric TOST. The 114 audit comparisons were exploratory and do not have familywise multiplicity control. The archive and replay are paired deterministic runs; independent multi-seed robustness is still pending.

The original archive lacks task-level K/L and cost decomposition, so historical mechanism-level equivalence cannot be established from it. Section 3.2's price and resource-allocation mechanisms remain unvalidated. Numerical strict comparison status remains STRICT_FAIL; this does not contradict preliminary statistical equivalence of specific economic contrasts.

**Do not change the Game 1 economic engine or parameters. Do not mark `research_validated=true`.** Next gates: multi-seed robustness, sensitivity to the approved economic margins, and validation of Section 3.2 mechanisms.

## Researcher approval decision — 2026-11-15
The principal researcher explicitly approved the preliminary A–B statistical-equivalence finding and the previously proposed economic materiality margins. Approved thresholds: price ±0.01, output ±0.01, per-round profit ±0.01, cumulative profit ±2, terminal A–B profit gap ±4, and change in A–B gap across sigma ±8, in model-normalized units. This approval authorizes interpreting the existing A–B audit as **approved preliminary statistical equivalence under these margins**, not as a claim that all 114 exploratory tests passed, that independent-seed robustness was established, or that the Section 3.2 mechanism was validated. The model engine and economic parameters remain unchanged; `research_validated=false`.

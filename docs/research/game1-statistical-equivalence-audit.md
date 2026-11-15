# Game 1 — Preliminary statistical equivalence of A–B contrasts

Status: **PRELIMINARY_STATISTICAL_EQUIVALENCE_AB** (diagnostic, not final validation)
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

All three CIs lie within the **proposed, not yet approved** equivalence margin ±4 cumulative-profit units. All three differences in the A–B contrast across sigma pairs (0.5→1, 1→2, 0.5→2) also satisfy the proposed ±8 margin using 90% bootstrap CIs.

Terminal winner agreement and complete nine-strategy ranking agreement: 300/300 profile–sigma cases. Mean Kendall's tau: 1 for each sigma.

## Interpretation and limitations
This is evidence of **preliminary statistical equivalence of the replay-versus-archive A–B contrasts under candidate economic materiality margins**, not proof of exact numerical equivalence or general statistical reproducibility. The equivalence decision is conditional on accepting the candidate margins, which require substantive economic justification. The bootstrap CI-inclusion method is an approximate equivalence test, not a parametric TOST. The 114 audit comparisons were exploratory and do not have familywise multiplicity control. The archive and replay are paired deterministic runs; independent multi-seed robustness is still pending.

The original archive lacks task-level K/L and cost decomposition, so historical mechanism-level equivalence cannot be established from it. Section 3.2's price and resource-allocation mechanisms remain unvalidated. Numerical strict comparison status remains STRICT_FAIL; this does not contradict preliminary statistical equivalence of specific economic contrasts.

**Do not change the Game 1 economic engine or parameters. Do not mark `research_validated=true`.** Next gates: approve economically meaningful equivalence margins, multi-seed robustness, and validate Section 3.2 mechanisms.

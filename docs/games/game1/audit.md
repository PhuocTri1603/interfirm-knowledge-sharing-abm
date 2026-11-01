# Game 1 — Research validation and audit status

**Status: CONDITIONAL / NOT SIGNED OFF (independent raw-artifact audit PASSED on 2026-10-31).** This is a research-audit checkpoint, not proof of scientific validity or website acceptance.

## Scope and provenance
- Branch: `experiment/game1-heterogeneous-firms`.
- Simulation source commit: `797361d5c804ac03b9baabf2bb187f08408c7bf2`.
- CI: https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41204620746
- Experiment: `experiments/game1_heterogeneous.py`; 100 firms, four technologies (25 each), 100 matched learning seeds, fixed population seed 2026, horizons 50/100/200, Random vs Guided.
- Evidence: CI job logs and three uploaded workflow artifacts; summary values transcribed to `docs/games/game1/heterogeneous_findings.md`.
- Historical homogeneous-parameter experiment: `docs/games/game1/horizon_100_firms_results.md`. Do not mix historical statistics with the heterogeneous experiment.

## Verified
1. All three horizon jobs completed successfully. Their pytest steps reported 241 passing tests per job.
2. Each job successfully ran the paired experiment and its export assertions, then uploaded its artifact.
3. The experiment asserts 20,000 final firm-policy-seed rows and 10,000 paired firm-seed rows per horizon, 100 firms per policy and seed, 50 labor-oriented firms per policy and seed, and efficiency <=100% within tolerance.
4. CI log summaries show mean Guided-minus-Random final efficiency differences (pp): 50 rounds +0.4821336 [0.4611170,0.5031502]; 100 rounds +0.2417890 [0.2323358,0.2512422]; 200 rounds +0.1213950 [0.1161967,0.1265933]. Intervals are approximate normal 95% intervals based on seed-aggregated differences conditional on one fixed population.

## Independent audit update — 2026-10-31

- **PASSED:** [Independent audit run 41212931829](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41212931829) downloaded all 15 original artifacts from [full population-sensitivity run 41210955389](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41210955389); 150,000 paired rows and 300,000 final rows.
- **PASSED:** Recomputed paired Guided-minus-Random means, family and Strong-minus-Moderate effects, and seed-level normal-approximation 95% intervals independently using Python standard library; verified keys, row counts and agreement with exported summaries. CI printed `INDEPENDENT AUDIT PASSED` and uploaded an audit JSON artifact.
- **PASSED:** Five population seeds (2026–2030) × three horizons (50,100,200), 100 learning seeds in each cell. Across-population mean overall advantage: +0.470813 pp at 50 rounds [range 0.443996–0.482134], +0.243426 at 100 [0.233473–0.250487], +0.121806 at 200 [0.117037–0.124963]. These brackets denote cross-population **min–max**, not confidence intervals.
- **PASSED:** Family subgroup effects and F7 within-family alpha contrasts verified; full tables and their limitations in `docs/games/game1/heterogeneous_findings.md` §9. Leontief > Linear > both CES and Cobb-Douglas for F5 across all cells; CES/Cobb-Douglas ordering can differ. F7 CES/200 has a negative point estimate in one of five populations.
- **LIMITATION:** Only five populations; population-level interval inference and multiple-testing correction not established. No causal search-geometry decomposition or audited website replay yet.

The next section documents **outstanding items at the earlier audit checkpoint**, some of which are superseded by the verified independent audit above. Do not interpret that historical checklist as current status.

## Not yet verified / outstanding audit findings
- **Major — raw artifact reanalysis:** No independent recalculation of subgroup statistics, missingness, paired keys or confidence intervals from downloaded CSVs has been completed in this checkpoint. Successful CI checks are not an independent audit.
- **Major — within-family heterogeneity:** No reported heterogeneous-experiment treatment effects by Cobb–Douglas/Leontief/Linear/CES or alpha stratum.
- **Major — population sensitivity:** One fixed population seed; learning-seed intervals do not represent uncertainty across populations.
- **Major — mechanism/convergence:** Final-outcome exports do not establish time-to-threshold or the causal reason for the diminishing advantage. The roughly halving gap at three horizons is descriptive, not a scaling law.
- **Major — website audit:** Existing website implementation, artifact lineage, replay fidelity, visibility and interaction tests have not yet been audited for this new heterogeneous experiment.
- **Minor — literature evidence:** March (1991), Nelson & Winter (1982) and Levinthal (1997) provide conceptual alignment; they do not directly replicate these numerical results or establish novelty.

## Sign-off decision
**Game 1 heterogeneous extension remains CONDITIONALLY VALIDATED / NOT SIGNED OFF.** Independent raw-artifact recalculation, subgroup analysis and five-population sensitivity have now passed. Search-geometry mechanism interpretation, multiple-testing assessment and website provenance/replay validation remain outstanding. Do not merge, publish the website, or change economic mechanisms without researcher approval.

## Next workflow gate
Proceed with `simulation-visualization` **Gate 0**: inspect actual website files and data sources, confirm schema/provenance and privacy, then prepare a minimal design/validation specification before implementing or altering frontend behavior.


## Independent audit reconfirmation — 2026-11-01

- **PASS:** [Run 41302627999](https://github.com/PhuocTri1603/interfirm-knowledge-sharing-abm/actions/runs/41302627999) completed the audit job, original-artifact download, independent CSV recomputation, and report upload. Report artifact ID: 13082122304.
- **Scope:** 15 original population/horizon artifacts, 150,000 paired observations and 300,000 final policy observations; verification of keys and row bounds, overall/family effects and seed-level 95% normal-approximation confidence intervals, and within-technology strong-minus-moderate effects.
- **Mean final Guided–Random effect across five populations:** +0.470813 pp (50 rounds), +0.243426 pp (100), +0.121806 pp (200). Population min–max ranges are not confidence intervals. Source results are detailed in heterogeneous_findings.md §14.
- **Interpretation:** Confirms numerical reconciliation to exported CSV and JSON, not model correctness, identification of learning mechanisms or population-level uncertainty. All outstanding independent mechanism and scientific-validity caveats remain; **NOT SIGNED OFF**.
- **Literature:** March (1991), https://doi.org/10.1287/orsc.2.1.71, is conceptual support for the importance of learning dynamics, not independent confirmation of these numerical effects.

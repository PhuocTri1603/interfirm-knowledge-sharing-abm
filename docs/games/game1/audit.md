# Game 1 — Research validation and audit status

**Status: CONDITIONAL / NOT SIGNED OFF.** This is a research-audit checkpoint, not proof of scientific validity or website acceptance.

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

## Not yet verified / outstanding audit findings
- **Major — raw artifact reanalysis:** No independent recalculation of subgroup statistics, missingness, paired keys or confidence intervals from downloaded CSVs has been completed in this checkpoint. Successful CI checks are not an independent audit.
- **Major — within-family heterogeneity:** No reported heterogeneous-experiment treatment effects by Cobb–Douglas/Leontief/Linear/CES or alpha stratum.
- **Major — population sensitivity:** One fixed population seed; learning-seed intervals do not represent uncertainty across populations.
- **Major — mechanism/convergence:** Final-outcome exports do not establish time-to-threshold or the causal reason for the diminishing advantage. The roughly halving gap at three horizons is descriptive, not a scaling law.
- **Major — website audit:** Existing website implementation, artifact lineage, replay fidelity, visibility and interaction tests have not yet been audited for this new heterogeneous experiment.
- **Minor — literature evidence:** March (1991), Nelson & Winter (1982) and Levinthal (1997) provide conceptual alignment; they do not directly replicate these numerical results or establish novelty.

## Sign-off decision
**Game 1 remains OPEN.** CI execution and documentation have passed their respective checks, but independent data analysis, robustness and the verified real-data visualization remain outstanding. Do not merge, publish the website, or change economic mechanisms without researcher approval.

## Next workflow gate
Proceed with `simulation-visualization` **Gate 0**: inspect actual website files and data sources, confirm schema/provenance and privacy, then prepare a minimal design/validation specification before implementing or altering frontend behavior.

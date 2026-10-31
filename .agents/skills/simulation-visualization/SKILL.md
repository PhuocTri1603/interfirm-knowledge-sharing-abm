---
name: simulation-visualization
description: Build and verify an interactive website showing actual ABM firm trajectories, policies, production technologies and learning outcomes without fabricated data.
---
# Simulation Visualization

## When to use
When designing, implementing or reviewing a website, animation, dashboard or interactive Game 1 simulation.

## Inputs
Validated firm-round data and schema, source commit, run/artifact IDs, model-specification document, user-approved visualization scope.

## Procedure
1. Read research-governance, model-specification, simulation-validation and reproducibility. Inspect the real data columns before designing UI.
2. Distinguish **replay of precomputed results** from **live simulation**; label the mode prominently. Do not call an animation of CSV data a newly executed simulation.
3. Specify controls: seed, firm ID, technology, policy, round, playback speed, compare Random/Guided; display allocation share, implied K and L, output, efficiency, candidate vs accepted action and optimum when supported.
4. Use real data only. Never invent missing observations, smooth trajectories without disclosure, or imply causal mechanisms from an animation.
5. Preserve firm identity, seed, technology and round ordering; align matched policies by keys. Confirm plotted values equal source CSV at sampled checkpoints.
6. For performance, preprocess or paginate large files; do not load millions of rows into the browser by default. Document any downsampling and retain exact-value inspection.
7. Provide accessible labels, units, legend, pause/seek, keyboard-usable controls, mobile layout, clear empty/error states and provenance.
8. Test interactions, data reconciliation, browser errors and hosting visibility. A repository website is not considered deployed until its live URL is verified. Never make a private research site public without explicit approval.

## Output
Versioned web source, data-processing instructions, validation checklist, deployment instructions, and verified URL if deployed.

## Acceptance
User can follow one firm's genuine history across rounds and reproduce at least sampled chart values from original artifacts; privacy and deployment status are explicit.

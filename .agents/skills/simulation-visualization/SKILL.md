---
name: simulation-visualization
description: Plan, design, implement, and independently validate an interactive Game 1 research website using only traceable, verified ABM outputs; never alter economic mechanisms.
---
# Simulation Visualization

## When to use
Before designing, implementing, reviewing, deploying, or auditing the Game 1 research website, animation, dashboard, or interactive simulation replay.

## Research boundary and mandatory inputs
- Game 1 is **independent firm learning** under a fixed capital–labor budget, four production functions, and Random/Guided search. It does not simulate interfirm knowledge sharing, product-market competition, profit maximization, or endogenous AI investment.
- Website scope is **visualization and inspection of existing simulation results**, not a new economic experiment, algorithm, research hypothesis, or paper contribution.
- Read `AGENTS.md` and the skills `research-governance`, `model-specification`, `simulation-validation`, `reproducibility`, `statistical-analysis`, and `research-audit` as relevant.
- Use `docs/games/game1/research.md` as the canonical model/audit record and `docs/games/game1/horizon_100_firms_results.md` for the validated horizon experiment.
- Confirm the active branch, actual repository contents, source commit, data schema, seeds, horizon, workflow run, artifact IDs, and access/privacy constraints **before writing website code**.
- If a design requirement conflicts with available columns, report the gap; do not invent observations or silently change the model.

## Website design and delivery procedure (ordered gates)

### Gate 0 — Inspect existing website and lock scope
1. Inspect repository structure, frontend framework, existing pages, components, data pipeline, tests, and deployment configuration. Reuse working implementation; do not create a parallel website by default.
2. Inventory source artifacts and exact CSV/JSON schemas, types, keys, sizes, missing values, and validated experiment configurations. Distinguish `Simulation` defaults (20 firms/50 rounds) from the experiment (100 firms; 25 per technology; 100 seeds; horizons 50/100/200).
3. Write a concise design specification: user journeys, data provenance, screens, chart definitions, interactions, accessibility, loading strategy, verification plan, privacy and hosting. Request approval before any material scope expansion or public deployment.
4. Declare **Replay of precomputed simulation data** prominently; do not describe a CSV animation as a new live simulation.

### Gate 1 — Information architecture and screen designs
Design four research-focused views, using only variables actually supported by verified data:
1. **Simulation Overview:** population, four technologies, policies, seed/horizon/round context, mean output efficiency, attainment thresholds, and provenance.
2. **Learning Trajectories:** choose seed, firm ID, technology, policy, horizon and round; inspect candidate vs accepted allocation, capital share, implied `K=B×share`, `L=B×(1−share)`, output, efficiency, and paired Random/Guided histories. Add play/pause, seek, speed and step controls for *replay*.
3. **Production Functions:** graph the four fixed, implemented output-versus-capital-share functions within the feasible range `[.05,.95]`, mark feasible optima and actual selected shares, label fixed budget `B=100`; explicitly separate analytic curves from exported simulation observations.
4. **Statistical Validation:** show seed-aggregated paired policy advantage, pointwise 95% seed-level confidence intervals, per-technology results, and attainment at 95%, 99%, 99.9%; label conditional Monte Carlo uncertainty, censoring, and differences between percentage and percentage points.

### Gate 2 — Data contract and provenance
1. Define a typed data contract and data dictionary from actual exported columns, not assumptions; include unique keys (`seed`, `policy`, `firm_id`, `round`) and technology.
2. Link each plotted metric to its exact source field or a documented, independently tested transformation. Keep the definitions of mean efficiency, mean paired relative output advantage, threshold attainment, and seed-level intervals distinct.
3. Embed/display experiment source commit `40266bf38b644bb169fcb5d1358f9649ab7085cb`, workflow run `41171674224`, artifact identifiers (50: `13031790079`; 100: `13031585631`; 200: `13030944570`), selected horizon and seeds. These are **existing validated-baseline provenance**, not hardcoded substitutes for inspecting actual files.
4. Preserve exact observation identity and ordering; join matched policies by keys. Never manufacture missing data, interpolate undisclosed values, or reuse a different seed's trajectory.
5. Preprocess large artifacts to compact, versioned data products or queryable partitions; do not load 1–4 million full rows into the browser by default. Preserve exact-value drill-down and a reproducible build script. Disclose sampling/downsampling.

### Gate 3 — Interaction and visual standards
1. Provide controls for seed, technology, firm, policy, horizon, round, replay speed and comparison mode only where underlying data support them; ensure dependent controls update every affected view consistently.
2. Use legible axis labels, units, legends, hover/keyboard-accessible exact values, responsive desktop/mobile layout, color-blind-friendly distinctions, clear empty/error/loading states, and visible provenance.
3. Clearly distinguish observed simulation series, analytical optimum curves, and derived statistics. Do not imply an empirical causal effect or universal convergence.
4. Do not include new Game 2/3 knowledge-sharing mechanisms or allow user-facing controls to modify economic parameters unless the researcher explicitly authorizes a separate experiment.

### Gate 4 — Implementation and verification
1. Build the smallest working vertical slice first: select seed+firm → show actual trajectory → compare policies → inspect source row. Expand to the other three views after that passes.
2. Unit-test data ingestion, transformations, seed-level aggregation, key uniqueness, missing-data behavior, production optima and percentage/percentage-point units.
3. Independently sample-check displayed values against original artifact CSVs across all four technologies, both policies, several seeds and rounds (including 1, 11, 20, 50, 100 and 200 when available). Check that changing horizon preserves the shared earlier trajectory.
4. Test all filters, replay controls, keyboard interaction, mobile rendering, missing/corrupt data states, browser errors and large-data performance. Record **passed / failed / not run / not verifiable** separately.
5. Do not mark visualization verified merely because charts render or GitHub Actions is green.

### Gate 5 — Deployment and research sign-off
1. Keep the website private by default. Never enable public GitHub Pages, public hosting, or publish data without explicit researcher approval.
2. Document reproducible local startup/build, required dependencies, data regeneration commands, source commit, data manifest and hosting configuration.
3. Only claim a deployed website after checking its actual reachable URL and critical interactions. Otherwise report **implemented locally / not deployed** accurately.
4. Request an independent `research-audit` review of data lineage, sampled rendered values, interaction tests, and visibility before marking the **whole Game 1 milestone** complete.

## Deliverables
- Website design specification and screen/interaction map.
- Versioned frontend source, documented data contracts and reproducible preprocessing/build scripts.
- Validation report mapping displayed numbers to original artifact records.
- Deployment/privacy status and verified URL **only if actually deployed**.

## Acceptance criteria
- A researcher can replay one real firm's learning history and compare matched Random/Guided outcomes without fabricated values.
- At least sampled values from each view reconcile with versioned original artifacts.
- Existing economic rules and Game 1 scope remain unchanged.
- Accessibility, performance, provenance, and privacy requirements are tested or explicitly marked outstanding.
- Full Game 1 sign-off waits for independent website audit.

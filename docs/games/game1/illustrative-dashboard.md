# Game 1 illustrative dashboard — deployment and research status

## What currently works

The pull-request CI verifies the task-based market engine and exports a reproducible illustrative 200-round comparison. The website preview artifact bundles `site/index.html` with `site/economic-results.json`. The player-level plots include cumulative profit, round profit, output, capital and labor. A fallback proxy dashboard is shown if the economic JSON is unavailable or fails structural checks.

## Critical interpretation

**These numbers are not empirical findings or validated economic strategy rankings.** The current demonstration contains two behavioral policy labels (optimization and softmax) under a common task-capability setup. Choice scores, softmax temperature, inverse demand, costs and task aggregation are externally assigned illustration fixtures. They are not calibrated to real firms or derived from the approved full economic design. This is not a 256-strategy tournament, nor 100 initial configurations.

The explicit `ILLUSTRATIVE FIXTURE ONLY` warning is exported with the JSON and displayed on the website.

## Preview without publishing

Open the successful **Game 1 illustrative dashboard data** Actions run for the PR branch, then download the `game1-illustrative-site-preview` artifact. It contains the HTML and matching JSON. The `game1-illustrative-economic-results` artifact contains only JSON.

## Publishing after researcher's approval

1. Review the pull request; do not merge it without explicit approval.
2. Once approved and merged into `main`, verify the repository's GitHub Pages source is **GitHub Actions** (Settings → Pages).
3. In Actions, select **Publish illustrative Game 1 Pages demo** and choose **Run workflow** on `main`.
4. Confirm the deployment job succeeds and check the published site. The workflow's environment URL is the authoritative deployed address.
5. Verify the data-source label reads `economic-results.json` and the research warning remains visible. If it reads `data.json`, the site is showing the proxy fallback instead.

The deployment workflow deliberately has no automatic push or pull-request publication trigger. It requires explicit manual invocation on `main`.

## Research milestones not yet complete

- Define and approve distinct, economically interpretable behavioral strategy mechanisms and feasible choice sets.
- Execute the approved market comparison across the intended initial technology configurations, each with 200 rounds and common initial conditions across competing players.
- Verify accounting, reproducibility, sensitivity, parameter identification and robustness.
- Separate research findings from diagnostics and cite supporting economics literature for every substantive finding.

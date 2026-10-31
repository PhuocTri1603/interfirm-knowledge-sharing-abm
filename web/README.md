# Game 1 research website

Live English website: https://phuoctri1603.github.io/interfirm-knowledge-sharing-abm/

This is **replay of precomputed simulation data**, not a live simulation. Public website publication and the full repository's public visibility were explicitly authorized by the researcher on 2026-10-31. Economic mechanisms remain unchanged.

## Implemented views

- Simulation Overview: mean output efficiency and threshold attainment across 100 seeds, separately from selected-firm observations.
- Learning Trajectories: seed, technology, firm, 50/100/200-round horizon, seek, step, play/pause, speed, exact exported records and candidate/accepted states.
- Production Functions: four fixed-budget analytical curves, feasible optima and selected accepted-state observations; Linear optimum is constrained to share 0.95.
- Statistical Validation: mean within-seed paired firm relative output advantage, pointwise 95% Student-t intervals across 100 seed means, technology breakdown and attainment differences in percentage points.

Each horizon uses its **original artifact**, not truncated 200-round data. Population summaries are independent of the selected replay seed and are labeled accordingly.

## Reproduce locally

Python 3.11+ and Node.js are sufficient for these website tools. From repository root:

```bash
python -m unittest discover -s tests -p 'test_replay*.py' -v
node tests/test_production_view.cjs
node tests/test_replay_selection.cjs
node tests/test_horizon_requests.cjs
for horizon in 50 100 200; do
  python tools/build_replay_data.py verified-horizon${horizon}.zip --horizon $horizon --output web/data/$horizon --packed
  python tools/check_replay_sample.py verified-horizon${horizon}.zip --data web/data/$horizon
  python tools/check_replay_statistics.py verified-horizon${horizon}.zip --data web/data/$horizon
done
python -m http.server 8000 --bind 127.0.0.1 --directory web
```

Open http://127.0.0.1:8000. Do not use file://.

Original artifacts from run 41171674224 / source 40266bf38b644bb169fcb5d1358f9649ab7085cb: 50 rounds = 13031790079; 100 = 13031585631; 200 = 13030944570. Obtain them through authorized GitHub Actions downloads and save with the names above. The builder pins each ZIP SHA-256 and configuration, validates rows/keys/types and technology consistency, retains all rounds and exact parsed numbers, and writes lossless per-seed partitions plus summary.json. Generated data are excluded from Git. No credentials belong in frontend code.

## Statistics and verification

Advantage: average the matched firm-level relative percentages within a seed, then average 100 seeds. CI: mean ± t(99, .975) × sample SD / sqrt(100). Threshold attainment is %, while Guided − Random attainment is pp. Intervals are pointwise model-conditional Monte Carlo intervals; not simultaneous bands or empirical-firm inference. Unreached thresholds are censored for first-hit interpretation.

Revision dd0262c00a7a2841c1f911cb1874b20308fe35d0 deployed successfully in run 41192077110. Nine Python and three Node checks passed. All 7 million source history rows were processed. Exact partition checks reconciled 96/120/144 source records (all 14 fields) for horizons 50/100/200. A separately written raw-CSV checker independently reconciled 960/1200/1440 aggregate fields over 80k/100k/120k sampled-round rows. Maximum error 1.05084e-10, tolerance 1e-9. Its Student-t critical value is independently integrated/inverted.

Live browser checks passed: horizon artifact identity; shared round-50 values between 50/100; end-round statistics; seed 2125/firm 6 context; main control Tab order; source drawer; seek, step and play/pause from earlier checks. Desktop rendering was inspected. Selection/horizon error paths and overlapping-request recovery passed deterministic Node tests with minimal DOM/transport doubles.

## Deployment and limitations

Pages source: GitHub Actions, active branch experiment/game1-100-firms. Workflow downloads pinned artifacts, builds all horizons, runs independent checks, stages index.html and data only and enforces 900,000,000 bytes. Verified staged size: 865,048,661 bytes. Each selected seed loads only its horizon partition. Published data are public. Original Actions artifacts expire in January 2027; establish a durable reproducible input archive before expiry.

Independent static/numerical website review conditionally accepts the implemented scope; previously identified stale-data and failed-horizon recovery findings are closed. **Not fully tested:** real mobile/device rendering, assistive technologies, corrupt/offline transport in a real browser and rigorous performance benchmarks. The provided browser API did not expose viewport resizing or resource timing; these are not claimed passed.

The website is available for research inspection with documented limitations. **Whole Game 1 milestone remains OPEN** pending final acceptance of outstanding checks and broader model/literature review. See canonical docs/games/game1/research.md.

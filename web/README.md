# Game 1 replay — first vertical slice

Static replay of verified 200-round data. Public publication was authorized by the researcher on 2026-10-31. No simulation model is executed or modified. The English interface is deployed at https://phuoctri1603.github.io/interfirm-knowledge-sharing-abm/. Researcher authorization subsequently included making the entire research repository public. Pages uses GitHub Actions and permits the active experiment/game1-100-firms branch to deploy, alongside main. No merge into main was performed.

From repository root (Python 3.11+, standard library only):

```bash
python tools/build_replay_data.py /path/to/game1-horizon-200.zip --output web/data --packed
python -m unittest discover -s tests -p test_replay_data.py -v
python tools/check_replay_sample.py /path/to/game1-horizon-200.zip --data web/data
python -m http.server 8000 --bind 127.0.0.1 --directory web
```

Open http://127.0.0.1:8000. Do not open index.html directly with file://. Download GitHub Actions artifact 13030944570 from run 41171674224 with your authorized GitHub account. The builder rejects any ZIP with a different SHA-256/source commit. Never place a GitHub token in the frontend.

The builder processes all 4,000,000 original history rows, validates types/domains, per-seed unique keys and technology balance, then writes 100 partitions plus a manifest. JSON preserves parsed binary64 values and booleans; partitions retain every round. Generated data is intentionally excluded from Git. The --packed option writes lossless packed-v1 column arrays, with source optima stored once per technology per seed. The original 14-field row is reconstructed for inspection. All four million rows are retained; no downsampling or rounding. The packed output is approximately 494 MB (472 MiB), with ~5 MB per seed. Legacy object partitions are still readable.

Available: seed/technology/firm selection, paired policies, round seeking, play/pause, step, speed, exact source-row drawer, candidate/accepted state and implied K/L. Horizon is fixed at 200; no 50/100 option or population statistics is claimed. The full trajectory is visible with a selected-round marker.

In secure contexts the browser verifies SHA-256 for each partition. Where Web Crypto is unavailable (some HTTP previews), it explicitly reports byte-count/row-count checks only; the original ZIP SHA-256 remains mandatory at build time. This fallback is not cryptographic verification of HTTP transport. Use localhost or HTTPS for Web Crypto.

Verification on 2026-10-31: full build completed (4 million rows, 100 partitions); four focused unittest cases passed. Browser smoke checks: initial load, four technology filters (25 firms each), round seek, stepping, play/pause, exact source drawer; source-row sample audit described in canonical research.md. Existing model suite, mobile, corrupt-network scenarios, all controls across all seeds, 50/100 horizons and independent milestone audit remain outstanding. pytest could not run in the execution environment because pytest is not installed; this is not a failed model test.

## GitHub Pages

`.github/workflows/game1-pages.yml` downloads artifact 13030944570 with the workflow token, verifies provenance/digest, runs the converter and 144-row source audit, enforces a 900 MB staging limit and deploys only index.html plus generated data. Audit documents, the original ZIP and tokens are not copied into the website; the research repository itself is now public by explicit researcher authorization. Every served dataset is public after deployment. The artifact expires in January 2027; renew the reproducible input/archival route before that date.

GitHub Pages is enabled with GitHub Actions as publishing source. Deployment and repository visibility are separate settings; both public publication and the repository visibility change were explicitly authorized by the researcher.

## Live verification — 2026-10-31

Deployed frontend revision: `4d4b311bca46cfd49abce331c0bfa3a449a5b237`; workflow run `41178512443`. Build tests, the 144-row source comparison and the deployment step completed successfully. The public HTTPS page loaded seed 2026 with SHA-256 verification and 40,000 records; English labels, status messages and Step forward were verified after deployment. Earlier deployment smoke checks also exercised seed 2027 and play/pause.

Additional live checks: all four technology filters show 25 eligible firms; Home/End on the round slider select rounds 1/200; the exact-source drawer opens. Seed-2026 firms 1–4 at round 200 reconcile with the previously audited output pairs in the canonical research record. These checks are implementation QA, not an independent raw-artifact re-audit or full milestone sign-off.

**Still not run:** mobile-device rendering, complete keyboard/focus audit, missing/corrupt-network scenarios, performance benchmarks and independent website audit. Overview, production curves, population statistics and 50/100-round products remain unimplemented. The whole Game 1 milestone remains open.

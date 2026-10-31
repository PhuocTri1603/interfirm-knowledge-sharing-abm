# Game 1 replay — first vertical slice

Static replay of verified 200-round data. Public publication was authorized by the researcher on 2026-10-31. No simulation model is executed or modified. GitHub Pages workflow is prepared; hosting must be enabled in repository Settings → Pages → Source: GitHub Actions. Deployment is not confirmed until the workflow and live URL are verified.

From repository root (Python 3.11+, standard library only):

```bash
python tools/build_replay_data.py /path/to/game1-horizon-200.zip --output web/data --packed
python -m unittest discover -s tests -p test_replay_data.py -v
python tools/check_replay_sample.py /path/to/game1-horizon-200.zip --data web/data
python -m http.server 8000 --bind 127.0.0.1 --directory web
```

Open http://127.0.0.1:8000. Do not open index.html directly with file://. Download private GitHub Actions artifact 13030944570 from run 41171674224 with your authorized GitHub account. The builder rejects any ZIP with a different SHA-256/source commit. Never place a GitHub token in the frontend.

The builder processes all 4,000,000 original history rows, validates types/domains, per-seed unique keys and technology balance, then writes 100 partitions plus a manifest. JSON preserves parsed binary64 values and booleans; partitions retain every round. Generated data is intentionally excluded from Git. The --packed option writes lossless packed-v1 column arrays, with source optima stored once per technology per seed. The original 14-field row is reconstructed for inspection. All four million rows are retained; no downsampling or rounding. The packed output is approximately 494 MB (472 MiB), with ~5 MB per seed. Legacy object partitions are still readable.

Available: seed/technology/firm selection, paired policies, round seeking, play/pause, step, speed, exact source-row drawer, candidate/accepted state and implied K/L. Horizon is fixed at 200; no 50/100 option or population statistics is claimed. The full trajectory is visible with a selected-round marker.

In secure contexts the browser verifies SHA-256 for each partition. Where Web Crypto is unavailable (some HTTP previews), it explicitly reports byte-count/row-count checks only; the original ZIP SHA-256 remains mandatory at build time. This fallback is not cryptographic verification of HTTP transport. Use localhost or HTTPS for Web Crypto.

Verification on 2026-10-31: full build completed (4 million rows, 100 partitions); four focused unittest cases passed. Browser smoke checks: initial load, four technology filters (25 firms each), round seek, stepping, play/pause, exact source drawer; source-row sample audit described in canonical research.md. Existing model suite, mobile, corrupt-network scenarios, all controls across all seeds, 50/100 horizons and independent milestone audit remain outstanding. pytest could not run in the execution environment because pytest is not installed; this is not a failed model test.

## GitHub Pages

`.github/workflows/game1-pages.yml` downloads artifact 13030944570 with the workflow token, verifies provenance/digest, runs the converter and 144-row source audit, enforces a 900 MB staging limit and deploys only index.html plus generated data. The private research repository, audit documents, original ZIP and tokens are not copied into the website. Every served dataset is public after deployment. The artifact expires in January 2027; renew the reproducible input/archival route before that date.

GitHub Pages must already be enabled with GitHub Actions as publishing source. The GitHub account plan must support Pages from a private repository; otherwise use a separate public website repository, without changing the research repository visibility. Do not make the whole research repository public merely to resolve a Pages limitation.

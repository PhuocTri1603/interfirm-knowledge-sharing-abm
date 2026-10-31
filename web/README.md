# Game 1 replay — first vertical slice

Static, local-only replay of verified 200-round data. No simulation model is executed or modified. No hosting has been provisioned.

From repository root (Python 3.11+, standard library only):

```bash
python tools/build_replay_data.py /path/to/game1-horizon-200.zip --output web/data
python -m unittest discover -s tests -p test_replay_data.py -v
python tools/check_replay_sample.py /path/to/game1-horizon-200.zip --data web/data
python -m http.server 8000 --bind 127.0.0.1 --directory web
```

Open http://127.0.0.1:8000. Do not open index.html directly with file://. Download private GitHub Actions artifact 13030944570 from run 41171674224 with your authorized GitHub account. The builder rejects any ZIP with a different SHA-256/source commit. Never place a GitHub token in the frontend.

The builder processes all 4,000,000 original history rows, validates types/domains, per-seed unique keys and technology balance, then writes 100 partitions plus a manifest. JSON preserves parsed binary64 values and booleans; partitions retain every round. Generated data is intentionally excluded from Git. Allow approximately 2 GB disk for expanded JSON in this initial object-based format. The browser requests one seed (~20 MB), not the entire dataset; further compact encoding/per-firm partitioning remains a performance improvement.

Available: seed/technology/firm selection, paired policies, round seeking, play/pause, step, speed, exact source-row drawer, candidate/accepted state and implied K/L. Horizon is fixed at 200; no 50/100 option or population statistics is claimed. The full trajectory is visible with a selected-round marker.

In secure contexts the browser verifies SHA-256 for each partition. Where Web Crypto is unavailable (some HTTP previews), it explicitly reports byte-count/row-count checks only; the original ZIP SHA-256 remains mandatory at build time. This fallback is not cryptographic verification of HTTP transport. Use localhost or HTTPS for Web Crypto.

Verification on 2026-10-31: full build completed (4 million rows, 100 partitions); four focused unittest cases passed. Browser smoke checks: initial load, four technology filters (25 firms each), round seek, stepping, play/pause, exact source drawer; source-row sample audit described in canonical research.md. Existing model suite, mobile, corrupt-network scenarios, all controls across all seeds, 50/100 horizons and independent milestone audit remain outstanding. pytest could not run in the execution environment because pytest is not installed; this is not a failed model test.

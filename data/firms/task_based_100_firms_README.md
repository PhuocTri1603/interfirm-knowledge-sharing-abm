# 100 task-based firms — approved initial population

**Status:** Approved by principal researcher on 2026-11-03 as the initial synthetic 100-firm population for Game 1. This approval covers the population profiles and task-level dataset; it does not establish simulation outcomes or approve unmodeled economic mechanisms.

- `task_based_100_firms_profiles.csv`: 100 firms with K, L, K/L, resource scale, provisional cash, automation capability, productivity summaries and Vietnamese individual portraits.
- `task_based_100_firms_tasks.csv`: 2,000 firm-task records (20 shared tasks per firm), labor productivity, potential capital productivity and automation eligibility.
- Deterministic JS xorshift32 seed: `20261103` (GitHub CSV population generated for repository; not byte-identical to earlier local Python/Excel preview).
- 34 labor-oriented, 32 balanced, 34 capital-oriented; K/L bands 0.3–0.75, 0.8–1.25, 1.5–3.4; normalized K+L scale 65–180; task productivity uniform 0.7–1.3; automation eligibility count 2–12 of 20.
- Cash 15–90 is **provisional**, not an approved financial-capacity rule; generated independently of scale.
- Eligibility means the task *can* be automated, not that automation has been adopted. Potential capital productivity is recorded for all tasks.
- K+L is a descriptive normalized resource index, **not** economic cost; no wages, rental rates, prices, profit, output, or equilibrium are inferred.
- No correlation is deliberately imposed between task productivity and automation eligibility, but finite-sample correlations need not be exactly zero.
- No firm is preassigned superior profits, adoption or cooperation.

Research context: [Game 1 design](../../docs/games/game1/design.md), [theoretical charter](../../docs/theoretical_charter.md).

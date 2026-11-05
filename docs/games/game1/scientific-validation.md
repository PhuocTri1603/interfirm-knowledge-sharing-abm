# Game 1: scientific validation ledger

Status: **verification in progress; research_validated=false**. Technical completion of 100 × 256 × 200 is not proof of an economic mechanism. The diagnostic market is an illustrative scenario, not an approved PhD specification.

| Gate | Evidence | Current decision |
| --- | --- | --- |
| 1. Execution | GitHub Actions run 41971828596, 5,120,000 observations and artifact 13390269760 | Technical run passed; subsequent verification suite is separate |
| 2. Production | task feasibility tests and `task_ces_reference.py` tests for alpha=0.5, A fixed, sigma and Cobb–Douglas limit | **Not validated**: the actual diagnostic uses additive task activity; CES reference is not integrated; AI shock and substitution mapping not specified |
| 3. Market | quantity bounds, reserve-price checks, accounting identities in `task_mixed_market.py` | **Not validated**: illustrative inverse demand, rationing and cost assumptions; no equilibrium or calibrated demand |
| 4. Learning | policy-action tests for all compatible L3–L6 combinations, feedback and seeded reproducibility | **Not validated**: 16 adaptive × imitation identities use own-score optimization fallback, not imitation; no convergence evidence |
| 5. Robustness | reproducibility check for identical seed | **Not validated**: independent seeds, demand/technology perturbations, AI vs no-AI counterfactual and confidence intervals not yet executed |

## Approval-dependent economic decisions

1. **Production:** specify whether a CES K/L aggregator or a task-based assignment production function is the actual Game 1 mechanism. A CES benchmark alone is insufficient. Define sigma, the AI shock, and capital/labor feasibility, retaining A constant and alpha=0.5 where applicable.
2. **Market:** specify whether competition is Cournot, price competition or another explicit clearing institution, plus inverse demand, cost, and information assumptions. Current illustrative clearing computes price from total supply before reserve-price exclusion, so it is not asserted to be a competitive equilibrium.
3. **Information semantics:** adaptive means own-history only, while imitation requires peer actions/payoffs. Decide whether adaptive × imitation becomes a sequential observation regime or is excluded from scientifically comparable identities. Do not relabel own-score optimization as imitation.
4. **Sensitivity:** pre-register random seeds, parameter grids, convergence criterion, counterfactual definitions, summary estimands and uncertainty intervals before interpreting rankings.

## Release gate

`research_validated` must remain false until approved production/market specifications are implemented, all semantic conflicts resolved, and mechanism tests plus multi-seed/counterfactual/sensitivity reports are reproducible and reviewed. Passing CI is **necessary but not sufficient**. Do not silently flip the flag.

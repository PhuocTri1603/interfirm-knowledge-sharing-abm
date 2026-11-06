# Game 1 — 256 strategy labels: economic mechanisms and literature map

**Status (2026-11-06):** All 256 identities are registered; several option-level economic meanings have been approved, but 256 fully implemented and scientifically validated policies **do not yet exist**. This document is synchronized to the later authoritative decisions in `normalized_economic_specification.md`. Unapproved operating equations and numerical parameters remain OPEN. **Researcher design rule (2026-11-04): every L3 × L4 × L5 × L6 combination is a distinct player identity; no combination is excluded due to conceptual overlap.**

**Identity:** S001–S256 in [strategy_catalog_256.csv](strategy_catalog_256.csv), lexicographic nested product L3 × L4 × L5 × L6, in the order in the canonical `task_layer_registry.py`. Each row points to four option-level references below. L1/L2 describe production technology; L7 describes market regimes; none belongs in the count of 256 behavioral labels.

## Game boundary and precedence

**Game 1:** each firm learns from its **own** decisions, outcomes and history, plus approved common market signals. **Game 2:** firms may additionally observe individual rivals and use those observations in decisions. Game 1 must retain self-learning across rounds. The researcher-approved 256-player design is L3 × L4 × L5 × L6, with no excluded combinations. Later explicit researcher corrections supersede older speculative descriptions, especially any L3 capital-purchase interpretation. Do not treat an option name or diagnostic code as proof of implemented economic behavior.

## L3 — Resource allocation and adjustment constraints

**Economic question:** Which resource or adjustment friction bounds the firm's feasible action set?

| Code | Current economic interpretation and approval | Economic anchor | Still OPEN |
|---|---|---|---|
| flexible | **Approved meaning:** reallocate existing K/L across tasks within common fixed endowments, without extra task-capacity or adjustment restriction | Varian (1992), production/cost theory | Common actionable allocation rule |
| capacity | **Approved:** extra task throughput bound `0 <= q_ijt <= h_ij`, beyond common K/L limits | Varian (1992), constrained production | Pre-treatment `h_ij` initialization and binding cases |
| adjustment | **Approved conceptual distinction:** genuine friction/cost or feasibility limit when reallocating existing K/L across rounds; the rotating task-weight heuristic is **not** this mechanism | Adjustment-friction literature, including Abel & Eberly (1994), as analogy rather than capital-acquisition requirement | Exact minimal friction rule and initial reference allocation |
| investment | **Approved, controlling interpretation:** prioritize reallocating **existing fixed K** to tasks **already capital-eligible** when the decision is made; **no purchase or accumulation of K** | Varian (1992), scarce-input allocation and opportunity cost; task automation framework of Acemoglu & Restrepo (2018) | Exact priority decision rule; no new investment-stock, depreciation, financing or terminal-value model |

Historical references for adjustment-friction context (not authorization to purchase K): https://www.nber.org/papers/w4296 ; https://press.princeton.edu/books/hardcover/9780691034102/investment-under-uncertainty

**Common feasibility:** `sum_j k_ijt <= K_i` and `sum_j l_ijt <= Lbar_i` for all L3 options. L3 `investment` is a historical strategy ID only, not an asset purchase. L4 determines effective capital eligibility; L3 chooses allocation. Four alternative policies are a research design, not an exhaustive theory of firms.

## L4 — Automation channel

**Economic question:** Through which margin can AI/automation change task execution?

| Code | Proposed interpretation, **not yet approved** | Economic anchor | Modeling gap |
|---|---|---|---|
| eligibility | AI enables capital execution in previously labor-only tasks; approved conceptual channel | Acemoglu & Restrepo (2018), *The Race between Man and Machine* | Eligibility transition scope and timing |
| efficiency | AI raises capital-task productivity in eligible tasks; approved conceptual channel | Acemoglu & Restrepo (2018), *Modeling Automation* | Gain function, timing and persistence |
| adoption_cost | **Approved:** real payment **in exchange for unlocking capital eligibility in a previously labor-only task**, not a fee without benefit | Acemoglu & Restrepo (2018), automation; adoption-cost literature | Amount, charging unit, activation and persistence |
| combined | Combines eligibility, efficiency and adoption-cost channels; retain distinct identity, avoid double-charging unlocks | Acemoglu & Restrepo (2018) plus adoption frictions; model synthesis | Precise event/fee overlap and transition rule |

References: https://doi.org/10.1257/aer.20160696 ; https://doi.org/10.1257/pandp.20181020 ; https://www.nber.org/papers/w4296

**Caution:** Adoption cost is a friction, not a technological effect by itself. Therefore L4 mixes mechanisms and costs; the researcher may later prefer a factorial design rather than four mutually exclusive labels. No literature claims the four labels are exhaustive.

## L5 — Market interaction / expectations

**Economic question:** What market signal or strategic interdependence enters the player's choice?

| Code | Proposed interpretation, **not yet approved** | Economic anchor | Modeling gap |
|---|---|---|---|
| competitive | Price-taking expectation: firm does not internalize own output's effect on market price | Varian (1992), competitive firm | Operational forecast rule in common market |
| cournot | Firm internalizes own output's effect on aggregate price, **without observing individual rival actions** in Game 1 | Cournot (1838); Tirole (1988) | Own-impact expectation under approved aggregate information |
| price | Explicit price-offer strategy; requires an economically coherent sales/allocation mechanism | Bertrand (1883); Tirole (1988) | How offers transact with quantity strategies; current quantity-only runner insufficient |
| adaptive | Adapt choices using **own realized action–payoff history only** | Erev & Roth (1998); Sutton & Barto (2018) | Consistent action-value update and distinction from L6 selection |

References: https://press.princeton.edu/books/paperback/9780691096010/learning-and-expectations-in-macroeconomics ; Tirole (1988), MIT Press, ISBN 9780262200714.

**Caution:** `competitive`, `cournot`, and `price` describe distinct market games, whereas `adaptive` uses only own realized action–payoff history. **All four are retained as player-level choices, including every cross-layer combination.** Price and quantity players may coexist in the same market; a common transaction mechanism need not imply a common price or identical choice variable.

## L6 — Choice and learning rule

**Economic question:** How does the player select an action from feasible alternatives?

| Code | Proposed interpretation, **not yet approved** | Economic anchor | Modeling gap |
|---|---|---|---|
| optimization | Choose highest estimated payoff among **available feasible candidates**; do not claim global optimum | Varian (1992) | Candidate set and payoff estimation |
| trial_error | Explore alternatives and update choices from **own realized outcomes** | Erev & Roth (1998) | Genuine own-feedback update; random exploration alone insufficient |
| softmax | probabilistic logit choice weighted by expected utilities/values | McFadden (1974), *Conditional Logit Analysis of Qualitative Choice Behavior*, in *Frontiers in Econometrics*; Sutton & Barto (2018), *Reinforcement Learning*, 2nd ed. | Specify value learning and temperature; softmax alone is a selection rule, not learning |
| imitation | **UNRESOLVED conflict:** existing code imitates observed peers, but Game 1 **prohibits rival-specific observations**. Retain label and all 64 associated identities; do **not** silently redefine or implement peer imitation as Game 1 self-learning | Ellison & Fudenberg (1993) is a **Game 2 social-learning reference**, not evidence for own-only imitation | Researcher must approve an own-information-consistent meaning or defer this mechanism's operationalization; no assumed peer data |

References: https://dash.harvard.edu/entities/publication/73120378-866f-6bd4-e053-0100007fdf3b ; https://www.jstor.org/stable/2646959 ; https://www.andrew.cmu.edu/user/alm3/presentations/mcfadden1974.pdf

**Critical boundary:** Game 1 cannot expose individual peer actions/payoffs even when L6=`imitation` or L5=`adaptive`. The current engine's `peer_provider` imitation is a **code/spec mismatch**, not an approved Game 1 rule. McFadden motivates choice probabilities, not a dynamic value update. The full registry stays intact while the conflict is unresolved.

## Required before full-sample execution

1. Preserve the complete 4×4×4×4 Cartesian product: 256 distinct player identities, with no exclusion filter. Resolve information tensions (e.g. Adaptive × Imitation) by explicit rules rather than deleting a combination.
2. Preserve L4's four named options in the full player roster; document overlapping mechanisms without removing combinations.
3. Operationalize only researcher-approved mechanisms, with common feasible endowments and own-information-only learning in Game 1. Resolve the L6 imitation conflict without assuming rival observations.
4. Run strategy-distinctness tests: at least one designed state in which each relevant option changes decisions, not merely its label.
5. Only then execute 100 configurations × 256 validated policies × 200 rounds; include replication seeds and report confidence/robustness, not one deterministic ranking. `research_validated: false` until tests and scientific checks actually pass.

## Core bibliographic references

- Abel, A. B., & Eberly, J. C. (1994). A unified model of investment under uncertainty. *American Economic Review*, 84(5), 1369–1384.
- Acemoglu, D., & Restrepo, P. (2018). The race between man and machine: Implications of technology for growth, factor shares, and employment. *American Economic Review*, 108(6), 1488–1542. https://doi.org/10.1257/aer.20160696
- Acemoglu, D., & Restrepo, P. (2018). Modeling automation. *AEA Papers and Proceedings*, 108, 48–53. https://doi.org/10.1257/pandp.20181020
- Bertrand, J. (1883). Review of *Théorie mathématique de la richesse sociale* and *Recherches sur les principes mathématiques de la théorie des richesses*. *Journal des Savants*, 499–508.
- Cournot, A. A. (1838). *Recherches sur les principes mathématiques de la théorie des richesses*. Hachette.
- Dixit, A. K., & Pindyck, R. S. (1994). *Investment under Uncertainty*. Princeton University Press.
- Ellison, G., & Fudenberg, D. (1993). Rules of thumb for social learning. *Journal of Political Economy*, 101(4), 612–643. https://doi.org/10.1086/261890
- Erev, I., & Roth, A. E. (1998). Predicting how people play games: Reinforcement learning in experimental games with unique, mixed strategy equilibria. *American Economic Review*, 88(4), 848–881.
- Evans, G. W., & Honkapohja, S. (2001). *Learning and Expectations in Macroeconomics*. Princeton University Press.
- McFadden, D. (1974). Conditional logit analysis of qualitative choice behavior. In P. Zarembka (Ed.), *Frontiers in Econometrics* (pp. 105–142). Academic Press.
- Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press.
- Tirole, J. (1988). *The Theory of Industrial Organization*. MIT Press.
- Varian, H. R. (1992). *Microeconomic Analysis* (3rd ed.). W. W. Norton.

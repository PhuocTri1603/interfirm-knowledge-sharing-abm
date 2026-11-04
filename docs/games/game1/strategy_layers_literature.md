# Game 1 — 256 strategy labels: economic mechanisms and literature map

**Status:** The 256 combinations are **labels**, not 256 implemented or empirically validated policies. The principal researcher must approve operational definitions, parameters, information sets and economic identification before running a research tournament.

**Identity:** S001–S256 in [strategy_catalog_256.csv](strategy_catalog_256.csv), lexicographic nested product L3 × L4 × L5 × L6, in the order in the canonical `task_layer_registry.py`. Each row points to four option-level references below. L1/L2 describe production technology; L7 describes market regimes; none belongs in the count of 256 behavioral labels.

## L3 — Resource and adjustment constraints

**Economic question:** Which resource or adjustment friction bounds the firm's feasible action set?

| Code | Proposed interpretation, **not yet approved** | Economic anchor | Modeling gap |
|---|---|---|---|
| flexible | K/L can be reallocated within endowment without extra adjustment friction | Varian (1992), *Microeconomic Analysis*, production and cost theory | Specify feasibility, timing and opportunity cost |
| capacity | binding installed capacity/endowment constrains task activity | Varian (1992), *Microeconomic Analysis*, constrained cost minimization | Define capacity constraints per task versus firm |
| adjustment | changing K/L allocation across rounds incurs convex or fixed adjustment costs | Abel & Eberly (1994), *A Unified Model of Investment Under Uncertainty*, AER 84(5), 1369–1384 | Define adjustment cost and state persistence |
| investment | firm can expand productive capacity with an investment decision subject to irreversibility/uncertainty | Dixit & Pindyck (1994), *Investment under Uncertainty*, Princeton UP; Abel & Eberly (1994) | Define budget, capital law of motion and irreversibility |

References: https://www.nber.org/papers/w4296 ; https://press.princeton.edu/books/hardcover/9780691034102/investment-under-uncertainty

**Caution:** These options mix baseline feasibility and intertemporal frictions; they are not necessarily mutually exclusive in a real firm. Treating them as four mutually exclusive experiment regimes is a **research design choice**, not a proposition from the literature.

## L4 — Automation channel

**Economic question:** Through which margin can AI/automation change task execution?

| Code | Proposed interpretation, **not yet approved** | Economic anchor | Modeling gap |
|---|---|---|---|
| eligibility | automation makes previously labor-only tasks capital-feasible | Acemoglu & Restrepo (2018), *The Race between Man and Machine*, AER 108(6), 1488–1542 | Define eligibility transition and task index |
| efficiency | productivity rises in tasks already executable by capital | Acemoglu & Restrepo (2018), *Modeling Automation*, AEA Papers and Proceedings 108, 48–53 | Define capital task-efficiency shock |
| adoption_cost | adoption entails a fixed/sunk cost, creating an investment threshold | Dixit & Pindyck (1994); Abel & Eberly (1994) | Define fixed cost and adoption persistence |
| combined | allow eligibility, efficiency and adoption cost together | Acemoglu & Restrepo (2018) **plus** investment-friction literature | Combination is a model synthesis, not a separate published theory |

References: https://doi.org/10.1257/aer.20160696 ; https://doi.org/10.1257/pandp.20181020 ; https://www.nber.org/papers/w4296

**Caution:** Adoption cost is a friction, not a technological effect by itself. Therefore L4 mixes mechanisms and costs; the researcher may later prefer a factorial design rather than four mutually exclusive labels. No literature claims the four labels are exhaustive.

## L5 — Market interaction / expectations

**Economic question:** What market signal or strategic interdependence enters the player's choice?

| Code | Proposed interpretation, **not yet approved** | Economic anchor | Modeling gap |
|---|---|---|---|
| competitive | price-taking benchmark; agent treats market price as exogenous to its own output | Varian (1992), *Microeconomic Analysis*, competitive firm | Clarify if this is a belief under shared endogenous pricing |
| cournot | quantity competition; firm recognizes effect of its output on aggregate market price | Cournot (1838), *Recherches sur les principes mathématiques de la théorie des richesses*; Tirole (1988), *The Theory of Industrial Organization* | Specify rivals' quantity expectations and best-response timing |
| price | price competition, requiring an explicit price-choice and demand-allocation mechanism | Bertrand (1883), review of Cournot; Tirole (1988) | **Incompatible with a quantity-only decision API until price actions are added** |
| adaptive | market expectations updated from past observed prices/quantities | Evans & Honkapohja (2001), *Learning and Expectations in Macroeconomics*, Princeton UP | Specify updating rule, memory and information |

References: https://press.princeton.edu/books/paperback/9780691096010/learning-and-expectations-in-macroeconomics ; Tirole (1988), MIT Press, ISBN 9780262200714.

**Caution:** `competitive`, `cournot`, and `price` describe distinct market games, whereas `adaptive` describes belief updating that could occur in any of them. They are **not four mutually exclusive strategies on the same conceptual axis**. Before treating L5 as a strategy layer, the researcher must decide whether to separate market structure from expectations.

## L6 — Choice and learning rule

**Economic question:** How does the player select an action from feasible alternatives?

| Code | Proposed interpretation, **not yet approved** | Economic anchor | Modeling gap |
|---|---|---|---|
| optimization | choose feasible action with highest expected payoff under an explicit information set | Varian (1992), *Microeconomic Analysis* | Finite-choice versus global optimum, forecasting beliefs |
| trial_error | experiment with actions and update choice using realized own outcomes | Erev & Roth (1998), *Predicting How People Play Games: Reinforcement Learning in Experimental Games with Unique, Mixed Strategy Equilibria*, AER 88(4), 848–881 | Specify reinforcement/aspiration update; random exploration alone is insufficient |
| softmax | probabilistic logit choice weighted by expected utilities/values | McFadden (1974), *Conditional Logit Analysis of Qualitative Choice Behavior*, in *Frontiers in Econometrics*; Sutton & Barto (2018), *Reinforcement Learning*, 2nd ed. | Specify value learning and temperature; softmax alone is a selection rule, not learning |
| imitation | use observed peers' choices/payoffs to guide own action | Ellison & Fudenberg (1993), *Rules of Thumb for Social Learning*, JPE 101(4), 612–643 | Specify peer observability and imitation criterion |

References: https://dash.harvard.edu/entities/publication/73120378-866f-6bd4-e053-0100007fdf3b ; https://www.jstor.org/stable/2646959 ; https://www.andrew.cmu.edu/user/alm3/presentations/mcfadden1974.pdf

**Caution:** McFadden motivates probabilistic utility choice; it does **not** by itself validate a particular dynamic learning update. Ellison–Fudenberg studies social learning, not necessarily copying the highest-profit competitor. These mappings are theoretical starting points.

## Required before full-sample execution

1. Decide whether L5 market structures should be moved to L7, with `adaptive` modeled separately.
2. Decide whether L4 adoption cost should be a crossed friction rather than a mutually exclusive technology channel.
3. Approve exact equations for all option mechanisms, state transitions, observability and prices, keeping common conditions across strategies in each market.
4. Run strategy-distinctness tests: at least one designed state in which each relevant option changes decisions, not merely its label.
5. Only then execute 100 configurations × 256 validated policies × 200 rounds; include replication seeds and report confidence/robustness, not one deterministic ranking.

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

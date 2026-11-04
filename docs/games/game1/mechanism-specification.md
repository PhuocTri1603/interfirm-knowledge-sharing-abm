# Game 1 — L1–L6 economic mechanism specification plan

**Status:** Literature-grounded research design. These are hypotheses and
candidate implementations, not approved calibrated mechanisms or results.

## Identification principle

Keep a clean separation between (a) technology/task feasibility, (b) input
adjustment and AI investment, (c) information and competition, and (d)
learning/choice. Holding the initial K and L fixed within each original
profile isolates strategic variation in the simulated environment; it does
not prove external validity. Common random numbers are desirable for
matched stochastic counterfactuals.

## Layer-to-theory map

| Layer | Candidate economic interpretation | Theoretical anchor | Main identification risk |
|---|---|---|---|
| L1 task technology | assignment / CES / Leontief / hybrid are distinct *task-aggregation or assignment* mechanisms | Acemoglu & Restrepo (2018); Varian (1992) | L1 overlaps with L2 unless task allocation and aggregation are separated |
| L2 within-task substitution | linear / Leontief / CES represent different factor substitution possibilities | Arrow et al. (1961); Varian (1992) | Existing within-task activity is linear; Leontief and CES require new implementation |
| L3 dynamic constraint | flexible / capacity / adjustment / investment govern feasibility and intertemporal costs | Lucas (1967); Hayashi (1982) | Current TaskBasedFirm endowments are static; no capital law of motion |
| L4 AI adoption friction | eligibility / efficiency / adoption_cost / combined govern technology availability and fixed/variable adoption costs | Acemoglu & Restrepo (2018); Jovanovic & Nyarko (1996) | No AI adoption state or cost accounting yet |
| L5 competitive information | competitive / cournot / price / adaptive must be operationally distinguished by beliefs and observable signals | Cournot (1838); Vives (1999) | All players currently clear at one price; L5 should not silently create four incompatible market structures |
| L6 learning | optimization / trial_error / softmax / imitation are different choice/update mechanisms | Sutton & Barto (2018); Schlag (1998); Posen & Levinthal (2012) | Current trial-error stores history but has no reward-based updating rule; imitation requires observable peer information |

**Interpretation constraint:** L5 concerns *beliefs and decision rules inside
the same Mixed Market*, whereas L7 changes market organization. Otherwise
the 3,072 strategies are not compared within a common market mechanism.

## Implementation sequence

1. Specify the 20-task production and aggregation rules, then test limiting
   cases for linear, Leontief and CES. Do not infer task coefficients from
   the old four-form CSV without a documented mapping.
2. Specify investment state transitions, capital/labor adjustment costs,
   AI adoption eligibility and costs, with accounting identities.
3. Specify the information set at each round: only previous market price and
   quantity are available in the current dynamic runner. Additional
   observations require explicit modeled disclosure.
4. Bind L6 to executable policies and demonstrate distinct behavior under
   controlled counterexamples, not merely distinct class names.
5. Audit all 23 option definitions, calibrate demand/technology/cost scales,
   and only then run the 100x3072x200 Mixed benchmark.

## Sources

- Acemoglu, D., & Restrepo, P. (2018). The Race between Man and Machine:
  Implications of Technology for Growth, Factor Shares, and Employment.
  *American Economic Review*, 108(6), 1488–1542.
  https://doi.org/10.1257/aer.20160696
- Arrow, K. J., Chenery, H. B., Minhas, B. S., & Solow, R. M. (1961).
  Capital-Labor Substitution and Economic Efficiency. *Review of Economics
  and Statistics*, 43(3), 225–250.
  https://doi.org/10.2307/1927286
- Lucas, R. E. Jr. (1967). Adjustment Costs and the Theory of Supply.
  *Journal of Political Economy*, 75(4), 321–334.
- Hayashi, F. (1982). Tobin's Marginal q and Average q: A Neoclassical
  Interpretation. *Econometrica*, 50(1), 213–224.
- Jovanovic, B., & Nyarko, Y. (1996). Learning by Doing and the Choice of
  Technology. *Econometrica*, 64(6), 1299–1310.
- Vives, X. (1999). *Oligopoly Pricing: Old Ideas and New Tools*. MIT Press.
- Schlag, K. H. (1998). Why Imitate, and If So, How? A Boundedly Rational
  Approach to Multi-Armed Bandits. *Journal of Economic Theory*, 78(1), 130–156.
- Posen, H. E., & Levinthal, D. A. (2012). Chasing a Moving Target:
  Exploitation and Exploration in Dynamic Environments. *Management Science*,
  58(3), 587–601.
- Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning:
  An Introduction* (2nd ed.). MIT Press.

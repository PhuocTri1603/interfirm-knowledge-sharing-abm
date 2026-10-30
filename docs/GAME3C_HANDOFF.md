# Game 3C — Research and Development Handoff

Last updated: 2026-10-27
Status: Core learning and knowledge-pool components tested.
Next task: Integrate Game 3C simulation.

## 1. Research context

Working research title:

Inter-Firm Knowledge Sharing under Technological Heterogeneity:
Organizational Learning, Strategic Disclosure, and AI-Related Investment.

Research focus:
- Agent-based modeling of interfirm learning and knowledge sharing.
- Technological heterogeneity across firms.
- Strategic Share/Withhold decisions.
- Conditional reciprocity and access to external knowledge.
- Adaptive learning under technological change.

Hypotheses:
- H1: Knowledge sharing accelerates organizational learning.
- H2: Technological heterogeneity affects knowledge-transfer benefits.
- H3: Competition discourages voluntary disclosure.

Important limitation:
The current ABM primarily models production-output improvement.
H3 requires a future market competition/profit mechanism.
Do not claim that H3 has already been tested.

WBES Vietnam Enterprise Survey 2023 and laboratory experiments
are proposed empirical extensions, not completed empirical studies.

## 2. Existing repository

Local repository:
~/research/interfirm-knowledge-sharing-abm

Environment:
- macOS
- Conda environment: interfirm-abm
- Python 3.11
- pytest

Existing components:
- Game 1: Baseline production and technological change.
- Game 2: Competitive observational learning.
- Game 3A: Cooperative learning.
- Game 3B: Cross-technology knowledge transfer.
- Game 3C: Adaptive disclosure and conditional reciprocity.

Do not change Game 3A or Game 3B semantics.

Existing production technologies:
- Cobb-Douglas
- Leontief
- Linear
- CES

Firm experiments:
- Each firm performs at most one experiment per round.
- Candidate capital share is evaluated.
- An experiment is accepted only if output strictly improves.
- Experiment history records accepted status and output.

## 3. Game 3C design decisions

### 3.1 Disclosure decision

Only a new successful experiment is eligible for disclosure.

After success, the firm chooses:
- Share
- Withhold

Failed experiments:
- No disclosure decision.
- No reputation update.
- No disclosure cost.

A withheld experiment is never published later.

### 3.2 Adaptive disclosure

Method:
- Trial-and-Error learning.
- Softmax action selection.
- Q-values for Share and Withhold.

Initial Q-values:
Q_share = 0
Q_withhold = 0

Share probability:

P(Share) =
1 / (1 + exp(-(Q_share - Q_withhold) / tau))

Baseline temperature:
tau = 0.01

Sensitivity:
tau in {0.005, 0.01, 0.02}

Learning rate:
eta = 0.30

Sensitivity:
eta in {0.10, 0.30, 0.50}

Q-value update:
Q(a) <- Q(a) + eta * (R - Q(a))

Only the selected action's Q-value is updated.

### 3.3 Contribution history

Rolling window:
5 previous calendar rounds.

Only eligible Share/Withhold decisions count.

Reputation:

H(i,t) = (1 + s) / (2 + n)

Where:
- s = number of Share decisions in the previous 5 rounds.
- n = number of eligible disclosure decisions in that window.

Initial reputation:
H = 0.5

The current round's disclosure decision must not affect
the current round's access probability.

### 3.4 Conditional reciprocity

Baseline access probability:

P_access(i,t) = 0.10 + 0.80 * H(i,t)

Sensitivity specifications:
- Weak: 0.30 + 0.40 * H
- Strong: 0.02 + 0.96 * H
- Threshold: 0.20 if H < 0.5, otherwise 0.80
- No reciprocity: 0.50

Access lottery:
- One random draw per firm per round.
- Access is granted when draw < P_access.
- Use a reproducible random-number generator.
- Access is based on previous-round reputation.

### 3.5 Learning strategies

Baseline selection probabilities:
- Random exploration: 0.20
- Shared knowledge: 0.30
- Own-history guided: 0.50

If shared knowledge is unavailable:
- Random exploration: 2/7
- Own-history guided: 5/7

If own history is empty:
- Fall back to random exploration.

Maintain at most one firm experiment per round.

### 3.6 Selective knowledge pool

Only successful experiments explicitly marked Share
are published.

Knowledge availability:
- One-round lag.
- No access to own published experiments.
- Published knowledge persists.
- Withheld experiments are not published.
- Failed experiments are not published.

Access lottery is enforced at the simulation layer,
not inside SelectiveKnowledgePool.observe().

### 3.7 Disclosure cost

Cost applies only to Share:

cost = kappa * Y(i,t)

The cost is a reward penalty.
It does not physically reduce production output.

Baseline/sensitivity:
kappa in {0, 0.001, 0.005, 0.01, 0.02}

### 3.8 Delayed reward

Reward horizon:
5 future rounds.

Discount factor:
gamma = 0.95

Reward:

R(i,t) =
sum over k=1..5 [
    gamma^(k-1) * B_shared(i,t+k)
] / Y(i,t)
- kappa * I(Share)

Where B_shared is realized improvement from accepted
experiments using received knowledge.

Important:
- Reward is observational, not a causal estimate.
- Overlapping reward windows are allowed.
- Update Q-values only after the full 5-round window.
- Decisions in the last 5 simulation rounds remain pending.
- Do not assign zero rewards to incomplete windows.

## 4. Completed implementation

File:
src/interfirm_abm/disclosure_learning.py

Classes:
- DisclosureLearner
- ContributionHistory

Implemented and tested:
- Initial Q-values.
- Stable Softmax probability.
- Delayed reward accounting.
- Q-value updates.
- Rolling contribution history.
- Access probability.
- Access lottery using externally supplied random draw.

File:
src/interfirm_abm/selective_knowledge.py

Class:
- SelectiveKnowledgePool

Methods:
- publish(experiment, shared)
- observe(observer_id, round_number)

Implemented and tested:
- Share successful experiment.
- Withhold experiment.
- Reject failed experiment.
- One-round lag.
- Exclude own knowledge.
- Persistence of published knowledge.

## 5. Tests

tests/test_disclosure_learning.py
19 tests PASSED.

tests/test_selective_knowledge.py
6 tests PASSED.

Total:
25 Game 3C tests PASSED.

These results are from the user's Mac Terminal.

The full repository test suite has NOT yet been
rerun after the latest Game 3C additions.

## 6. Pending implementation

Primary next task:

Create:
src/interfirm_abm/disclosure_simulation.py

First inspect:
src/interfirm_abm/cooperative_simulation.py

Then inspect relevant Game 3B and Firm interfaces.

Integration requirements:
1. Initialize each firm's disclosure learner.
2. Initialize each firm's contribution history.
3. Initialize the selective knowledge pool.
4. Determine access once per firm per round.
5. Select learning strategy with proportional fallback.
6. Execute one experiment per firm per round.
7. Record realized gains from accepted shared learning.
8. Make Share/Withhold decisions only after success.
9. Publish only Share decisions.
10. Update contribution history.
11. Finalize matured delayed rewards.
12. Record simulation outputs and diagnostics.

Do not assume the integration is already implemented.

## 7. Planned experiments

Baseline:
- 20 firms.
- 50 rounds.
- 100 matched random seeds.

Later:
- Full kappa x eta x tau sensitivity grid.
- Reciprocity sensitivity.
- Technological heterogeneity comparisons.
- Appropriate comparisons with Game 3A and Game 3B.

All numerical findings must be labeled simulation results.

## 8. Development workflow

User preference:
- Communicate in Vietnamese.
- Proceed slowly and sequentially.
- Give exactly one Mac Terminal command/block at a time.
- Wait for the user's Terminal output before continuing.
- Use test-driven development.
- Do not execute the user's local repository elsewhere.
- Do not modify Game 3A or Game 3B behavior.

Next immediate command:

sed -n '1,260p' src/interfirm_abm/cooperative_simulation.py

After reading the actual code, design the Game 3C
simulation integration and write tests first.

## 9. Technical cautions

Review later:
- Duplicate disclosure decisions after finalization.
- Reward finalization timing relative to gain observation.
- Retroactive shared-gain recording.
- Input validation and deterministic random streams.
- Whether re-sharing learned knowledge should be allowed.

These are pending review items, not verified bugs.

## 10. Continuation instruction

Continue implementing Game 3C from this handoff.

Do not restart the theoretical design.
Do not rewrite completed modules without a specific reason.

First inspect the existing CooperativeSimulation implementation.
Then implement Game 3C integration through incremental tests.

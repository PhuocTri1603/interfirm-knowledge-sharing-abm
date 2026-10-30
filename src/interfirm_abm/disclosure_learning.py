"""Game 3C: adaptive disclosure learning and contribution history."""

import math


class DisclosureLearner:
    """Maintain action values for Share and Withhold."""

    def __init__(
        self,
        temperature=0.01,
        learning_rate=0.30,
        q_share=0.0,
        q_withhold=0.0,
    ):
        if not math.isfinite(temperature) or temperature <= 0:
            raise ValueError("Temperature must be positive and finite.")

        if not math.isfinite(learning_rate) or not 0 < learning_rate <= 1:
            raise ValueError("Learning rate must be in (0, 1].")

        if not all(math.isfinite(q) for q in (q_share, q_withhold)):
            raise ValueError("Initial Q-values must be finite.")

        self.temperature = float(temperature)
        self.learning_rate = float(learning_rate)
        self.q_share = float(q_share)
        self.q_withhold = float(q_withhold)

    def share_probability(self):
        """Numerically stable two-action Softmax."""
        difference = (
            self.q_share - self.q_withhold
        ) / self.temperature

        if difference >= 0:
            return 1.0 / (1.0 + math.exp(-difference))

        exp_difference = math.exp(difference)
        return exp_difference / (1.0 + exp_difference)


    def record_decision(
        self,
        round_number,
        shared,
        baseline_output,
        disclosure_cost_rate,
    ):
        """Register an eligible decision for delayed evaluation."""
        if not isinstance(round_number, int) or isinstance(round_number, bool) or round_number <= 0:
            raise ValueError("Round number must be a positive integer.")
        if not isinstance(shared, bool):
            raise ValueError("Shared must be boolean.")
        if not math.isfinite(baseline_output) or baseline_output <= 0:
            raise ValueError("Baseline output must be positive and finite.")
        if not math.isfinite(disclosure_cost_rate) or disclosure_cost_rate < 0:
            raise ValueError("Disclosure cost rate must be nonnegative and finite.")

        if not hasattr(self, "pending_decisions"):
            self.pending_decisions = []
        if not hasattr(self, "shared_gains"):
            self.shared_gains = {}

        if any(d["round"] == round_number for d in self.pending_decisions):
            raise ValueError("Decision already registered for this round.")

        self.pending_decisions.append({
            "round": round_number,
            "shared": shared,
            "baseline_output": float(baseline_output),
            "cost_rate": float(disclosure_cost_rate),
        })

    def observe_shared_gain(self, round_number, gain):
        """Record realized output improvement from received knowledge."""
        if not isinstance(round_number, int) or isinstance(round_number, bool) or round_number <= 0:
            raise ValueError("Round number must be a positive integer.")
        if not math.isfinite(gain) or gain < 0:
            raise ValueError("Shared gain must be nonnegative and finite.")

        if not hasattr(self, "shared_gains"):
            self.shared_gains = {}

        self.shared_gains[round_number] = (
            self.shared_gains.get(round_number, 0.0) + float(gain)
        )

    def finalize_rewards(self, round_number):
        """Finalize full five-round rewards and update chosen Q-values."""
        if not isinstance(round_number, int) or isinstance(round_number, bool) or round_number <= 0:
            raise ValueError("Round number must be a positive integer.")

        if not hasattr(self, "pending_decisions"):
            self.pending_decisions = []
        if not hasattr(self, "shared_gains"):
            self.shared_gains = {}

        matured = sorted(
            (d for d in self.pending_decisions if d["round"] + 5 <= round_number),
            key=lambda d: d["round"],
        )
        results = []

        for decision in matured:
            t = decision["round"]

            discounted_gain = sum(
                (0.95 ** (k - 1)) * self.shared_gains.get(t + k, 0.0)
                for k in range(1, 6)
            )

            reward = (
                discounted_gain / decision["baseline_output"]
                - (decision["cost_rate"] if decision["shared"] else 0.0)
            )

            if decision["shared"]:
                self.q_share += self.learning_rate * (
                    reward - self.q_share
                )
            else:
                self.q_withhold += self.learning_rate * (
                    reward - self.q_withhold
                )

            results.append({
                "round": t,
                "shared": decision["shared"],
                "reward": reward,
            })

        matured_rounds = {d["round"] for d in matured}
        self.pending_decisions = [
            d for d in self.pending_decisions
            if d["round"] not in matured_rounds
        ]

        return results


class ContributionHistory:
    """Rolling history of eligible disclosure decisions."""

    def __init__(self, window=5):
        if isinstance(window, bool) or not isinstance(window, int) or window <= 0:
            raise ValueError("Window must be a positive integer.")

        self.window = window
        self.decisions = {}

    def record(self, round_number, shared):
        """Record a decision after a successful experiment."""
        if isinstance(round_number, bool) or not isinstance(round_number, int) or round_number <= 0:
            raise ValueError("Round number must be a positive integer.")

        if not isinstance(shared, bool):
            raise ValueError("Shared must be a boolean.")

        if round_number in self.decisions:
            raise ValueError("Only one eligible decision per round.")

        self.decisions[round_number] = shared

    def reputation(self, round_number):
        """Use only decisions in the preceding rolling window."""
        if isinstance(round_number, bool) or not isinstance(round_number, int) or round_number <= 0:
            raise ValueError("Round number must be a positive integer.")

        start = max(1, round_number - self.window)

        eligible = [
            shared
            for decision_round, shared in self.decisions.items()
            if start <= decision_round < round_number
        ]

        n = len(eligible)
        s = sum(eligible)

        return (1.0 + s) / (2.0 + n)

    def access_probability(
        self,
        round_number,
        intercept=0.10,
        slope=0.80,
    ):
        """Compute access probability from prior contribution history."""
        if not math.isfinite(intercept) or not math.isfinite(slope):
            raise ValueError("Access parameters must be finite.")

        reputation = self.reputation(round_number)
        probability = intercept + slope * reputation

        if not 0.0 <= probability <= 1.0:
            raise ValueError("Access probability must be in [0, 1].")

        return float(probability)



    def check_access(
        self,
        round_number,
        draw,
        intercept=0.10,
        slope=0.80,
    ):
        """Determine access using an externally supplied random draw."""
        if not isinstance(draw, (int, float)) or not math.isfinite(draw):
            raise ValueError("Random draw must be a finite number.")

        if not 0.0 <= draw < 1.0:
            raise ValueError("Random draw must be in [0, 1).")

        probability = self.access_probability(
            round_number=round_number,
            intercept=intercept,
            slope=slope,
        )
        return bool(draw < probability)

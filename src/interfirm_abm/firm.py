"""
Firm agent for the minimal agent-based model.

Each firm learns through independent experimentation
with capital and labor allocation.
"""

from dataclasses import dataclass, field

import numpy as np

from interfirm_abm.production import (
    cobb_douglas,
    leontief,
    linear,
    ces,
)


PRODUCTION_FUNCTIONS = {
    "Cobb-Douglas": cobb_douglas,
    "Leontief": leontief,
    "Linear": linear,
    "CES": ces,
}


@dataclass
class Firm:
    firm_id: int
    technology: str
    budget: float = 100.0
    capital_share: float = 0.50
    history: list = field(default_factory=list)

    def __post_init__(self):
        if self.technology not in PRODUCTION_FUNCTIONS:
            raise ValueError("Unknown production technology.")

        if not np.isfinite(self.budget) or self.budget <= 0:
            raise ValueError("Budget must be positive and finite.")

        if not 0 < self.capital_share < 1:
            raise ValueError("Capital share must be between 0 and 1.")

        self.production_function = PRODUCTION_FUNCTIONS[
            self.technology
        ]

        self.current_output = self.produce(self.capital_share)

    def produce(self, capital_share):
        K = self.budget * capital_share
        L = self.budget * (1 - capital_share)

        return float(self.production_function(K, L))

    def experiment(self, candidate_share, round_number):
        if not 0 < candidate_share < 1:
            raise ValueError("Candidate share must be between 0 and 1.")

        candidate_output = self.produce(candidate_share)
        previous_output = self.current_output

        accepted = candidate_output > previous_output

        if accepted:
            self.capital_share = candidate_share
            self.current_output = candidate_output

        record = {
            "firm_id": self.firm_id,
            "round": round_number,
            "technology": self.technology,
            "candidate_share": candidate_share,
            "candidate_output": candidate_output,
            "accepted": accepted,
            "capital_share": self.capital_share,
            "current_output": self.current_output,
        }

        self.history.append(record)

        return record

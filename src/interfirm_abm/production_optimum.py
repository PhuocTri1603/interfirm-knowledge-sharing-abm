import numpy as np

from interfirm_abm.firm import PRODUCTION_FUNCTIONS


def optimal_capital_share(technology):
    if technology not in PRODUCTION_FUNCTIONS:
        raise ValueError("Unknown production technology.")

    if technology in ("Cobb-Douglas", "Leontief"):
        return 0.70

    if technology == "Linear":
        return 0.95

    if technology == "CES":
        alpha = 0.70
        rho = -0.50
        ratio = (alpha / (1 - alpha)) ** (1 / (1 - rho))
        return ratio / (1 + ratio)

    raise ValueError("Unknown production technology.")


def optimal_output(technology, budget=100.0):
    if not np.isfinite(budget) or budget <= 0:
        raise ValueError("Budget must be positive and finite.")

    share = optimal_capital_share(technology)
    production = PRODUCTION_FUNCTIONS[technology]

    return float(
        production(
            budget * share,
            budget * (1 - share),
        )
    )


def remaining_improvement_potential(
    technology,
    current_output,
    budget=100.0,
):
    optimum = optimal_output(technology, budget)

    if not np.isfinite(current_output):
        raise ValueError("Current output must be finite.")

    if current_output > optimum + 1e-8:
        raise ValueError("Current output exceeds feasible optimum.")

    return max(0.0, optimum - current_output)

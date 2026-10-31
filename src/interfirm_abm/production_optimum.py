"""Firm-specific constrained production optima for Game 1."""
import numpy as np
from interfirm_abm.firm import Firm, PRODUCTION_FUNCTIONS


def optimal_capital_share(technology, alpha=0.70, rho=-0.50):
    if technology not in PRODUCTION_FUNCTIONS:
        raise ValueError("Unknown production technology.")
    if not np.isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("alpha must be in (0,1).")
    if not np.isfinite(rho) or rho > 1:
        raise ValueError("rho must be finite and <= 1.")
    if technology in ("Cobb-Douglas", "Leontief"):
        share = alpha
    elif technology == "Linear":
        share = 0.95 if alpha > 0.5 else 0.05 if alpha < 0.5 else 0.5
    elif np.isclose(rho, 0, atol=1e-10):
        share = alpha
    elif rho == 1:
        share = 0.95 if alpha > 0.5 else 0.05 if alpha < 0.5 else 0.5
    else:
        ratio = (alpha / (1 - alpha)) ** (1 / (1 - rho))
        share = ratio / (1 + ratio)
    return float(np.clip(share, 0.05, 0.95))


def optimal_output(technology, budget=100.0, alpha=0.70, rho=-0.50, productivity=1.0):
    share = optimal_capital_share(technology, alpha=alpha, rho=rho)
    firm = Firm(firm_id=0, technology=technology, budget=budget,
                alpha=alpha, rho=rho, productivity=productivity)
    return firm.produce(share)


def remaining_improvement_potential(technology, current_output, budget=100.0,
                                    alpha=0.70, rho=-0.50, productivity=1.0):
    optimum = optimal_output(technology, budget, alpha, rho, productivity)
    if not np.isfinite(current_output):
        raise ValueError("Current output must be finite.")
    if current_output > optimum + 1e-8:
        raise ValueError("Current output exceeds feasible optimum.")
    return max(0.0, optimum - current_output)

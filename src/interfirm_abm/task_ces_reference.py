"""Reference CES mathematics for theoretical checks; NOT wired to Game 1 yet.

With alpha=0.5 and constant A, rho=(sigma-1)/sigma. CES at sigma=1
is the Cobb-Douglas continuous limit. These functions are reference
benchmarks; they do not turn the diagnostic linear task technology into CES.
"""
from __future__ import annotations
from math import exp, isfinite, log


def ces_output(k: float, l: float, sigma: float, a: float = 1.0, alpha: float = 0.5) -> float:
    if not all(isfinite(x) for x in (k, l, sigma, a, alpha)):
        raise ValueError("parameters must be finite")
    if k <= 0 or l <= 0 or sigma <= 0 or a <= 0 or not 0 < alpha < 1:
        raise ValueError("positive inputs and elasticity, alpha strictly between zero and one")
    if abs(sigma - 1.0) < 1e-10:
        return a * exp(alpha * log(k) + (1 - alpha) * log(l))
    rho = (sigma - 1.0) / sigma
    z1, z2 = log(alpha) + rho * log(k), log(1 - alpha) + rho * log(l)
    top = max(z1, z2)
    log_sum = top + log(exp(z1 - top) + exp(z2 - top))
    return a * exp(log_sum / rho)


def ces_mrt_ratio(k: float, l: float, sigma: float, alpha: float = 0.5) -> float:
    """MP_K / MP_L; theoretical first-order ratio."""
    if k <= 0 or l <= 0 or sigma <= 0 or not 0 < alpha < 1:
        raise ValueError("invalid CES inputs")
    return alpha / (1 - alpha) * (k / l) ** (-1.0 / sigma)

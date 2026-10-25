"""
Production functions for heterogeneous firms.

All four production functions exhibit
constant returns to scale in capital and labor.
"""

import numpy as np


def _validate_inputs(K, L):
    """Validate non-negative production inputs."""
    K = np.asarray(K, dtype=float)
    L = np.asarray(L, dtype=float)

    if np.any(~np.isfinite(K)) or np.any(~np.isfinite(L)):
        raise ValueError("K and L must be finite.")

    if np.any(K < 0) or np.any(L < 0):
        raise ValueError("K and L must be non-negative.")

    return K, L


def _validate_share(value, name):
    if not np.isfinite(value) or not 0 < value < 1:
        raise ValueError(f"{name} must be between 0 and 1.")


def cobb_douglas(K, L, alpha=0.7):
    """Cobb-Douglas: K^alpha * L^(1-alpha)."""
    K, L = _validate_inputs(K, L)
    _validate_share(alpha, "alpha")

    return K**alpha * L**(1 - alpha)


def leontief(K, L, kappa=0.7):
    """Leontief: min(K/kappa, L/(1-kappa))."""
    K, L = _validate_inputs(K, L)
    _validate_share(kappa, "kappa")

    return np.minimum(K / kappa, L / (1 - kappa))


def linear(K, L, alpha=0.7):
    """Linear: alpha*K + (1-alpha)*L."""
    K, L = _validate_inputs(K, L)
    _validate_share(alpha, "alpha")

    return alpha * K + (1 - alpha) * L


def ces(K, L, alpha=0.7, rho=-0.5):
    """
    CES production function.

    rho approaches zero: Cobb-Douglas limit.
    rho equals one: Linear production.
    """
    K, L = _validate_inputs(K, L)
    _validate_share(alpha, "alpha")

    if not np.isfinite(rho) or rho > 1:
        raise ValueError("rho must be finite and <= 1.")

    if np.isclose(rho, 0, atol=1e-10):
        return cobb_douglas(K, L, alpha)

    if rho < 0:
        # A zero input yields zero output for negative rho.
        K, L = np.broadcast_arrays(K, L)
        result = np.zeros_like(K, dtype=float)
        positive = (K > 0) & (L > 0)

        result[positive] = (
            alpha * K[positive] ** rho
            + (1 - alpha) * L[positive] ** rho
        ) ** (1 / rho)

        return result

    return (
        alpha * K**rho + (1 - alpha) * L**rho
    ) ** (1 / rho)

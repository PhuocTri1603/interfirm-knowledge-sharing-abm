import numpy as np
import pytest

from interfirm_abm.production import (
    cobb_douglas,
    leontief,
    linear,
    ces,
)


PRODUCTION_FUNCTIONS = [
    cobb_douglas,
    leontief,
    linear,
    ces,
]


@pytest.mark.parametrize("production", PRODUCTION_FUNCTIONS)
@pytest.mark.parametrize("scale", [0.5, 2.0, 10.0])
def test_constant_returns_to_scale(production, scale):
    K, L = 70.0, 30.0

    original = production(K, L)
    scaled = production(scale * K, scale * L)

    assert np.isclose(scaled, scale * original)


@pytest.mark.parametrize("production", PRODUCTION_FUNCTIONS)
def test_nonnegative_output(production):
    K = np.array([0.0, 10.0, 70.0])
    L = np.array([10.0, 0.0, 30.0])

    output = production(K, L)

    assert np.all(output >= 0)


def test_ces_cobb_douglas_limit():
    K, L = 70.0, 30.0

    expected = cobb_douglas(K, L)
    actual = ces(K, L, rho=1e-8)

    assert np.isclose(actual, expected, rtol=1e-6)


def test_ces_linear_limit():
    K, L = 70.0, 30.0

    assert np.isclose(
        ces(K, L, rho=1.0),
        linear(K, L)
    )


@pytest.mark.parametrize("production", PRODUCTION_FUNCTIONS)
def test_negative_inputs_rejected(production):
    with pytest.raises(ValueError):
        production(-10, 30)


def test_invalid_ces_parameter():
    with pytest.raises(ValueError):
        ces(70, 30, rho=1.5)


def test_invalid_alpha():
    with pytest.raises(ValueError):
        cobb_douglas(70, 30, alpha=1.5)


def test_invalid_kappa():
    with pytest.raises(ValueError):
        leontief(70, 30, kappa=0)


def test_zero_inputs():
    assert np.isclose(ces(0, 0), 0)
    assert np.isclose(cobb_douglas(0, 0), 0)
    assert np.isclose(leontief(0, 0), 0)
    assert np.isclose(linear(0, 0), 0)

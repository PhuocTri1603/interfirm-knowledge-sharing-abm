import numpy as np
import pytest

from interfirm_abm.firm import Firm
from interfirm_abm.production_optimum import (
    optimal_capital_share,
    optimal_output,
    remaining_improvement_potential,
)


@pytest.mark.parametrize(
    "technology",
    ["Cobb-Douglas", "Leontief", "Linear", "CES"],
)
def test_optimum_dominates_feasible_grid(technology):
    firm = Firm(firm_id=1, technology=technology)
    optimum = optimal_output(technology)

    grid = np.linspace(0.05, 0.95, 901)
    grid_outputs = [firm.produce(float(s)) for s in grid]

    assert optimum >= max(grid_outputs) - 1e-8
    assert 0.05 <= optimal_capital_share(technology) <= 0.95


def test_known_optimal_shares():
    assert np.isclose(optimal_capital_share("Cobb-Douglas"), 0.70)
    assert np.isclose(optimal_capital_share("Leontief"), 0.70)
    assert np.isclose(optimal_capital_share("Linear"), 0.95)
    assert np.isclose(
        optimal_capital_share("CES"),
        0.6376,
        atol=0.001,
    )


@pytest.mark.parametrize(
    "technology",
    ["Cobb-Douglas", "Leontief", "Linear", "CES"],
)
def test_remaining_potential_at_optimum_is_zero(technology):
    optimum = optimal_output(technology)

    remaining = remaining_improvement_potential(
        technology,
        optimum,
    )

    assert np.isclose(remaining, 0.0)


def test_remaining_potential_is_positive_initially():
    for technology in ["Cobb-Douglas", "Leontief", "Linear", "CES"]:
        firm = Firm(firm_id=1, technology=technology)

        remaining = remaining_improvement_potential(
            technology,
            firm.current_output,
        )

        assert remaining > 0


def test_invalid_output_above_optimum():
    with pytest.raises(ValueError):
        remaining_improvement_potential(
            "Linear",
            optimal_output("Linear") + 1.0,
        )

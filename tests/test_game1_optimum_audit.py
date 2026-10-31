"""Audit constrained production optima used in Game 1 efficiency metrics."""

import numpy as np
import pytest

from interfirm_abm.firm import PRODUCTION_FUNCTIONS
from interfirm_abm.production_optimum import (
    optimal_capital_share,
    optimal_output,
)


@pytest.mark.parametrize(
    "technology",
    ["Cobb-Douglas", "Leontief", "Linear", "CES"],
)
def test_analytic_optimum_matches_dense_feasible_grid(technology):
    budget = 100.0
    shares = np.linspace(0.05, 0.95, 9001)
    fn = PRODUCTION_FUNCTIONS[technology]
    outputs = np.asarray(fn(budget * shares, budget * (1 - shares)))
    best_grid_output = float(outputs.max())
    best_analytic_output = optimal_output(technology, budget)
    share = optimal_capital_share(technology)

    assert 0.05 <= share <= 0.95
    assert best_analytic_output >= best_grid_output - 1e-6
    assert best_analytic_output <= best_grid_output + 0.005


def test_linear_constrained_optimum_is_upper_search_bound():
    assert optimal_capital_share("Linear") == pytest.approx(0.95)

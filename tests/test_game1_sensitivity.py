"""Small deterministic smoke tests for sensitivity parameterization."""

import pytest

from interfirm_abm.simulation import Simulation
from experiments.game1_sensitivity import SCENARIOS, run_experiment


@pytest.mark.parametrize("probability,radius", [
    (-0.01, 0.1), (1.01, 0.1), (0.2, 0), (0.2, -0.1),
])
def test_invalid_guided_parameters_rejected(probability, radius):
    with pytest.raises(ValueError):
        Simulation(
            exploration_probability=probability,
            search_radius=radius,
        )


def test_default_guided_parameters_match_explicit_baseline():
    implicit = Simulation(n_firms=4, n_rounds=10, seed=2026,
                          learning_policy="guided", matched_randomness=True).run()
    explicit = Simulation(n_firms=4, n_rounds=10, seed=2026,
                          learning_policy="guided", matched_randomness=True,
                          exploration_probability=0.2, search_radius=0.1).run()
    assert implicit.equals(explicit)


def test_sensitivity_design_has_unique_scenarios_and_baseline():
    assert len(SCENARIOS) == len({name for name, _, _ in SCENARIOS}) == 9
    assert ("baseline", 0.2, 0.1) in SCENARIOS

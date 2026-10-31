from interfirm_abm.simulation import Simulation
from interfirm_abm.production_optimum import optimal_output


def test_heterogeneous_population_is_used():
    sim = Simulation(n_firms=100, n_rounds=2, heterogeneous_population=True, matched_randomness=True)
    assert len(sim.firms) == 100
    assert all(f.alpha == sim.population.iloc[i]['alpha'] for i, f in enumerate(sim.firms))
    assert len(sim.run()) == 200
    assert all(f.current_output <= optimal_output(f.technology, f.budget, f.alpha, f.rho, f.productivity) + 1e-8 for f in sim.firms)


def test_original_default_is_preserved():
    sim = Simulation(n_firms=4, n_rounds=1)
    assert all(f.alpha == 0.7 for f in sim.firms)

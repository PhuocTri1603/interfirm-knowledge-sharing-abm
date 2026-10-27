import numpy as np
import pandas as pd
import pytest

from interfirm_abm.simulation import Simulation
from interfirm_abm.cooperative_simulation import CooperativeSimulation


def test_one_experiment_per_firm_round():
    sim = CooperativeSimulation(n_firms=20, n_rounds=5, seed=2026)
    history = sim.run()

    assert len(history) == 100
    assert len(sim.learning_log) == 100
    assert history.groupby(["round", "firm_id"]).size().eq(1).all()


def test_first_round_matches_independent_baseline():
    baseline = Simulation(
        n_firms=20,
        n_rounds=5,
        seed=2026,
        learning_policy="guided_initial",
        matched_randomness=True,
    )
    cooperative = CooperativeSimulation(
        n_firms=20,
        n_rounds=5,
        seed=2026,
    )

    h1 = baseline.run()
    h3 = cooperative.run()

    pd.testing.assert_frame_equal(
        h1[h1["round"] == 1].reset_index(drop=True),
        h3[h3["round"] == 1].reset_index(drop=True),
    )


def test_no_sharing_during_first_round():
    sim = CooperativeSimulation(n_firms=20, n_rounds=5, seed=2026)
    sim.run()

    first = [
        record
        for record in sim.learning_log
        if record["round"] == 1
    ]

    assert all(record["learning_source"] == "random" for record in first)


def test_shared_knowledge_comes_from_previous_rounds():
    sim = CooperativeSimulation(n_firms=20, n_rounds=5, seed=2026)
    sim.run()

    for record in sim.learning_log:
        if record["learning_source"] != "shared":
            continue

        prior = [
            item
            for firm in sim.firms
            for item in firm.history
            if item["firm_id"] == record["selected_peer_id"]
            and item["round"] < record["round"]
            and item["accepted"] is True
            and item["technology"] == record["technology"]
        ]

        assert len(prior) > 0


def test_shared_knowledge_never_comes_from_self():
    sim = CooperativeSimulation(n_firms=20, n_rounds=5, seed=2026)
    sim.run()

    for record in sim.learning_log:
        if record["learning_source"] == "shared":
            assert record["selected_peer_id"] != record["firm_id"]


def test_reproducible_with_same_seed():
    sim1 = CooperativeSimulation(n_firms=20, n_rounds=5, seed=2026)
    sim2 = CooperativeSimulation(n_firms=20, n_rounds=5, seed=2026)

    pd.testing.assert_frame_equal(sim1.run(), sim2.run())

    assert sim1.learning_log == sim2.learning_log


def test_different_seed_changes_experiment_paths():
    sim1 = CooperativeSimulation(n_firms=20, n_rounds=5, seed=2026)
    sim2 = CooperativeSimulation(n_firms=20, n_rounds=5, seed=2027)

    h1 = sim1.run()
    h2 = sim2.run()

    assert not np.allclose(
        h1["candidate_share"],
        h2["candidate_share"],
    )


def test_allocation_and_output_consistency():
    sim = CooperativeSimulation(n_firms=20, n_rounds=5, seed=2026)
    history = sim.run()

    assert history["candidate_share"].between(0.05, 0.95).all()

    for firm in sim.firms:
        rows = history[history["firm_id"] == firm.firm_id]

        for _, row in rows.iterrows():
            expected = firm.produce(row["capital_share"])
            assert np.isclose(row["current_output"], expected)


def test_sharing_requires_same_technology():
    sim = CooperativeSimulation(n_firms=20, n_rounds=5, seed=2026)
    sim.run()

    technologies = {
        firm.firm_id: firm.technology
        for firm in sim.firms
    }

    for record in sim.learning_log:
        if record["learning_source"] == "shared":
            assert (
                technologies[record["selected_peer_id"]]
                == record["technology"]
            )


def test_no_same_technology_peer_falls_back():
    sim = CooperativeSimulation(n_firms=4, n_rounds=10, seed=2026)
    sim.run()

    assert all(
        record["learning_source"] != "shared"
        for record in sim.learning_log
    )


def test_cannot_run_twice():
    sim = CooperativeSimulation(n_firms=20, n_rounds=5, seed=2026)
    sim.run()

    with pytest.raises(RuntimeError):
        sim.run()

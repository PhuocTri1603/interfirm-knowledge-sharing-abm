import pandas as pd

from interfirm_abm.cooperative_simulation import CooperativeSimulation
from interfirm_abm.cross_technology_simulation import (
    CrossTechnologySimulation,
)


def test_same_technology_matches_game3a():
    for seed in [2026, 2027, 2028, 2029, 2030]:
        original = CooperativeSimulation(
            seed=seed,
            sharing_probability=0.30,
        )
        extended = CrossTechnologySimulation(
            seed=seed,
            sharing_probability=0.30,
            transfer_policy="same_technology",
        )

        pd.testing.assert_frame_equal(
            original.run(),
            extended.run(),
        )
        assert original.learning_log == extended.learning_log


def test_cross_technology_selects_only_different_sources():
    sim = CrossTechnologySimulation(
        seed=2026,
        sharing_probability=0.60,
        transfer_policy="cross_technology",
    )
    sim.run()

    technologies = {
        firm.firm_id: firm.technology
        for firm in sim.firms
    }

    shared_count = 0

    for record in sim.learning_log:
        if record["learning_source"] != "shared":
            continue

        shared_count += 1
        recipient_technology = record["technology"]
        source_technology = technologies[record["selected_peer_id"]]

        assert source_technology != recipient_technology

    assert shared_count > 0


def test_mixed_policy_selects_both_source_types():
    sim = CrossTechnologySimulation(
        seed=2026,
        sharing_probability=0.60,
        transfer_policy="mixed",
    )
    sim.run()

    technologies = {
        firm.firm_id: firm.technology
        for firm in sim.firms
    }

    selected_types = set()

    for record in sim.learning_log:
        if record["learning_source"] != "shared":
            continue

        source_technology = technologies[record["selected_peer_id"]]

        if source_technology == record["technology"]:
            selected_types.add("same")
        else:
            selected_types.add("cross")

    assert selected_types == {"same", "cross"}


def test_one_experiment_per_firm_per_round():
    sim = CrossTechnologySimulation(
        seed=2026,
        sharing_probability=0.30,
        transfer_policy="cross_technology",
    )

    history = sim.run()

    assert len(history) == sim.n_firms * sim.n_rounds
    assert not history.duplicated(["firm_id", "round"]).any()


def test_shared_knowledge_uses_only_past_rounds():
    sim = CrossTechnologySimulation(
        seed=2026,
        sharing_probability=0.60,
        transfer_policy="cross_technology",
    )
    sim.run()

    assert len(sim.knowledge_timeline._rounds) == sim.n_rounds

    for round_number, records in sim.knowledge_timeline._rounds.items():
        assert len(records) == sim.n_firms
        assert all(
            record["round"] == round_number
            for record in records
        )

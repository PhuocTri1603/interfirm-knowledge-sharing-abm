import numpy as np
import pytest

from interfirm_abm.cross_technology_learning import (
    select_transfer_experiment,
)


@pytest.fixture
def shared_history():
    return [
        {
            "firm_id": 2,
            "technology": "Leontief",
            "candidate_share": 0.70,
            "accepted": True,
        },
        {
            "firm_id": 3,
            "technology": "Linear",
            "candidate_share": 0.90,
            "accepted": True,
        },
        {
            "firm_id": 4,
            "technology": "CES",
            "candidate_share": 0.60,
            "accepted": False,
        },
        {
            "firm_id": 5,
            "technology": "Cobb-Douglas",
            "candidate_share": 0.65,
            "accepted": True,
        },
    ]


def test_same_technology_policy(shared_history):
    rng = np.random.default_rng(2026)
    for _ in range(100):
        selected = select_transfer_experiment(
            shared_history,
            recipient_technology="Cobb-Douglas",
            rng=rng,
            transfer_policy="same_technology",
        )
        assert selected["technology"] == "Cobb-Douglas"
        assert selected["accepted"] is True


def test_cross_technology_policy(shared_history):
    rng = np.random.default_rng(2026)
    for _ in range(100):
        selected = select_transfer_experiment(
            shared_history,
            recipient_technology="Cobb-Douglas",
            rng=rng,
            transfer_policy="cross_technology",
        )
        assert selected["technology"] != "Cobb-Douglas"
        assert selected["accepted"] is True


def test_mixed_policy(shared_history):
    rng = np.random.default_rng(2026)
    technologies = set()

    for _ in range(100):
        selected = select_transfer_experiment(
            shared_history,
            recipient_technology="Cobb-Douglas",
            rng=rng,
            transfer_policy="mixed",
        )
        assert selected["accepted"] is True
        technologies.add(selected["technology"])

    assert "Cobb-Douglas" in technologies
    assert any(t != "Cobb-Douglas" for t in technologies)


def test_no_eligible_knowledge(shared_history):
    rng = np.random.default_rng(2026)
    selected = select_transfer_experiment(
        shared_history,
        recipient_technology="CES",
        rng=rng,
        transfer_policy="same_technology",
    )
    assert selected is None


def test_invalid_policy(shared_history):
    rng = np.random.default_rng(2026)
    with pytest.raises(ValueError):
        select_transfer_experiment(
            shared_history,
            recipient_technology="CES",
            rng=rng,
            transfer_policy="unknown",
        )

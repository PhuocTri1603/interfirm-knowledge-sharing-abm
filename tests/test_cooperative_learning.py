import numpy as np
import pytest

from interfirm_abm.cooperative_learning import (
    select_shared_experiment,
    shared_knowledge_exploration,
)


@pytest.fixture
def shared_history():
    return [
        {
            "firm_id": 2,
            "technology": "Leontief",
            "candidate_share": 0.40,
            "accepted": False,
        },
        {
            "firm_id": 6,
            "technology": "Leontief",
            "candidate_share": 0.65,
            "accepted": True,
        },
        {
            "firm_id": 10,
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
    ]


def test_selects_successful_experiment(shared_history):
    rng = np.random.default_rng(2026)

    for _ in range(100):
        selected = select_shared_experiment(
            shared_history, "Leontief", rng
        )
        assert selected["accepted"] is True


def test_filters_by_technology(shared_history):
    rng = np.random.default_rng(2026)

    for _ in range(100):
        selected = select_shared_experiment(
            shared_history, "Leontief", rng
        )
        assert selected["technology"] == "Leontief"
        assert selected["firm_id"] in (6, 10)


def test_returns_none_without_eligible_knowledge(shared_history):
    rng = np.random.default_rng(2026)

    assert select_shared_experiment(
        shared_history, "Cobb-Douglas", rng
    ) is None

    assert shared_knowledge_exploration(
        shared_history, "Cobb-Douglas", rng
    ) is None


def test_does_not_mutate_shared_history(shared_history):
    rng = np.random.default_rng(2026)

    selected = select_shared_experiment(
        shared_history, "Leontief", rng
    )

    selected["candidate_share"] = 0.99

    assert shared_history[1]["candidate_share"] == 0.65
    assert shared_history[2]["candidate_share"] == 0.70


def test_selection_reproducible_with_same_seed(shared_history):
    rng1 = np.random.default_rng(2026)
    rng2 = np.random.default_rng(2026)

    sequence1 = [
        select_shared_experiment(
            shared_history, "Leontief", rng1
        )["firm_id"]
        for _ in range(100)
    ]

    sequence2 = [
        select_shared_experiment(
            shared_history, "Leontief", rng2
        )["firm_id"]
        for _ in range(100)
    ]

    assert sequence1 == sequence2


def test_selection_is_approximately_uniform(shared_history):
    rng = np.random.default_rng(2026)

    selected_ids = [
        select_shared_experiment(
            shared_history, "Leontief", rng
        )["firm_id"]
        for _ in range(10000)
    ]

    share_firm_6 = selected_ids.count(6) / len(selected_ids)

    assert 0.48 <= share_firm_6 <= 0.52


def test_exploration_within_bounds(shared_history):
    rng = np.random.default_rng(2026)

    for _ in range(1000):
        candidate = shared_knowledge_exploration(
            shared_history, "Leontief", rng
        )

        assert 0.05 <= candidate <= 0.95


@pytest.mark.parametrize(
    "radius",
    [0, -0.1, np.nan, np.inf],
)
def test_rejects_invalid_search_radius(shared_history, radius):
    rng = np.random.default_rng(2026)

    with pytest.raises(ValueError):
        shared_knowledge_exploration(
            shared_history,
            "Leontief",
            rng,
            search_radius=radius,
        )

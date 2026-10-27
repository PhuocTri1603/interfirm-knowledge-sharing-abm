from types import SimpleNamespace

from interfirm_abm.shared_knowledge import SharedKnowledgeTimeline


def make_firm(firm_id, technology, rounds):
    history = [
        {
            "firm_id": firm_id,
            "technology": technology,
            "round": round_number,
            "candidate_share": 0.5 + 0.01 * round_number,
            "accepted": True,
        }
        for round_number in rounds
    ]
    return SimpleNamespace(history=history)


def test_cross_technology_information_delay():
    timeline = SharedKnowledgeTimeline()

    firms = [
        make_firm(1, "Linear", [1, 2]),
        make_firm(2, "CES", [1, 2]),
    ]

    assert timeline.observe(observer_id=1, round_number=1) == []

    timeline.record_round(firms, round_number=1)

    visible_round_2 = timeline.observe(
        observer_id=1,
        round_number=2,
    )

    assert len(visible_round_2) == 1
    assert visible_round_2[0]["firm_id"] == 2
    assert visible_round_2[0]["round"] == 1

    timeline.record_round(firms, round_number=2)

    visible_round_3 = timeline.observe(
        observer_id=1,
        round_number=3,
    )

    assert len(visible_round_3) == 2
    assert {r["round"] for r in visible_round_3} == {1, 2}
    assert all(r["firm_id"] == 2 for r in visible_round_3)


def test_observed_knowledge_cannot_mutate_timeline():
    timeline = SharedKnowledgeTimeline()

    firms = [
        make_firm(1, "Linear", [1]),
        make_firm(2, "CES", [1]),
    ]

    timeline.record_round(firms, round_number=1)

    observed = timeline.observe(
        observer_id=1,
        round_number=2,
    )

    observed[0]["candidate_share"] = 0.99

    observed_again = timeline.observe(
        observer_id=1,
        round_number=2,
    )

    assert observed_again[0]["candidate_share"] == 0.51

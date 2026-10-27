import pytest

from interfirm_abm.firm import Firm
from interfirm_abm.shared_knowledge import SharedKnowledgeTimeline


@pytest.fixture
def firms():
    return [
        Firm(firm_id=1, technology="Cobb-Douglas"),
        Firm(firm_id=2, technology="Leontief"),
    ]


def complete_round(firms, timeline, round_number):
    firms[0].experiment(0.60, round_number)
    firms[1].experiment(0.40, round_number)
    timeline.record_round(firms, round_number)


def test_no_knowledge_before_first_round():
    timeline = SharedKnowledgeTimeline()

    assert timeline.observe(1, 1) == []


def test_shares_completed_experiments_only(firms):
    timeline = SharedKnowledgeTimeline()

    complete_round(firms, timeline, 1)

    assert len(timeline.observe(1, 2)) == 1
    assert timeline.observe(1, 2)[0]["round"] == 1


    with pytest.raises(ValueError):
        timeline.observe(1, 3)


def test_excludes_own_history(firms):
    timeline = SharedKnowledgeTimeline()

    complete_round(firms, timeline, 1)

    observed = timeline.observe(1, 2)

    assert all(r["firm_id"] != 1 for r in observed)


def test_preserves_failed_experiments(firms):
    timeline = SharedKnowledgeTimeline()

    complete_round(firms, timeline, 1)

    observed = timeline.observe(1, 2)

    assert observed[0]["accepted"] is False
    assert observed[0]["candidate_share"] == 0.40


def test_copy_isolation(firms):
    timeline = SharedKnowledgeTimeline()

    complete_round(firms, timeline, 1)

    observed = timeline.observe(1, 2)
    observed[0]["candidate_share"] = 0.99

    assert timeline.observe(1, 2)[0]["candidate_share"] == 0.40

    firms[1].history[0]["candidate_share"] = 0.10

    assert timeline.observe(1, 2)[0]["candidate_share"] == 0.40


def test_rejects_duplicate_round(firms):
    timeline = SharedKnowledgeTimeline()

    complete_round(firms, timeline, 1)

    with pytest.raises(ValueError):
        timeline.record_round(firms, 1)


def test_rejects_skipped_round(firms):
    timeline = SharedKnowledgeTimeline()

    with pytest.raises(ValueError):
        timeline.record_round(firms, 2)


def test_rejects_incomplete_experiments(firms):
    timeline = SharedKnowledgeTimeline()

    firms[0].experiment(0.60, 1)

    with pytest.raises(ValueError):
        timeline.record_round(firms, 1)


def test_multi_round_knowledge_accumulates(firms):
    timeline = SharedKnowledgeTimeline()

    complete_round(firms, timeline, 1)
    complete_round(firms, timeline, 2)

    observed = timeline.observe(1, 3)

    assert len(observed) == 2
    assert [r["round"] for r in observed] == [1, 2]

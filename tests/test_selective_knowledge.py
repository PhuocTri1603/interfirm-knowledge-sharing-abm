"""Tests for the Game 3C selective knowledge pool."""

from interfirm_abm.selective_knowledge import SelectiveKnowledgePool


def make_experiment(firm_id, round_number, accepted=True):
    return {
        "firm_id": firm_id,
        "round": round_number,
        "accepted": accepted,
        "candidate_share": 0.6,
        "candidate_output": 120.0,
    }


def test_shared_successful_experiment_is_published():
    pool = SelectiveKnowledgePool()
    pool.publish(make_experiment(1, 1), shared=True)

    assert len(pool.observe(observer_id=2, round_number=2)) == 1


def test_withheld_experiment_is_not_published():
    pool = SelectiveKnowledgePool()
    pool.publish(make_experiment(1, 1), shared=False)

    assert pool.observe(observer_id=2, round_number=2) == []


def test_failed_experiment_is_not_published():
    pool = SelectiveKnowledgePool()
    pool.publish(make_experiment(1, 1, accepted=False), shared=True)

    assert pool.observe(observer_id=2, round_number=2) == []


def test_shared_knowledge_has_one_round_lag():
    pool = SelectiveKnowledgePool()
    pool.publish(make_experiment(1, 3), shared=True)

    assert pool.observe(observer_id=2, round_number=3) == []
    assert len(pool.observe(observer_id=2, round_number=4)) == 1


def test_firm_cannot_observe_own_knowledge():
    pool = SelectiveKnowledgePool()
    pool.publish(make_experiment(1, 1), shared=True)

    assert pool.observe(observer_id=1, round_number=2) == []


def test_published_knowledge_persists():
    pool = SelectiveKnowledgePool()
    pool.publish(make_experiment(1, 1), shared=True)

    assert len(pool.observe(observer_id=2, round_number=2)) == 1
    assert len(pool.observe(observer_id=2, round_number=10)) == 1

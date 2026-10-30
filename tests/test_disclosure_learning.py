import pytest

from interfirm_abm.disclosure_learning import (
    DisclosureLearner,
    ContributionHistory,
)


def test_neutral_initial_q_values():
    learner = DisclosureLearner()

    assert learner.q_share == pytest.approx(0.0)
    assert learner.q_withhold == pytest.approx(0.0)


def test_neutral_softmax_probability():
    learner = DisclosureLearner(temperature=0.01)

    assert learner.share_probability() == pytest.approx(0.5)


def test_contribution_history_starts_neutral():
    history = ContributionHistory(window=5)

    assert history.reputation(round_number=1) == pytest.approx(0.5)


def test_only_eligible_decisions_count():
    history = ContributionHistory(window=5)

    history.record(round_number=1, shared=True)
    history.record(round_number=2, shared=False)

    # Round 3 has no successful experiment, so no record.
    assert history.reputation(round_number=4) == pytest.approx(0.5)


def test_contribution_history_uses_rolling_window():
    history = ContributionHistory(window=5)

    history.record(round_number=1, shared=True)
    history.record(round_number=2, shared=True)
    history.record(round_number=6, shared=False)

    # At round 7, only rounds 2 through 6 remain.
    # One Share, one Withhold, with neutral smoothing.
    assert history.reputation(round_number=7) == pytest.approx(0.5)


def test_delayed_reward_discount_and_normalization():
    learner = DisclosureLearner()

    learner.record_decision(
        round_number=1,
        shared=True,
        baseline_output=100.0,
        disclosure_cost_rate=0.01,
    )

    learner.observe_shared_gain(round_number=2, gain=2.0)
    learner.observe_shared_gain(round_number=3, gain=3.0)

    rewards = learner.finalize_rewards(round_number=6)

    expected = (2.0 + 0.95 * 3.0) / 100.0 - 0.01

    assert len(rewards) == 1
    assert rewards[0]["reward"] == pytest.approx(expected)


def test_reward_not_finalized_before_full_window():
    learner = DisclosureLearner()

    learner.record_decision(
        round_number=1,
        shared=False,
        baseline_output=100.0,
        disclosure_cost_rate=0.01,
    )

    assert learner.finalize_rewards(round_number=5) == []
    assert learner.q_withhold == pytest.approx(0.0)


def test_q_update_only_for_chosen_action():
    learner = DisclosureLearner(learning_rate=0.30)

    learner.record_decision(
        round_number=1,
        shared=True,
        baseline_output=100.0,
        disclosure_cost_rate=0.01,
    )

    learner.observe_shared_gain(round_number=2, gain=10.0)
    learner.finalize_rewards(round_number=6)

    # Reward = 10/100 - 0.01 = 0.09
    # Q_share = 0 + 0.30 * 0.09 = 0.027
    assert learner.q_share == pytest.approx(0.027)
    assert learner.q_withhold == pytest.approx(0.0)


def test_overlapping_reward_windows():
    learner = DisclosureLearner()

    learner.record_decision(
        round_number=1,
        shared=True,
        baseline_output=100.0,
        disclosure_cost_rate=0.0,
    )
    learner.record_decision(
        round_number=2,
        shared=False,
        baseline_output=100.0,
        disclosure_cost_rate=0.0,
    )

    learner.observe_shared_gain(round_number=3, gain=10.0)

    first = learner.finalize_rewards(round_number=6)
    second = learner.finalize_rewards(round_number=7)

    assert first[0]["reward"] == pytest.approx(0.95 * 10.0 / 100.0)
    assert second[0]["reward"] == pytest.approx(10.0 / 100.0)


def test_finalized_decision_is_not_updated_twice():
    learner = DisclosureLearner(learning_rate=0.30)

    learner.record_decision(
        round_number=1,
        shared=True,
        baseline_output=100.0,
        disclosure_cost_rate=0.01,
    )

    learner.observe_shared_gain(round_number=2, gain=10.0)

    first = learner.finalize_rewards(round_number=6)
    q_after_first = learner.q_share

    second = learner.finalize_rewards(round_number=7)

    assert len(first) == 1
    assert second == []
    assert learner.q_share == pytest.approx(q_after_first)


def test_withhold_has_no_disclosure_cost():
    learner = DisclosureLearner()

    learner.record_decision(
        round_number=1,
        shared=False,
        baseline_output=100.0,
        disclosure_cost_rate=0.02,
    )

    rewards = learner.finalize_rewards(round_number=6)

    assert rewards[0]["reward"] == pytest.approx(0.0)
    assert learner.q_withhold == pytest.approx(0.0)


def test_future_gain_not_counted_in_earlier_window():
    learner = DisclosureLearner()

    learner.record_decision(
        round_number=1,
        shared=True,
        baseline_output=100.0,
        disclosure_cost_rate=0.01,
    )

    learner.observe_shared_gain(round_number=7, gain=20.0)

    rewards = learner.finalize_rewards(round_number=7)

    assert rewards[0]["reward"] == pytest.approx(-0.01)


def test_neutral_access_probability():
    history = ContributionHistory(window=5)

    assert history.access_probability(round_number=1) == pytest.approx(0.50)


def test_contribution_changes_access_probability():
    sharing_firm = ContributionHistory(window=5)
    withholding_firm = ContributionHistory(window=5)

    sharing_firm.record(round_number=1, shared=True)
    withholding_firm.record(round_number=1, shared=False)

    assert sharing_firm.access_probability(round_number=2) == pytest.approx(
        0.10 + 0.80 * (2.0 / 3.0)
    )

    assert withholding_firm.access_probability(round_number=2) == pytest.approx(
        0.10 + 0.80 * (1.0 / 3.0)
    )


def test_access_probability_stays_in_valid_range():
    history = ContributionHistory(window=5)

    for round_number in range(1, 6):
        history.record(round_number=round_number, shared=True)

    probability = history.access_probability(round_number=6)

    assert 0.0 <= probability <= 1.0
    assert probability == pytest.approx(
        0.10 + 0.80 * (6.0 / 7.0)
    )



def test_access_granted_when_draw_below_probability():
    history = ContributionHistory(window=5)
    assert history.check_access(round_number=1, draw=0.30) is True


def test_access_denied_when_draw_above_probability():
    history = ContributionHistory(window=5)
    assert history.check_access(round_number=1, draw=0.70) is False


def test_access_denied_at_exact_probability():
    history = ContributionHistory(window=5)
    assert history.check_access(round_number=1, draw=0.50) is False


def test_access_rejects_invalid_random_draw():
    history = ContributionHistory(window=5)

    with pytest.raises(ValueError):
        history.check_access(round_number=1, draw=-0.1)

    with pytest.raises(ValueError):
        history.check_access(round_number=1, draw=1.0)

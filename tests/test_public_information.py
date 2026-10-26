"""Tests for the public information layer."""

from interfirm_abm.firm import Firm
from interfirm_abm.public_information import (
    create_public_snapshot,
    observe_competitors,
)


def test_snapshot_contains_only_public_fields():
    firms = [
        Firm(firm_id=1, technology="Cobb-Douglas"),
        Firm(firm_id=2, technology="Leontief"),
    ]

    snapshot = create_public_snapshot(firms, round_number=0)

    assert len(snapshot) == 2
    assert set(snapshot[0]) == {
        "round", "firm_id", "technology", "output"
    }


def test_private_information_is_not_exposed():
    firm = Firm(firm_id=1, technology="Cobb-Douglas")
    firm.experiment(0.70, round_number=1)

    snapshot = create_public_snapshot([firm], round_number=1)

    assert "history" not in snapshot[0]
    assert "capital_share" not in snapshot[0]
    assert "candidate_share" not in snapshot[0]
    assert "candidate_output" not in snapshot[0]


def test_observer_cannot_observe_itself():
    firms = [
        Firm(firm_id=1, technology="Cobb-Douglas"),
        Firm(firm_id=2, technology="Leontief"),
        Firm(firm_id=3, technology="Linear"),
    ]

    snapshot = create_public_snapshot(firms, round_number=0)
    observed = observe_competitors(snapshot, observer_id=2)

    assert {row["firm_id"] for row in observed} == {1, 3}


def test_snapshot_is_not_live_reference():
    firm = Firm(firm_id=1, technology="Cobb-Douglas")

    snapshot = create_public_snapshot([firm], round_number=0)
    original_output = snapshot[0]["output"]

    firm.experiment(0.70, round_number=1)

    assert snapshot[0]["output"] == original_output


def test_observation_does_not_modify_snapshot():
    firms = [
        Firm(firm_id=1, technology="Cobb-Douglas"),
        Firm(firm_id=2, technology="Leontief"),
    ]

    snapshot = create_public_snapshot(firms, round_number=0)
    observed = observe_competitors(snapshot, observer_id=1)

    observed[0]["output"] = -999

    assert snapshot[1]["output"] != -999


from interfirm_abm.public_information import (
    PublicInformationTimeline,
)


def test_timeline_starts_with_round_zero():
    firm = Firm(firm_id=1, technology="Cobb-Douglas")
    timeline = PublicInformationTimeline([firm])

    snapshot = timeline.get_snapshot(0)

    assert len(snapshot) == 1
    assert snapshot[0]["round"] == 0


def test_timeline_observes_previous_round():
    firms = [
        Firm(firm_id=1, technology="Cobb-Douglas"),
        Firm(firm_id=2, technology="Linear"),
    ]

    timeline = PublicInformationTimeline(firms)

    initial_output = firms[1].current_output

    firms[1].experiment(0.90, round_number=1)

    observed_round_one = timeline.observe(
        observer_id=1,
        round_number=1,
    )

    assert observed_round_one[0]["output"] == initial_output

    timeline.record_round(firms, round_number=1)

    observed_round_two = timeline.observe(
        observer_id=1,
        round_number=2,
    )

    assert (
        observed_round_two[0]["output"]
        == firms[1].current_output
    )


def test_timeline_rejects_missing_round():
    firm = Firm(firm_id=1, technology="Cobb-Douglas")
    timeline = PublicInformationTimeline([firm])

    try:
        timeline.observe(observer_id=2, round_number=3)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_timeline_rejects_duplicate_snapshot():
    firm = Firm(firm_id=1, technology="Cobb-Douglas")
    timeline = PublicInformationTimeline([firm])

    timeline.record_round([firm], round_number=1)

    try:
        timeline.record_round([firm], round_number=1)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_timeline_snapshot_is_copy():
    firm = Firm(firm_id=1, technology="Cobb-Douglas")
    timeline = PublicInformationTimeline([firm])

    snapshot = timeline.get_snapshot(0)
    snapshot[0]["output"] = -100

    assert timeline.get_snapshot(0)[0]["output"] != -100

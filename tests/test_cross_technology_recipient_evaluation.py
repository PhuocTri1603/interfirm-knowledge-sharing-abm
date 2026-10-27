import numpy as np

from interfirm_abm.firm import Firm
from interfirm_abm.cross_technology_learning import (
    select_transfer_experiment,
)


def test_successful_source_experiment_can_fail_for_recipient():
    source = Firm(firm_id=1, technology="Linear")
    recipient = Firm(
        firm_id=2,
        technology="CES",
        capital_share=0.6376,
    )

    source_record = source.experiment(
        candidate_share=0.90,
        round_number=1,
    )

    assert source_record["accepted"] is True

    shared = select_transfer_experiment(
        shared_history=[source_record],
        recipient_technology=recipient.technology,
        rng=np.random.default_rng(2026),
        transfer_policy="cross_technology",
    )

    assert shared is not None
    assert shared["technology"] == "Linear"

    previous_output = recipient.current_output

    result = recipient.experiment(
        candidate_share=shared["candidate_share"],
        round_number=2,
    )

    assert result["accepted"] is False
    assert np.isclose(
        result["candidate_output"],
        recipient.produce(0.90),
    )
    assert np.isclose(recipient.current_output, previous_output)
    assert len(recipient.history) == 1


def test_cross_technology_knowledge_can_benefit_recipient():
    source = Firm(firm_id=1, technology="Linear")
    recipient = Firm(firm_id=2, technology="Cobb-Douglas")

    source_record = source.experiment(
        candidate_share=0.70,
        round_number=1,
    )

    assert source_record["accepted"] is True

    shared = select_transfer_experiment(
        shared_history=[source_record],
        recipient_technology=recipient.technology,
        rng=np.random.default_rng(2026),
        transfer_policy="cross_technology",
    )

    previous_output = recipient.current_output

    result = recipient.experiment(
        candidate_share=shared["candidate_share"],
        round_number=2,
    )

    assert result["accepted"] is True
    assert result["candidate_output"] > previous_output
    assert np.isclose(
        result["candidate_output"],
        recipient.produce(0.70),
    )
    assert len(recipient.history) == 1
    assert recipient.history[0]["round"] == 2


def test_source_output_is_not_copied_to_recipient():
    source = Firm(firm_id=1, technology="Leontief")
    recipient = Firm(firm_id=2, technology="Cobb-Douglas")

    source_record = source.experiment(
        candidate_share=0.70,
        round_number=1,
    )

    assert source_record["accepted"] is True

    shared = select_transfer_experiment(
        shared_history=[source_record],
        recipient_technology=recipient.technology,
        rng=np.random.default_rng(2026),
        transfer_policy="cross_technology",
    )

    result = recipient.experiment(
        candidate_share=shared["candidate_share"],
        round_number=2,
    )

    assert np.isclose(
        result["candidate_output"],
        recipient.produce(0.70),
    )

    assert not np.isclose(
        result["candidate_output"],
        source_record["candidate_output"],
    )

    assert len(recipient.history) == 1

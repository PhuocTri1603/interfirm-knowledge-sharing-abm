"""Tests for the minimal firm agent."""

import numpy as np
import pytest

from interfirm_abm.firm import Firm


def test_initial_state():
    firm = Firm(firm_id=1, technology="Cobb-Douglas")

    assert firm.capital_share == 0.50
    assert np.isclose(firm.current_output, 50.0)
    assert len(firm.history) == 0


def test_accepts_better_allocation():
    firm = Firm(firm_id=1, technology="Cobb-Douglas")

    result = firm.experiment(0.70, round_number=1)

    assert result["accepted"] is True
    assert np.isclose(firm.capital_share, 0.70)
    assert firm.current_output > 50.0


def test_rejects_worse_allocation():
    firm = Firm(
        firm_id=1,
        technology="Cobb-Douglas",
        capital_share=0.70,
    )

    original_output = firm.current_output
    result = firm.experiment(0.20, round_number=1)

    assert result["accepted"] is False
    assert np.isclose(firm.capital_share, 0.70)
    assert np.isclose(firm.current_output, original_output)


def test_rejects_equal_output():
    firm = Firm(firm_id=1, technology="Cobb-Douglas")

    result = firm.experiment(0.50, round_number=1)

    assert result["accepted"] is False
    assert firm.capital_share == 0.50


def test_records_failed_experiments():
    firm = Firm(firm_id=1, technology="Cobb-Douglas")

    firm.experiment(0.70, round_number=1)
    firm.experiment(0.20, round_number=2)

    assert len(firm.history) == 2
    assert firm.history[0]["accepted"] is True
    assert firm.history[1]["accepted"] is False
    assert firm.history[1]["round"] == 2


def test_firm_histories_are_independent():
    firm_a = Firm(firm_id=1, technology="Cobb-Douglas")
    firm_b = Firm(firm_id=2, technology="CES")

    firm_a.experiment(0.70, round_number=1)

    assert len(firm_a.history) == 1
    assert len(firm_b.history) == 0


@pytest.mark.parametrize(
    "budget",
    [0, -100, float("nan"), float("inf")],
)
def test_invalid_budget(budget):
    with pytest.raises(ValueError):
        Firm(firm_id=1, technology="Linear", budget=budget)


@pytest.mark.parametrize(
    "share",
    [-0.1, 0.0, 1.0, 1.1],
)
def test_invalid_initial_share(share):
    with pytest.raises(ValueError):
        Firm(
            firm_id=1,
            technology="Linear",
            capital_share=share,
        )


def test_unknown_technology():
    with pytest.raises(ValueError):
        Firm(firm_id=1, technology="Unknown")


def test_invalid_candidate_share():
    firm = Firm(firm_id=1, technology="Linear")

    with pytest.raises(ValueError):
        firm.experiment(1.5, round_number=1)


def test_output_never_decreases():
    firm = Firm(firm_id=1, technology="CES")

    outputs = [firm.current_output]

    for round_number, q in enumerate(
        [0.20, 0.70, 0.90, 0.60, 0.65],
        start=1,
    ):
        firm.experiment(q, round_number)
        outputs.append(firm.current_output)

    assert np.all(np.diff(outputs) >= -1e-10)

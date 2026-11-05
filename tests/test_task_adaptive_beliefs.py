import pytest

from interfirm_abm.task_based_firm import TaskBasedFirm, TaskCapability
from interfirm_abm.task_economic_policy import MarketObservation
from interfirm_abm.task_adaptive_beliefs import AdaptivePriceBeliefs


def firm():
    return TaskBasedFirm(
        "p", 3, 3,
        tuple(TaskCapability(f"T{i:02d}", 1, 2, True) for i in range(1, 21)),
    )


def test_price_expectations_update_only_from_completed_round():
    beliefs = AdaptivePriceBeliefs(initial_price=10, adjustment_rate=0.5)
    f = firm()
    assert beliefs(f, MarketObservation(1, None, None)).expected_price == 10
    assert beliefs(f, MarketObservation(2, 6, 100)).expected_price == 8
    assert beliefs(f, MarketObservation(2, 6, 100)).expected_price == 8
    assert beliefs(f, MarketObservation(3, 4, 120)).expected_price == 6


def test_zero_and_full_adjustment_rates():
    f = firm()
    zero = AdaptivePriceBeliefs(10, 0)
    full = AdaptivePriceBeliefs(10, 1)
    assert zero(f, MarketObservation(2, 3, 10)).expected_price == 10
    assert full(f, MarketObservation(2, 3, 10)).expected_price == 3


def test_missing_history_and_invalid_rates_rejected():
    f = firm()
    beliefs = AdaptivePriceBeliefs(10, 0.5)
    with pytest.raises(ValueError):
        beliefs(f, MarketObservation(2, None, None))
    with pytest.raises(ValueError):
        AdaptivePriceBeliefs(10, 1.5)
    with pytest.raises(ValueError):
        AdaptivePriceBeliefs(10, float("nan"))


def test_no_skipping_rounds():
    beliefs = AdaptivePriceBeliefs(10, 0.5)
    with pytest.raises(ValueError):
        beliefs(firm(), MarketObservation(3, 5, 10))

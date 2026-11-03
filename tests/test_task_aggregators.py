"""Pure mathematical tests for candidate aggregators (not scientific validation)."""
import math
import pytest
from interfirm_abm.task_aggregators import weighted_linear, weighted_leontief, task_ces


def sample():
    return {"T01": 1.0, "T02": 4.0}, {"T01": 0.5, "T02": 0.5}


def test_linear():
    q, w = sample()
    assert weighted_linear(q, w) == pytest.approx(2.5)


def test_leontief():
    q, w = sample()
    assert weighted_leontief(q, w) == pytest.approx(2.0)


def test_ces_geometric_limit():
    q, w = sample()
    assert task_ces(q, w, sigma=1) == pytest.approx(2.0)


def test_ces_sigma_two():
    q, w = sample()
    assert task_ces(q, w, sigma=2) == pytest.approx(2.25)


def test_ces_zero_essential_task():
    q = {"T01": 0.0, "T02": 4.0}
    w = {"T01": 0.5, "T02": 0.5}
    assert task_ces(q, w, sigma=0.5) == 0.0
    assert task_ces(q, w, sigma=1) == 0.0
    assert task_ces(q, w, sigma=2) == pytest.approx(1.0)


def test_equal_activity_invariant():
    q = {"T01": 3.0, "T02": 3.0}
    w = {"T01": 0.2, "T02": 0.8}
    for sigma in (0.5, 1.0, 2.0, 10.0):
        assert task_ces(q, w, sigma=sigma) == pytest.approx(3.0)


def test_scale_homogeneity():
    q, w = sample()
    for sigma in (0.5, 1.0, 2.0):
        assert task_ces({k: v * 3 for k, v in q.items()}, w, sigma=sigma) == pytest.approx(
            3 * task_ces(q, w, sigma=sigma)
        )


def test_invalid_weights():
    with pytest.raises(ValueError, match="sum to one"):
        task_ces({"T01": 1, "T02": 2}, {"T01": .2, "T02": .2}, sigma=2)


def test_invalid_sigma():
    q, w = sample()
    with pytest.raises(ValueError, match="sigma"):
        task_ces(q, w, sigma=0)

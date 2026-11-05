"""Scientific gates for the isolated CES counterfactual, not the 256-player game."""
from dataclasses import replace
import pytest

from interfirm_abm.task_ces_counterfactual import CESExperiment, paired_counterfactual, simulate, robustness


def test_ai_does_not_change_a_or_pre_shock_path():
    spec = CESExperiment(rounds=12, ai_round=7)
    result = paired_counterfactual(spec, players=12)
    assert result["treated"]["rows"][:6] == [
        {**row, "ai":True} for row in result["control"]["rows"][:6]
    ]
    assert result["metrics"]["quantity"]["pre_difference"] == pytest.approx(0.)
    assert result["metrics"]["total_profit"]["pre_difference"] == pytest.approx(0.)
    assert all(row["sigma"] == spec.sigma_before for row in result["treated"]["rows"][:6])
    assert all(row["sigma"] == spec.sigma_after for row in result["treated"]["rows"][6:])


def test_accounting_and_feasibility_and_determinism():
    spec = CESExperiment(rounds=14, ai_round=8, seed=11)
    for learning in ("optimization", "trial_error", "softmax"):
        first = simulate(spec, ai=True, players=12, learning=learning)
        second = simulate(spec, ai=True, players=12, learning=learning)
        assert first == second
        for row in first["rows"]:
            assert row["quantity"] > 0
            assert row["capital"] > 0 and row["labor"] > 0
            assert row["price"] >= 0
            assert row["total_profit"] <= row["price"]*row["quantity"]


def test_robustness_grid_is_complete():
    rows = robustness(seeds=(11,17),sigma_after_values=(1.2,1.8),players=8,rounds=10)
    assert len(rows) == 4
    assert {(r["seed"],r["sigma_after"]) for r in rows} == {
        (11,1.2),(11,1.8),(17,1.2),(17,1.8)
    }
    assert all(r["delta_quantity"] == r["delta_quantity"] for r in rows)


def test_imitation_not_misrepresented_as_optimization():
    with pytest.raises(ValueError, match="approved observation regime"):
        simulate(CESExperiment(rounds=10,ai_round=6),ai=True,players=8,learning="imitation")

import pytest
from interfirm_abm.task_ar_benchmark import Parameters, run_game, summarize


def test_default_game_has_matched_100_firms_two_periods():
    rows = run_game()
    assert len(rows) == 200
    assert len({row["firm_id"] for row in rows}) == 100
    assert {row["phase"] for row in rows} == {"pre", "post"}


def test_reproducibility_and_nonnegative_inputs():
    rows = run_game()
    assert rows == run_game()
    assert all(r["labor"] >= 0 and r["capital"] >= 0 for r in rows)


def test_automation_expansion_cannot_raise_minimized_cost_under_fixed_prices():
    rows = run_game()
    pre = {r["firm_id"]: r for r in rows if r["phase"] == "pre"}
    post = {r["firm_id"]: r for r in rows if r["phase"] == "post"}
    for firm in pre:
        assert post[firm]["cost"] <= pre[firm]["cost"] + 1e-7
        assert post[firm]["automated_tasks"] >= pre[firm]["automated_tasks"]


def test_no_eligibility_means_labor_only():
    rows = run_game(Parameters(firms=1, tasks=5, initial_eligible_share=0,
                               post_eligible_share=0))
    assert all(r["capital"] == 0 and r["automated_tasks"] == 0 for r in rows)
    assert all(r["output"] == 20 for r in rows)


def test_summary_accounting_identity():
    rows = run_game(Parameters(firms=2))
    totals = summarize(rows)
    for phase in ("pre", "post"):
        assert totals[phase]["profit"] == pytest.approx(
            totals[phase]["revenue"] - totals[phase]["cost"], abs=1e-5
        )


def test_invalid_parameters_rejected():
    with pytest.raises(ValueError):
        run_game(Parameters(initial_eligible_share=0.8, post_eligible_share=0.2))

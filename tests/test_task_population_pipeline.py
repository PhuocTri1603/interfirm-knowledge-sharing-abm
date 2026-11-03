"""100-firm pipeline smoke test with explicitly non-scientific test parameters.

The test checks integration, invariants, and reproducibility only.
Do not interpret the output as simulated economic findings.
"""
from pathlib import Path
import math

from interfirm_abm.task_based_firm import load_approved_population
from interfirm_abm.task_bundle import TaskChoice
from interfirm_abm.task_plan_selection import CandidatePlan
from interfirm_abm.task_pipeline import evaluate_local_neighborhood
from interfirm_abm.task_economics import EconomicPrices


ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / "data/firms/task_based_100_firms_profiles.csv"
TASKS = ROOT / "data/firms/task_based_100_firms_tasks.csv"


def _run_population():
    firms = load_approved_population(PROFILES, TASKS)
    results = []
    for firm in firms:
        # A zero-activity baseline tests plumbing without inventing a policy.
        baseline = CandidatePlan(
            "zero_baseline",
            tuple(TaskChoice(t.task_id, "labor", 0.0) for t in firm.tasks),
        )
        result = evaluate_local_neighborhood(
            firm, baseline,
            activity_step=1.0,  # TEST FIXTURE, not an economic assumption
            aggregate_tasks=lambda q: sum(q.values()),  # TEST STUB
            prices=EconomicPrices(
                output_price=1.0,
                capital_unit_cost=1.0,
                labor_unit_cost=1.0,
            ),  # TEST FIXTURE, not calibrated prices
        )
        results.append(result)
    return results


def test_all_100_firms_pipeline_and_invariants():
    results = _run_population()
    assert len(results) == 100
    assert len({r.firm_id for r in results}) == 100
    for r in results:
        assert r.generated_candidate_count >= 21
        assert 1 <= r.feasible_candidate_count <= r.generated_candidate_count
        assert r.baseline_profit == 0.0
        assert r.best_profit_gain_over_baseline is not None
        assert math.isfinite(r.best_profit_gain_over_baseline)
        assert r.best_profit_gain_over_baseline >= 0
        assert r.comparison.best_candidate_id is not None
        assert len(r.comparison.results) == r.generated_candidate_count
        assert all(
            x.profit is None if not x.feasible else math.isfinite(x.profit)
            for x in r.comparison.results
        )


def test_population_pipeline_is_deterministic():
    first = _run_population()
    second = _run_population()
    assert first == second

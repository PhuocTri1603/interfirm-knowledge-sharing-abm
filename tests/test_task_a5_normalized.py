"""A5 production gates: pure-mode, normalization, CES regimes, paired designs.

Run: python -m unittest discover -s tests -p 'test_task_a5_normalized.py'
No market-price/profit validation is implied.
"""
import math
import unittest
from pathlib import Path

from interfirm_abm.task_a5_normalized import (
    A5Technology, TASK_IDS, SIGMA_SCENARIOS, paired_technologies,
    reference_for_profile, technology_for_profile,
)
from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm, TaskCapability, load_approved_population
from interfirm_abm.task_experiment_dimensions import strategy_player_ids


def fixture():
    return TaskBasedFirm(
        firm_id="F-test", capital_endowment=40., labor_endowment=20.,
        tasks=tuple(TaskCapability(k, 1. + i / 20., 2., i % 2 == 0)
                    for i, k in enumerate(TASK_IDS))
    )


class TestA5(unittest.TestCase):
    def setUp(self):
        self.firm = fixture()
        self.reference = reference_for_profile(self.firm)

    def test_T1_all_100_profiles_and_256_player_roster(self):
        root = Path(__file__).resolve().parents[1] / "data" / "firms"
        population = load_approved_population(
            root / "task_based_100_firms_profiles.csv",
            root / "task_based_100_firms_tasks.csv",
        )
        roster = strategy_player_ids()
        self.assertEqual(len(population), 100)
        self.assertEqual(len(roster), 256)
        self.assertEqual(len(set(roster)), 256)
        for index, firm in enumerate(population):
            self.assertEqual(firm.firm_id, f"F{index+1:03d}")
            self.assertEqual(len(firm.tasks), 20)
            techs = paired_technologies(firm)
            for sigma, tech in techs.items():
                self.assertAlmostEqual(tech.output_index(tech.reference), 1.)
                labor_plan = [TaskAllocation(k, firm.labor_endowment / 20., 0.)
                              for k in TASK_IDS]
                self.assertAlmostEqual(tech.output_from_allocation(firm, labor_plan), 1.)

    def test_reference_and_tasks_partial_T1(self):
        self.assertEqual(len(self.reference), 20)
        self.assertEqual(set(self.reference), set(TASK_IDS))
        self.assertTrue(all(v > 0 for v in self.reference.values()))
        self.assertAlmostEqual(sum(self.reference[k] / self.firm.tasks[i].labor_productivity
                                   for i, k in enumerate(TASK_IDS)), 20.)
        self.assertRaises(ValueError, A5Technology, {"T01": 1.}, 1.)

    def test_T2_feasible_pure_mode_and_eligibility(self):
        labor = [TaskAllocation(k, 1., 0.) for k in TASK_IDS]
        self.assertEqual(self.firm.evaluate_allocation(labor), self.reference)
        self.assertAlmostEqual(technology_for_profile(self.firm, 1.).output_from_allocation(self.firm, labor), 1.)
        invalid = labor.copy()
        invalid[0] = TaskAllocation("T01", 1., 1.)
        with self.assertRaises(ValueError):
            self.firm.evaluate_allocation(invalid)
        invalid[0] = TaskAllocation("T01", 0., 1.)
        invalid[1] = TaskAllocation("T02", 0., 1.)
        with self.assertRaises(ValueError):
            self.firm.evaluate_allocation(invalid)
        excessive = [TaskAllocation(k, 2., 0.) for k in TASK_IDS]
        with self.assertRaises(ValueError):
            self.firm.evaluate_allocation(excessive)

    def test_T3_ces_anchor_zero_monotonicity_homogeneity_limits(self):
        for sigma in (0.05, 0.5, 0.999999, 1., 1.000001, 2., 10000.):
            technology = A5Technology(self.reference, sigma)
            self.assertAlmostEqual(technology.output_index(self.reference), 1., places=8)
            doubled = {k: 2 * v for k, v in self.reference.items()}
            self.assertAlmostEqual(technology.output_index(doubled), 2., places=8)
            larger = doubled.copy()
            larger["T01"] *= 1.1
            self.assertGreaterEqual(technology.output_index(larger), 2.)
            zero = self.reference.copy()
            zero["T01"] = 0.
            if sigma <= 1.:
                self.assertEqual(technology.output_index(zero), 0.)
            else:
                self.assertGreater(technology.output_index(zero), 0.)
        mixed = {k: v * (0.5 if i < 10 else 2.) for i, (k, v) in enumerate(self.reference.items())}
        low = A5Technology(self.reference, 0.001).output_index(mixed)
        high = A5Technology(self.reference, 1e7).output_index(mixed)
        self.assertAlmostEqual(low, 0.5, places=2)
        self.assertAlmostEqual(high, 1.25, places=4)

    def test_T3_invalid_values_and_stability(self):
        for sigma in (0., -1., float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                A5Technology(self.reference, sigma)
        invalid = self.reference.copy()
        invalid["T01"] = -1.
        with self.assertRaises(ValueError):
            A5Technology(self.reference, 1.).output_index(invalid)
        invalid["T01"] = float("nan")
        with self.assertRaises(ValueError):
            A5Technology(self.reference, 1.).output_index(invalid)
        self.assertEqual(A5Technology(self.reference, 2.).output_index({k: 0. for k in TASK_IDS}), 0.)

    def test_shared_reference_partial_T5_T6(self):
        treatments = paired_technologies(self.firm)
        self.assertEqual(tuple(treatments), SIGMA_SCENARIOS)
        self.assertTrue(all(t.reference == self.reference for t in treatments.values()))
        self.assertEqual(len({id(t.reference) for t in treatments.values()}), 3)
        self.assertTrue(all(abs(t.output_index(self.reference) - 1.) < 1e-10
                            for t in treatments.values()))

    def test_T3_rank_changes_with_sigma_are_possible(self):
        # Technology counterfactual can change output comparisons, not assumed winner.
        balanced = dict(self.reference)
        specialized = {k: v * (0.1 if i < 10 else 3.)
                       for i, (k, v) in enumerate(self.reference.items())}
        self.assertLess(A5Technology(self.reference, 0.5).output_index(specialized),
                        A5Technology(self.reference, 0.5).output_index(balanced))
        self.assertGreater(A5Technology(self.reference, 2.).output_index(specialized),
                           A5Technology(self.reference, 2.).output_index(balanced))

    def test_T4_task_units_rescale_together(self):
        for sigma in SIGMA_SCENARIOS:
            base = A5Technology(self.reference, sigma)
            activities = {k: v * (1.5 if i % 2 else 0.8)
                          for i, (k, v) in enumerate(self.reference.items())}
            scales = {k: 2. + i for i, k in enumerate(TASK_IDS)}
            scaled_ref = {k: v * scales[k] for k, v in self.reference.items()}
            scaled_q = {k: v * scales[k] for k, v in activities.items()}
            self.assertAlmostEqual(base.output_index(activities),
                                   A5Technology(scaled_ref, sigma).output_index(scaled_q),
                                   places=10)

    def test_T8_governance_no_market_units(self):
        self.assertEqual(SIGMA_SCENARIOS, (0.5, 1., 2.))
        self.assertFalse(hasattr(A5Technology, "profit"))
        self.assertFalse(hasattr(A5Technology, "market_price"))


if __name__ == "__main__":
    unittest.main()

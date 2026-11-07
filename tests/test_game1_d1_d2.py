"""Regression checks for researcher-approved D1/D2 parameter calibration.

Run: python -m unittest discover -s tests -p 'test_game1_d1_d2.py'
"""
import unittest

from interfirm_abm.task_a6_market import (
    approved_d1_d2_parameters,
    approved_profiles,
    reference_allocation,
    reference_market_quantity,
)
from interfirm_abm.task_a5_normalized import technology_for_profile


class D1D2CalibrationTests(unittest.TestCase):
    def test_baseline_demand_and_common_factor_prices(self):
        p = approved_d1_d2_parameters()
        self.assertAlmostEqual(p.demand_intercept, 2.0)
        self.assertAlmostEqual(p.demand_slope, 1.0 / 256.0)
        self.assertAlmostEqual(p.wage, 0.5 / 51.5)
        self.assertAlmostEqual(p.rental, 0.5 / 51.5)
        self.assertAlmostEqual(p.demand_intercept - p.demand_slope * 256.0, 1.0)
        self.assertEqual(p.adaptive_lambda, 0.5)

    def test_demand_elasticity_scenarios(self):
        for elasticity in (0.5, 1.0, 2.0, 5.0):
            p = approved_d1_d2_parameters(elasticity=elasticity)
            self.assertAlmostEqual(p.demand_intercept - p.demand_slope * 256.0, 1.0)
            self.assertAlmostEqual(1.0 / (256.0 * p.demand_slope), elasticity)

    def test_d2_robustness(self):
        for theta in (0.5, 1.0, 2.0):
            for kappa in (0.25, 0.5, 0.75):
                p = approved_d1_d2_parameters(theta=theta, kappa=kappa)
                self.assertAlmostEqual(p.wage / p.rental, theta)
                self.assertAlmostEqual(p.wage * 51.5, kappa)

    def test_reference_output_for_all_configurations(self):
        profiles = approved_profiles()
        self.assertEqual(len(profiles), 100)
        for firm in profiles:
            self.assertEqual(reference_market_quantity(firm), 256.0)
            allocation = reference_allocation(firm)
            for sigma in (0.5, 1.0, 2.0):
                self.assertAlmostEqual(
                    technology_for_profile(firm, sigma).output_from_allocation(
                        firm, list(allocation)), 1.0, places=9)

    def test_invalid_parameters_rejected(self):
        for kwargs in ({"theta": 0}, {"kappa": 0}, {"elasticity": 0},
                       {"adaptive_lambda": -0.1}, {"adaptive_lambda": 1.1}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    approved_d1_d2_parameters(**kwargs)


if __name__ == "__main__":
    unittest.main()

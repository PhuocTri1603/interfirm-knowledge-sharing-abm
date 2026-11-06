"""A6 staged invariant checks; explicit illustrative demand is NOT approved calibration."""
import math
import random
import unittest
from interfirm_abm.task_a6_market import (
    A6Parameters, approved_profiles, rank_softmax, reference_allocation,
    reference_market_quantity, run_a6_market,
)
from interfirm_abm.task_a5_normalized import technology_for_profile
from interfirm_abm.task_strategy_engine import strategy_roster


class TestA6(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.firm = approved_profiles()[0]
        # Testing-only demand; do NOT treat these numbers as researcher baseline.
        cls.p = A6Parameters(10.0, 0.01, 0.15, 1.0, 0.5, 11)

    def test_reference_anchor_all_sigma(self):
        self.assertEqual(reference_market_quantity(self.firm), 256)
        for sigma in (0.5, 1.0, 2.0):
            tech = technology_for_profile(self.firm, sigma)
            self.assertAlmostEqual(tech.output_from_allocation(self.firm, list(reference_allocation(self.firm))), 1.0)

    def test_rank_softmax_money_unit_invariance(self):
        a = {"a": (3.,), "b": (2.,), "c": (1.,)}
        b = {k: (1000 * v[0],) for k, v in a.items()}
        self.assertEqual(rank_softmax(a, 1., random.Random(4)),
                         rank_softmax(b, 1., random.Random(4)))

    def test_single_round_full_roster_and_accounting(self):
        result = run_a6_market(self.firm, 1., self.p, rounds=1)
        self.assertEqual(len(result["players"]), 256)
        self.assertEqual(len(result["ranking"]), 256)
        self.assertFalse(result["research_validated"])
        market = result["market"][0]
        rows = result["players"]
        self.assertAlmostEqual(sum(x["quantity"] for x in rows), market["quantity"])
        self.assertAlmostEqual(sum(x["profit"] for x in rows), market["profit"])
        self.assertAlmostEqual(market["price"], max(0, 10. - .01 * market["quantity"]))
        for x in rows:
            self.assertAlmostEqual(x["profit"], x["price"] * x["quantity"] - x["cost"])
            self.assertGreaterEqual(x["quantity"], 0)
            self.assertGreaterEqual(x["cost"], 0)
            self.assertTrue(math.isfinite(x["profit"]))
        self.assertTrue(all(v <= 1 for v in result["feedback_counts"].values()))

    def test_shutdown_zero_price_and_no_double_update(self):
        # No action can yield positive predicted net profit at the tiny prior
        # for all profiles, but a forced low actual price tests accounting.
        p = A6Parameters(0.0001, 100., .1, 1., .5, 11)
        result = run_a6_market(self.firm, 2., p, rounds=2)
        self.assertEqual(len(result["players"]), 512)
        self.assertTrue(all(x["profit"] <= 0 for x in result["players"]))
        self.assertTrue(all(v <= 2 for v in result["feedback_counts"].values()))

    def test_three_sigma_paired_determinism(self):
        for sigma in (0.5, 1., 2.):
            first = run_a6_market(self.firm, sigma, self.p, rounds=2)
            second = run_a6_market(self.firm, sigma, self.p, rounds=2)
            self.assertEqual(first["market"], second["market"])
            self.assertEqual(first["ranking"], second["ranking"])

    def test_parameter_validation(self):
        with self.assertRaises(ValueError):
            A6Parameters(10, 0, .1, 1, .5, 1)
        with self.assertRaises(ValueError):
            A6Parameters(10, .1, .1, 0, .5, 1)


if __name__ == "__main__":
    unittest.main()

"""Approved D3 accounting invariants (no full Game 1 run)."""
import unittest
from types import SimpleNamespace
from interfirm_abm.task_based_firm import TaskAllocation
from interfirm_abm.task_l34_economics import L34Parameters, economic_extra_cost
from interfirm_abm.task_a6_market import approved_d1_d2_parameters

P = L34Parameters(capacity_ratio=2, adjustment_unit_cost=.001,
                  efficiency_gain=.2, adoption_fee=.001)
I = SimpleNamespace(L3="flexible", L4="eligibility")
F = SimpleNamespace(tasks=())
def plan(l=0., k=0., k2=0.):
    return (TaskAllocation("t1", l, k), TaskAllocation("t2", 0., k2))
def cost(new, old=None, adopted=frozenset(), delta=.1, mu=.1, kappa=.5):
    p = approved_d1_d2_parameters(adjustment_delta=delta, ai_adoption_mu=mu, kappa=kappa)
    return economic_extra_cost(I, new, old, F, adopted, P,
        wage=p.wage, rental=p.rental, delta=p.adjustment_delta,
        adoption_fee=p.ai_adoption_mu*p.kappa/20)

class D3Tests(unittest.TestCase):
    def test_first_round_adjustment_and_ai_fee(self):
        a, fee, new = cost(plan(10, 2))
        self.assertAlmostEqual(a, .1*(12*.5/51.5))
        self.assertAlmostEqual(fee, .0025)
        self.assertEqual(new, frozenset({"t1"}))
    def test_total_inputs_not_task_reallocation(self):
        a, fee, new = cost(plan(0, 0, 10), plan(0, 10, 0), frozenset({"t1","t2"}))
        self.assertEqual(a, 0.)
        self.assertEqual(fee, 0.)
        self.assertEqual(new, frozenset())
    def test_shutdown_and_reentry_without_double_fee(self):
        active = plan(10, 5)
        a, fee, new = cost(active)
        stop_a, stop_fee, stop_new = cost(plan(), active, new)
        self.assertAlmostEqual(stop_a, a)
        self.assertEqual(stop_fee, 0.)
        self.assertFalse(stop_new)
        restart_a, restart_fee, restart_new = cost(active, plan(), new)
        self.assertAlmostEqual(restart_a, a)
        self.assertEqual(restart_fee, 0.)
        self.assertFalse(restart_new)
    def test_ai_fee_once_across_all_l4(self):
        for l4 in ("eligibility", "efficiency", "adoption_cost", "combined"):
            identity = SimpleNamespace(L3="investment", L4=l4)
            p = approved_d1_d2_parameters()
            _, fee, new = economic_extra_cost(identity, plan(k=2,k2=3), None, F,
                frozenset(), P, wage=p.wage, rental=p.rental,
                delta=p.adjustment_delta, adoption_fee=p.ai_adoption_mu*p.kappa/20)
            self.assertEqual(len(new), 2)
            self.assertAlmostEqual(fee, .005)
    def test_robustness_zero_friction(self):
        a, fee, new = cost(plan(10, 2), delta=0, mu=0)
        self.assertEqual((a,fee), (0.,0.))
        self.assertEqual(new, frozenset({"t1"}))
if __name__ == "__main__":
    unittest.main()

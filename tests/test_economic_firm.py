"""Contract tests for the new economic player layer."""
import pytest

from interfirm_abm.economic_firm import (
    EconomicFirm, ProductionPlan, ProductionTechnology,
    illustrative_population, standard_technology,
)


def test_four_standard_technologies_are_available():
    for kind in ("Cobb-Douglas", "Leontief", "Linear", "CES"):
        assert standard_technology(kind).capacity(10, 10) >= 0


def test_custom_technology_is_supported():
    technology = ProductionTechnology("custom", lambda k, l: min(k, 2 * l))
    assert technology.capacity(4, 3) == 4


def test_feasible_plan_and_profit_accounting():
    firm = EconomicFirm(1, standard_technology("Linear", alpha=0.5), 10, 10)
    plan = ProductionPlan(5, 5, 5)
    assert firm.can_execute(plan)
    result = firm.evaluate_plan(plan, output_price=3,
                                capital_unit_cost=1, labor_unit_cost=2)
    assert result["revenue"] == 15
    assert result["variable_cost"] == 15
    assert result["profit"] == 0


def test_infeasible_output_rejected():
    firm = EconomicFirm(1, standard_technology("Linear", alpha=0.5), 10, 10)
    with pytest.raises(ValueError):
        firm.evaluate_plan(ProductionPlan(5, 5, 100), output_price=1,
                           capital_unit_cost=1, labor_unit_cost=1)


def test_endowment_constraint():
    firm = EconomicFirm(1, standard_technology("Linear"), 3, 10)
    assert not firm.can_execute(ProductionPlan(4, 1, 1))


def test_population_is_heterogeneous_and_reproducible():
    a = illustrative_population(100, seed=12)
    b = illustrative_population(100, seed=12)
    assert len(a) == len({f.firm_id for f in a}) == 100
    assert [f.technology.name for f in a] == [f.technology.name for f in b]
    assert [f.technology.productivity for f in a] == [
        f.technology.productivity for f in b]
    assert len({f.technology.name for f in a}) == 4
    assert len({f.capital_endowment for f in a}) > 1


@pytest.mark.parametrize("bad", [-1, float("nan"), float("inf")])
def test_bad_endowments_rejected(bad):
    with pytest.raises(ValueError):
        EconomicFirm(1, standard_technology("CES"), bad, 10)


def test_negative_profits_allowed():
    firm = EconomicFirm(1, standard_technology("Linear"), 10, 10)
    result = firm.evaluate_plan(ProductionPlan(1, 1, 1), output_price=0,
                                capital_unit_cost=1, labor_unit_cost=1)
    assert result["profit"] == -2

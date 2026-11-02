"""Charter-aligned economic firm players; independent of legacy learning agents.

This module models technological feasibility and economic accounting, not
learning, market clearing, or endogenous cooperation.
"""
from dataclasses import dataclass, field
from typing import Callable, Mapping
import math

from interfirm_abm.production import cobb_douglas, leontief, linear, ces


@dataclass(frozen=True)
class ProductionPlan:
    capital: float
    labor: float
    output: float

    def __post_init__(self):
        for name in ("capital", "labor", "output"):
            v = getattr(self, name)
            if not math.isfinite(v) or v < 0:
                raise ValueError(f"{name} must be finite and nonnegative")


@dataclass(frozen=True)
class ProductionTechnology:
    """A technology evaluates feasibility, not a firm's preferences."""
    name: str
    output_fn: Callable[[float, float], float]
    parameters: Mapping[str, float] = field(default_factory=dict)
    productivity: float = 1.0

    def __post_init__(self):
        if not math.isfinite(self.productivity) or self.productivity <= 0:
            raise ValueError("Productivity must be finite and positive")

    def capacity(self, capital: float, labor: float) -> float:
        if any(not math.isfinite(x) or x < 0 for x in (capital, labor)):
            raise ValueError("Inputs must be finite and nonnegative")
        result = self.productivity * float(self.output_fn(capital, labor, **self.parameters))
        if not math.isfinite(result) or result < 0:
            raise ValueError("Technology produced invalid output")
        return result

    def feasible(self, plan: ProductionPlan, tolerance: float = 1e-9) -> bool:
        return plan.output <= self.capacity(plan.capital, plan.labor) + tolerance


def standard_technology(kind: str, *, productivity: float = 1.0,
                        alpha: float = 0.7, kappa: float = 0.7,
                        rho: float = -0.5) -> ProductionTechnology:
    """Four standard functional forms, not an exhaustive technology taxonomy."""
    catalog = {
        "Cobb-Douglas": (cobb_douglas, {"alpha": alpha}),
        "Leontief": (leontief, {"kappa": kappa}),
        "Linear": (linear, {"alpha": alpha}),
        "CES": (ces, {"alpha": alpha, "rho": rho}),
    }
    if kind not in catalog:
        raise ValueError(f"Unknown standard technology: {kind}")
    fn, params = catalog[kind]
    tech = ProductionTechnology(kind, fn, params, productivity)
    tech.capacity(1.0, 1.0)  # Validate parameters early.
    return tech


@dataclass
class EconomicFirm:
    """Firm identity, owned technology, feasible actions, and payoff accounting.

    No decision policy is assumed: the researcher must approve firm information,
    optimization objectives, market demand, and adjustment dynamics first.
    """
    firm_id: int
    technology: ProductionTechnology
    capital_endowment: float
    labor_endowment: float
    cash: float = 0.0
    observations: list[dict] = field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.firm_id, int) or self.firm_id < 0:
            raise ValueError("firm_id must be a nonnegative integer")
        for name in ("capital_endowment", "labor_endowment", "cash"):
            v = getattr(self, name)
            if not math.isfinite(v) or v < 0:
                raise ValueError(f"{name} must be finite and nonnegative")

    def can_execute(self, plan: ProductionPlan) -> bool:
        return (plan.capital <= self.capital_endowment
                and plan.labor <= self.labor_endowment
                and self.technology.feasible(plan))

    def evaluate_plan(self, plan: ProductionPlan, *, output_price: float,
                      capital_unit_cost: float, labor_unit_cost: float,
                      fixed_cost: float = 0.0) -> dict:
        if not self.can_execute(plan):
            raise ValueError("Plan exceeds endowments or technological feasibility")
        if any(not math.isfinite(x) or x < 0 for x in
               (output_price, capital_unit_cost, labor_unit_cost, fixed_cost)):
            raise ValueError("Prices and costs must be finite and nonnegative")
        revenue = output_price * plan.output
        variable_cost = capital_unit_cost * plan.capital + labor_unit_cost * plan.labor
        return {
            "firm_id": self.firm_id,
            "revenue": revenue,
            "variable_cost": variable_cost,
            "fixed_cost": fixed_cost,
            "profit": revenue - variable_cost - fixed_cost,
        }


def illustrative_population(size: int = 100, *, seed: int = 42) -> list[EconomicFirm]:
    """Reproducible heterogeneous demonstration, NOT calibrated firm frequencies.

    Technology shares, productivity and endowments are provisional examples,
    not theoretically mandated or empirically estimated distributions.
    """
    import random
    if not isinstance(size, int) or size <= 0:
        raise ValueError("size must be a positive integer")
    rng = random.Random(seed)
    kinds = ["Cobb-Douglas", "Leontief", "Linear", "CES"]
    firms = []
    for i in range(size):
        kind = kinds[i % len(kinds)]
        tech = standard_technology(kind, productivity=rng.uniform(0.8, 1.2),
                                   alpha=rng.uniform(0.3, 0.7),
                                   kappa=rng.uniform(0.3, 0.7),
                                   rho=rng.uniform(-1.5, 0.5))
        firms.append(EconomicFirm(
            firm_id=i + 1, technology=tech,
            capital_endowment=rng.uniform(50, 150),
            labor_endowment=rng.uniform(50, 150),
            cash=rng.uniform(0, 50)))
    return firms

"""Bridge the existing 20-task production model to shared-market accounting.

Task aggregation and cost parameters remain explicitly supplied. A capital/
labor decision must be accompanied by a feasible allocation across 20 tasks.
This adapter does not select an aggregator or infer task allocations.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isclose
from typing import Callable, Mapping

from interfirm_abm.task_based_firm import TaskAllocation, TaskBasedFirm
from interfirm_abm.task_economic_policy import (
    EconomicSpecification, PlayerState, ProductionDecision,
)


@dataclass(frozen=True)
class TaskMarketTechnology:
    firms: Mapping[str, TaskBasedFirm]
    allocations: Mapping[str, tuple[TaskAllocation, ...]]
    aggregate_tasks: Callable[[Mapping[str, float]], float]
    capital_unit_cost: float
    labor_unit_cost: float
    inverse_demand: Callable[[float], float]

    def __post_init__(self) -> None:
        from math import isfinite
        if (not isfinite(self.capital_unit_cost) or not isfinite(self.labor_unit_cost)
                or self.capital_unit_cost < 0 or self.labor_unit_cost < 0):
            raise ValueError("input costs must be finite and nonnegative")
        if not self.firms or set(self.firms) != set(self.allocations):
            raise ValueError("every task-based player requires explicit allocations")
        for key, firm in self.firms.items():
            if key != firm.firm_id:
                raise ValueError("firm ID mismatch")
            firm.evaluate_allocation(list(self.allocations[key]))

    def _activities(self, player: PlayerState, decision: ProductionDecision) -> Mapping[str, float]:
        firm = self.firms[player.player_id]
        if (not isclose(player.capital_endowment, firm.capital_endowment, abs_tol=1e-9)
                or not isclose(player.labor_endowment, firm.labor_endowment, abs_tol=1e-9)):
            raise ValueError("player endowments disagree with task firm")
        allocations = self.allocations[player.player_id]
        used_capital = sum(a.capital for a in allocations)
        used_labor = sum(a.labor for a in allocations)
        if (not isclose(decision.capital, used_capital, rel_tol=0, abs_tol=1e-9)
                or not isclose(decision.labor, used_labor, rel_tol=0, abs_tol=1e-9)):
            raise ValueError("K/L decision must match 20-task allocation")
        return firm.evaluate_allocation(list(allocations))

    def specification(self) -> EconomicSpecification:
        def output(player: PlayerState, decision: ProductionDecision) -> float:
            return float(self.aggregate_tasks(self._activities(player, decision)))

        def cost(player: PlayerState, decision: ProductionDecision) -> float:
            self._activities(player, decision)
            return self.capital_unit_cost * decision.capital + self.labor_unit_cost * decision.labor

        return EconomicSpecification(output, cost, self.inverse_demand)

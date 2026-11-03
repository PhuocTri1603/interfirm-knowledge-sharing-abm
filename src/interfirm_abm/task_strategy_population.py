"""Extensible, behavior-neutral strategy registry and matched firm clones.

This module builds an experiment population, not a market-clearing model.
Strategy IDs are labels only until researcher-approved decision rules exist.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from interfirm_abm.task_based_firm import TaskBasedFirm


@dataclass(frozen=True)
class StrategySpec:
    strategy_id: str

    def __post_init__(self) -> None:
        if not self.strategy_id or not self.strategy_id.strip():
            raise ValueError("strategy_id must be nonempty")
        if self.strategy_id != self.strategy_id.strip() or "::" in self.strategy_id:
            raise ValueError("strategy_id cannot have surrounding whitespace or '::'")


@dataclass(frozen=True)
class StrategyClone:
    agent_id: str
    base_firm_id: str
    strategy_id: str
    firm: TaskBasedFirm


@dataclass(frozen=True)
class SharedMarketPopulation:
    strategies: tuple[StrategySpec, ...]
    clones: tuple[StrategyClone, ...]

    def __post_init__(self) -> None:
        ids = [c.agent_id for c in self.clones]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate agent IDs")

    @property
    def strategy_roster(self) -> tuple[str, ...]:
        return tuple(s.strategy_id for s in self.strategies)


def build_shared_market_population(
    base_firms: Iterable[TaskBasedFirm],
    strategies: Iterable[StrategySpec],
) -> SharedMarketPopulation:
    """Fully cross base firms with strategies in ONE market.

    Clone attributes are identical at t=0, but each clone is an independent
    immutable firm object. No choices, prices, payoffs or competition are run.
    """
    firms = tuple(base_firms)
    roster = tuple(strategies)
    if not firms or not roster:
        raise ValueError("At least one base firm and one strategy required")
    firm_ids = [f.firm_id for f in firms]
    strategy_ids = [s.strategy_id for s in roster]
    if len(firm_ids) != len(set(firm_ids)):
        raise ValueError("Duplicate base firm IDs")
    if len(strategy_ids) != len(set(strategy_ids)):
        raise ValueError("Duplicate strategy IDs")
    if any(not f.firm_id or "::" in f.firm_id for f in firms):
        raise ValueError("Base firm IDs must be nonempty and cannot contain '::'")
    clones = tuple(
        StrategyClone(
            agent_id=f"{firm.firm_id}::{strategy.strategy_id}",
            base_firm_id=firm.firm_id,
            strategy_id=strategy.strategy_id,
            firm=TaskBasedFirm(
                firm_id=f"{firm.firm_id}::{strategy.strategy_id}",
                capital_endowment=firm.capital_endowment,
                labor_endowment=firm.labor_endowment,
                tasks=firm.tasks,
            ),
        )
        for firm in firms
        for strategy in roster
    )
    return SharedMarketPopulation(strategies=roster, clones=clones)

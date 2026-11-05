import pytest

from interfirm_abm.task_based_firm import TaskBasedFirm, TaskCapability
from interfirm_abm.task_mechanism_audit import PlayerMechanism, audit_mixed_configuration


P1 = "L3=flexible|L4=eligibility|L5=competitive|L6=optimization"
P2 = P1.replace("L6=optimization", "L6=softmax")


def firm(player, capital=10):
    return TaskBasedFirm(
        player, capital, 10,
        tuple(TaskCapability(f"T{i:02d}", 1, 1, True) for i in range(1, 21)),
    )


def test_rejects_label_only_strategy_population():
    players = {P1: firm(P1), P2: firm(P2)}
    same = PlayerMechanism("same_production", "same_decision", "same_info")
    with pytest.raises(ValueError, match="identical declared mechanisms"):
        audit_mixed_configuration(players, {P1: same, P2: same}, expected_players=2)


def test_accepts_distinct_declared_mechanisms_with_common_resources():
    players = {P1: firm(P1), P2: firm(P2)}
    mechanisms = {
        P1: PlayerMechanism("linear", "optimize", "past_price"),
        P2: PlayerMechanism("linear", "softmax", "past_price"),
    }
    audit = audit_mixed_configuration(players, mechanisms, expected_players=2)
    assert audit["unique_mechanism_signatures"] == 2
    assert audit["common_initial_capital"] == 10
    assert audit["status"] == "structural_audit_only_not_research_validated"


def test_rejects_unequal_starting_resources():
    players = {P1: firm(P1), P2: firm(P2, capital=20)}
    mechanisms = {
        P1: PlayerMechanism("linear", "optimize", "past_price"),
        P2: PlayerMechanism("linear", "softmax", "past_price"),
    }
    with pytest.raises(ValueError, match="common initial K and L"):
        audit_mixed_configuration(players, mechanisms, expected_players=2)


def test_different_task_capabilities_are_rejected():
    first = firm(P1)
    tasks = list(first.tasks)
    tasks[0] = TaskCapability('T01', 2, 1, True)
    second = TaskBasedFirm(P2, 10, 10, tuple(tasks))
    mechanisms = {P1: PlayerMechanism('shared', 'optimize', 'price'), P2: PlayerMechanism('shared', 'softmax', 'price')}
    with pytest.raises(ValueError, match='common production technology'):
        audit_mixed_configuration({P1: first, P2: second}, mechanisms, expected_players=2)

def test_different_production_mechanisms_are_rejected():
    mechanisms = {P1: PlayerMechanism('linear', 'optimize', 'price'), P2: PlayerMechanism('ces', 'softmax', 'price')}
    with pytest.raises(ValueError, match='common production technology'):
        audit_mixed_configuration({P1: firm(P1), P2: firm(P2)}, mechanisms, expected_players=2)

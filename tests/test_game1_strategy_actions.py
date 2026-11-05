"""Verify that L3-L6 are executable behavior, not merely labels."""
from interfirm_abm.task_multi_action_diagnostic import configurations, action_factory, valuation, aggregate_20_tasks
from interfirm_abm.task_strategy_engine import DecisionInformation, strategy_roster
from interfirm_abm.task_economic_policy import MarketObservation


def _actions(identity):
    firm = configurations(1)["C000"][identity.strategy_id]
    info = DecisionInformation(MarketObservation(1, 2., 20.), ())
    return firm, info, action_factory(identity, firm, info)


def test_all_256_generate_four_feasible_distinct_actions():
    for identity in strategy_roster():
        firm, info, actions = _actions(identity)
        assert set(actions) == {f"effort_{i}" for i in range(4)}
        assert len({tuple((a.labor, a.capital) for a in x.allocation)
                    for x in actions.values()}) == 4
        for action in actions.values():
            firm.evaluate_allocation(list(action.allocation))
            assert all(not (a.capital > 0 and a.labor > 0) for a in action.allocation)


def test_l3_changes_resource_allocation():
    identities = [i for i in strategy_roster() if i.L4 == "eligibility"
                  and i.L5 == "competitive" and i.L6 == "optimization"]
    signatures = []
    for identity in identities:
        _, _, actions = _actions(identity)
        signatures.append(tuple((a.labor, a.capital)
                                for a in actions["effort_2"].allocation))
    assert len(set(signatures)) == 4


def test_l4_changes_automation_assignment():
    identities = [i for i in strategy_roster() if i.L3 == "capacity"
                  and i.L5 == "competitive" and i.L6 == "optimization"]
    signatures = []
    for identity in identities:
        _, _, actions = _actions(identity)
        signatures.append(tuple(a.capital > 0 for a in actions["effort_2"].allocation))
    assert len(set(signatures)) >= 2


def test_l5_changes_market_valuation_and_price_offers():
    identities = [i for i in strategy_roster() if i.L3 == "capacity"
                  and i.L4 == "eligibility" and i.L6 == "optimization"]
    values = {}
    for identity in identities:
        firm, info, actions = _actions(identity)
        action = actions["effort_2"]
        values[identity.L5] = valuation(identity, firm, info, action)
        if identity.L5 == "price":
            assert all(a.offered_price is not None for a in actions.values())
        else:
            assert all(a.offered_price is None for a in actions.values())
    assert values["cournot"] != values["competitive"]


def test_imitation_action_identifiers_shared_across_strategies():
    for identity in strategy_roster():
        _, _, actions = _actions(identity)
        assert set(actions) == {"effort_0", "effort_1", "effort_2", "effort_3"}

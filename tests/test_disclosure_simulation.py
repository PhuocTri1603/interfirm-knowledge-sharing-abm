"""Integration tests for Game 3C disclosure simulation."""

import numpy as np

from interfirm_abm.disclosure_simulation import DisclosureSimulation


def test_denied_access_cannot_use_shared_knowledge():
    simulation = DisclosureSimulation(
        n_firms=4,
        n_rounds=3,
        seed=2026,
    )

    simulation.knowledge_pool.publish(
        {
            "firm_id": 1,
            "round": 1,
            "technology": simulation.firms[0].technology,
            "accepted": True,
            "candidate_share": 0.65,
            "candidate_output": 120.0,
        },
        shared=True,
    )

    observed = simulation.available_knowledge(
        firm=simulation.firms[1],
        round_number=2,
        access_granted=False,
    )

    assert observed == []


def test_granted_access_observes_published_knowledge():
    simulation = DisclosureSimulation(
        n_firms=4,
        n_rounds=3,
        seed=2026,
    )

    simulation.knowledge_pool.publish(
        {
            "firm_id": 1,
            "round": 1,
            "technology": simulation.firms[0].technology,
            "accepted": True,
            "candidate_share": 0.65,
            "candidate_output": 120.0,
        },
        shared=True,
    )

    observed = simulation.available_knowledge(
        firm=simulation.firms[1],
        round_number=2,
        access_granted=True,
    )

    assert len(observed) == 1
    assert observed[0]["firm_id"] == 1


def test_technology_policy_filters_received_knowledge():
    simulation = DisclosureSimulation(
        n_firms=4,
        n_rounds=3,
        seed=2026,
        transfer_policy="same_technology",
    )

    recipient = simulation.firms[1]

    simulation.knowledge_pool.publish(
        {
            "firm_id": 1,
            "round": 1,
            "technology": "nonmatching_technology",
            "accepted": True,
            "candidate_share": 0.65,
            "candidate_output": 120.0,
        },
        shared=True,
    )

    observed = simulation.available_knowledge(
        firm=recipient,
        round_number=2,
        access_granted=True,
    )

    assert observed == []


def test_access_lottery_is_cached_per_firm_per_round():
    simulation = DisclosureSimulation(
        n_firms=4,
        n_rounds=3,
        seed=2026,
    )

    first = simulation.draw_access(firm_id=1, round_number=1)
    second = simulation.draw_access(firm_id=1, round_number=1)

    assert first is second
    assert len(simulation.access_log) == 1


def test_access_lottery_records_probability_and_outcome():
    simulation = DisclosureSimulation(
        n_firms=4,
        n_rounds=3,
        seed=2026,
    )

    result = simulation.draw_access(firm_id=1, round_number=1)

    assert isinstance(result, bool)
    assert len(simulation.access_log) == 1

    record = simulation.access_log[0]

    assert record["firm_id"] == 1
    assert record["round"] == 1
    assert record["access_probability"] == 0.50
    assert record["access_granted"] is result


def test_access_lottery_is_reproducible_with_same_seed():
    first_simulation = DisclosureSimulation(
        n_firms=4,
        n_rounds=3,
        seed=2026,
    )
    second_simulation = DisclosureSimulation(
        n_firms=4,
        n_rounds=3,
        seed=2026,
    )

    first_results = [
        first_simulation.draw_access(firm_id=firm_id, round_number=1)
        for firm_id in range(1, 5)
    ]

    second_results = [
        second_simulation.draw_access(firm_id=firm_id, round_number=1)
        for firm_id in range(1, 5)
    ]

    assert first_results == second_results


def test_learning_strategy_baseline_probabilities():
    simulation = DisclosureSimulation(n_firms=4, n_rounds=3)

    assert simulation.choose_learning_strategy(
        draw=0.10, shared_available=True, own_available=True
    ) == "random"

    assert simulation.choose_learning_strategy(
        draw=0.35, shared_available=True, own_available=True
    ) == "shared"

    assert simulation.choose_learning_strategy(
        draw=0.80, shared_available=True, own_available=True
    ) == "own"


def test_proportional_fallback_without_shared_knowledge():
    simulation = DisclosureSimulation(n_firms=4, n_rounds=3)

    assert simulation.choose_learning_strategy(
        draw=0.20, shared_available=False, own_available=True
    ) == "random"

    assert simulation.choose_learning_strategy(
        draw=0.30, shared_available=False, own_available=True
    ) == "own"


def test_fallback_uses_random_when_own_history_is_empty():
    simulation = DisclosureSimulation(n_firms=4, n_rounds=3)

    for draw in [0.0, 0.20, 0.50, 0.99]:
        assert simulation.choose_learning_strategy(
            draw=draw,
            shared_available=False,
            own_available=False,
        ) == "random"


def test_fallback_probability_boundary():
    simulation = DisclosureSimulation(n_firms=4, n_rounds=3)

    boundary = 2.0 / 7.0

    assert simulation.choose_learning_strategy(
        draw=boundary - 1e-9,
        shared_available=False,
        own_available=True,
    ) == "random"

    assert simulation.choose_learning_strategy(
        draw=boundary,
        shared_available=False,
        own_available=True,
    ) == "own"


def test_game3c_runs_exactly_one_experiment_per_firm_per_round():
    simulation = DisclosureSimulation(
        n_firms=4,
        n_rounds=3,
        seed=2026,
    )

    results = simulation.run()

    assert len(results) == 12

    counts = results.groupby(["firm_id", "round"]).size()

    assert len(counts) == 12
    assert (counts == 1).all()


def test_game3c_disclosure_decisions_and_selective_publication():
    simulation = DisclosureSimulation(
        n_firms=8,
        n_rounds=10,
        seed=2026,
    )

    results = simulation.run()

    assert hasattr(simulation, "disclosure_log")

    successful = results[results["accepted"] == True]

    assert len(simulation.disclosure_log) == len(successful)

    for decision in simulation.disclosure_log:
        assert isinstance(decision["shared"], bool)
        assert decision["accepted"] is True

    published = simulation.knowledge_pool.records

    assert all(record["accepted"] is True for record in published)

    shared_decisions = [
        decision
        for decision in simulation.disclosure_log
        if decision["shared"]
    ]

    assert len(published) == len(shared_decisions)

    published_keys = {
        (record["firm_id"], record["round"])
        for record in published
    }

    shared_keys = {
        (decision["firm_id"], decision["round"])
        for decision in shared_decisions
    }

    assert published_keys == shared_keys


def test_game3c_no_look_ahead_bias():
    simulation = DisclosureSimulation(
        n_firms=8,
        n_rounds=15,
        seed=2026,
    )

    simulation.run()

    published = {
        (record["firm_id"], record["round"]): record
        for record in simulation.knowledge_pool.records
    }

    for learning in simulation.learning_log:
        if learning["learning_source"] != "shared":
            continue

        recipient_round = learning["round"]
        source_id = learning["selected_peer_id"]

        assert source_id != learning["firm_id"]

        eligible_sources = [
            record
            for (firm_id, source_round), record in published.items()
            if firm_id == source_id
            and source_round < recipient_round
        ]

        assert eligible_sources, (
            "Shared learning must use previously published knowledge."
        )

    for access in simulation.access_log:
        firm_id = access["firm_id"]
        round_number = access["round"]

        prior_decisions = [
            decision
            for decision in simulation.disclosure_log
            if decision["firm_id"] == firm_id
            and max(1, round_number - 5)
                <= decision["round"] < round_number
        ]

        n = len(prior_decisions)
        s = sum(decision["shared"] for decision in prior_decisions)

        expected_reputation = (1.0 + s) / (2.0 + n)
        expected_probability = 0.10 + 0.80 * expected_reputation

        assert abs(
            access["reputation"] - expected_reputation
        ) < 1e-12

        assert abs(
            access["access_probability"] - expected_probability
        ) < 1e-12


def test_game3c_delayed_rewards_mature_after_five_rounds():
    simulation = DisclosureSimulation(
        n_firms=8,
        n_rounds=15,
        seed=2026,
    )

    simulation.run()

    decisions = {
        (decision["firm_id"], decision["round"])
        for decision in simulation.disclosure_log
    }

    matured = {
        (reward["firm_id"], reward["round"])
        for reward in simulation.reward_log
    }

    expected_matured = {
        (firm_id, decision_round)
        for firm_id, decision_round in decisions
        if decision_round + 5 <= simulation.n_rounds
    }

    assert matured == expected_matured
    assert len(simulation.reward_log) == len(matured)

    for reward in simulation.reward_log:
        assert reward["evaluation_round"] == reward["round"] + 5

    for firm_id, learner in simulation.disclosure_learners.items():
        expected_pending = {
            decision_round
            for decision_firm, decision_round in decisions
            if decision_firm == firm_id
            and decision_round + 5 > simulation.n_rounds
        }

        actual_pending = {
            decision["round"]
            for decision in learner.pending_decisions
        }

        assert actual_pending == expected_pending


def test_game3c_reward_formula_matches_realized_shared_gains():
    simulation = DisclosureSimulation(
        n_firms=8,
        n_rounds=15,
        seed=2026,
    )

    results = simulation.run()

    outputs = {
        (row.firm_id, row.round): row.current_output
        for row in results.itertuples(index=False)
    }

    decisions = {
        (decision["firm_id"], decision["round"]): decision
        for decision in simulation.disclosure_log
    }

    for reward in simulation.reward_log:
        firm_id = reward["firm_id"]
        t = reward["round"]

        baseline = outputs[(firm_id, t)]

        learner = simulation.disclosure_learners[firm_id]

        discounted_gain = sum(
            0.95 ** (k - 1)
            * learner.shared_gains.get(t + k, 0.0)
            for k in range(1, 6)
        )

        shared = decisions[(firm_id, t)]["shared"]

        expected_reward = (
            discounted_gain / baseline
            - (0.005 if shared else 0.0)
        )

        assert abs(
            reward["reward"] - expected_reward
        ) < 1e-10


def test_game3c_q_values_match_sequential_reward_updates():
    simulation = DisclosureSimulation(
        n_firms=8,
        n_rounds=15,
        seed=2026,
    )

    simulation.run()

    for firm in simulation.firms:
        firm_id = firm.firm_id

        q_share = 0.0
        q_withhold = 0.0

        rewards = sorted(
            (
                reward
                for reward in simulation.reward_log
                if reward["firm_id"] == firm_id
            ),
            key=lambda reward: reward["evaluation_round"],
        )

        for reward in rewards:
            if reward["shared"]:
                q_share += 0.30 * (
                    reward["reward"] - q_share
                )
            else:
                q_withhold += 0.30 * (
                    reward["reward"] - q_withhold
                )

        learner = simulation.disclosure_learners[firm_id]

        assert abs(learner.q_share - q_share) < 1e-12
        assert abs(learner.q_withhold - q_withhold) < 1e-12


def test_game3c_shared_gains_match_actual_output_improvements():
    simulation = DisclosureSimulation(
        n_firms=8,
        n_rounds=15,
        seed=2026,
    )

    results = simulation.run()

    learning_sources = {
        (entry["firm_id"], entry["round"]): entry["learning_source"]
        for entry in simulation.learning_log
    }

    for firm in simulation.firms:
        firm_id = firm.firm_id

        firm_results = (
            results[results["firm_id"] == firm_id]
            .sort_values("round")
        )

        expected_gains = {}
        previous_output = None

        for row in firm_results.itertuples(index=False):
            if previous_output is not None:
                gain = max(
                    0.0,
                    float(row.current_output) - previous_output,
                )

                if learning_sources[(firm_id, row.round)] == "shared":
                    expected_gains[row.round] = gain

            previous_output = float(row.current_output)

        learner = simulation.disclosure_learners[firm_id]

        assert set(learner.shared_gains) == set(expected_gains)

        for round_number, expected_gain in expected_gains.items():
            assert abs(
                learner.shared_gains[round_number] - expected_gain
            ) < 1e-10


def test_game3c_accepts_configurable_disclosure_parameters():
    simulation = DisclosureSimulation(
        n_firms=4,
        n_rounds=3,
        seed=2026,
        disclosure_cost_rate=0.01,
        learning_rate=0.50,
        temperature=0.02,
    )

    assert simulation.disclosure_cost_rate == 0.01

    for learner in simulation.disclosure_learners.values():
        assert learner.learning_rate == 0.50
        assert learner.temperature == 0.02


def test_game3c_rejects_invalid_disclosure_parameters():
    import pytest

    invalid_parameters = [
        {"disclosure_cost_rate": -0.01},
        {"learning_rate": 0.0},
        {"learning_rate": 1.5},
        {"temperature": 0.0},
        {"temperature": -0.01},
    ]

    for parameters in invalid_parameters:
        with pytest.raises(ValueError):
            DisclosureSimulation(
                n_firms=4,
                n_rounds=3,
                **parameters,
            )


def test_game3c_disclosure_cost_changes_reward():
    low_cost = DisclosureSimulation(
        n_firms=8,
        n_rounds=15,
        seed=2026,
        disclosure_cost_rate=0.0,
    )

    high_cost = DisclosureSimulation(
        n_firms=8,
        n_rounds=15,
        seed=2026,
        disclosure_cost_rate=0.02,
    )

    low_cost.run()
    high_cost.run()

    low_rewards = {
        reward["firm_id"]: reward
        for reward in low_cost.reward_log
        if reward["evaluation_round"] == min(
            r["evaluation_round"]
            for r in low_cost.reward_log
            if r["firm_id"] == reward["firm_id"]
        )
    }

    high_rewards = {
        reward["firm_id"]: reward
        for reward in high_cost.reward_log
        if reward["evaluation_round"] == min(
            r["evaluation_round"]
            for r in high_cost.reward_log
            if r["firm_id"] == reward["firm_id"]
        )
    }

    assert low_rewards.keys() == high_rewards.keys()
    assert low_rewards, "Expected at least one matured reward"

    for firm_id in low_rewards:
        low = low_rewards[firm_id]
        high = high_rewards[firm_id]

        assert low["round"] == high["round"]
        assert low["shared"] == high["shared"]

        expected_difference = -0.02 if low["shared"] else 0.0

        assert abs(
            (high["reward"] - low["reward"]) - expected_difference
        ) < 1e-10


def test_game3c_ablation_accepts_mechanism_switches():
    simulation = DisclosureSimulation(
        n_firms=8,
        n_rounds=10,
        seed=2026,
        selective_disclosure=False,
        conditional_reciprocity=False,
    )

    assert simulation.selective_disclosure is False
    assert simulation.conditional_reciprocity is False


def test_game3c_open_sharing_publishes_all_successes():
    simulation = DisclosureSimulation(
        n_firms=8,
        n_rounds=15,
        seed=2026,
        selective_disclosure=False,
        conditional_reciprocity=False,
    )

    results = simulation.run()

    accepted = int(results["accepted"].sum())

    assert len(simulation.knowledge_pool.records) == accepted
    assert all(
        record["accepted"]
        for record in simulation.knowledge_pool.records
    )

    assert all(
        entry["access_granted"]
        for entry in simulation.access_log
    )

    assert simulation.reward_log == []


def test_game3c_reciprocity_off_grants_all_access():
    simulation = DisclosureSimulation(
        n_firms=8,
        n_rounds=15,
        seed=2026,
        selective_disclosure=True,
        conditional_reciprocity=False,
    )

    simulation.run()

    assert len(simulation.access_log) == 8 * 15
    assert all(
        entry["access_granted"]
        for entry in simulation.access_log
    )


def test_game3c_disclosure_off_publishes_all_successes():
    simulation = DisclosureSimulation(
        n_firms=8,
        n_rounds=15,
        seed=2026,
        selective_disclosure=False,
        conditional_reciprocity=True,
    )

    results = simulation.run()

    assert len(simulation.knowledge_pool.records) == int(
        results["accepted"].sum()
    )
    assert simulation.reward_log == []

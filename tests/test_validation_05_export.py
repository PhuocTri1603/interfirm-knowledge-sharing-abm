"""Smoke tests for Game 1 Validation 05 export contract."""

import json

import pandas as pd

from experiments.validation_05 import export_results


def test_export_results_writes_expected_files(tmp_path):
    paired = pd.DataFrame(
        [
            {
                "seed": 2026,
                "round": 5,
                "firm_id": 1,
                "technology": "Cobb-Douglas",
                "random": 50.0,
                "guided": 52.0,
                "advantage_pct": 4.0,
            },
            {
                "seed": 2026,
                "round": 5,
                "firm_id": 2,
                "technology": "Leontief",
                "random": 40.0,
                "guided": 40.0,
                "advantage_pct": 0.0,
            },
        ]
    )
    export_results(paired, tmp_path)

    expected = {
        "paired_observations.csv",
        "seed_round_summary.csv",
        "summary_by_round.json",
        "metadata.json",
    }
    assert expected.issubset({p.name for p in tmp_path.iterdir()})

    observed = pd.read_csv(tmp_path / "paired_observations.csv")
    assert len(observed) == 2
    assert observed["advantage_pct"].tolist() == [4.0, 0.0]

    seed_round = pd.read_csv(tmp_path / "seed_round_summary.csv")
    assert len(seed_round) == 1
    assert seed_round.loc[0, "mean_advantage_pct"] == 2.0

    summary = json.loads((tmp_path / "summary_by_round.json").read_text())
    assert len(summary) == 1
    assert summary[0]["round"] == 5
    assert summary[0]["mean_advantage_pct"] == 2.0

    metadata = json.loads((tmp_path / "metadata.json").read_text())
    assert metadata["observed_paired_rows"] == 2
    assert metadata["expected_paired_rows"] == 40000
    assert metadata["matched_randomness"] is True


def test_100_firm_baseline_smoke():
    from interfirm_abm.simulation import Simulation

    for policy in ("random", "guided"):
        sim = Simulation(n_firms=100, n_rounds=1, seed=2026,
                         learning_policy=policy, matched_randomness=True)
        assert len(sim.firms) == 100
        assert all(f.capital_share == 0.50 and f.budget == 100.0
                   for f in sim.firms)
        technologies = pd.Series([f.technology for f in sim.firms]).value_counts()
        assert len(technologies) == 4
        assert (technologies == 25).all()
        history = sim.run()
        assert len(history) == 100
        assert history["firm_id"].nunique() == 100
        assert (history["round"] == 1).all()
        assert history["current_output"].notna().all()

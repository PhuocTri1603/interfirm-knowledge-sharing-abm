from pathlib import Path

import pytest

from interfirm_abm.task_initial_profile_bridge import load_initial_economic_profiles


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "firms" / "firm_profiles_100.csv"


def test_original_100_firms_are_100_configuration_profiles():
    profiles = load_initial_economic_profiles(SOURCE)
    assert len(profiles) == 100
    assert len({p.configuration_id for p in profiles}) == 100
    assert profiles[0].configuration_id == "profile_001"
    assert profiles[0].source_firm_id == 1
    assert profiles[0].technology == "Cobb-Douglas"
    assert profiles[0].capital_endowment == pytest.approx(87.5660197111)
    assert profiles[0].labor_endowment == pytest.approx(52.5663904846)
    assert profiles[3].technology == "CES"
    assert profiles[3].rho == pytest.approx(0.3862433252)
    assert all(p.profile_status == "illustrative_unapproved" for p in profiles)


def test_rejects_missing_source_profile(tmp_path):
    lines = SOURCE.read_text().splitlines()
    file = tmp_path / "incomplete.csv"
    file.write_text("\n".join(lines[:-1]) + "\n")
    with pytest.raises(ValueError, match="100 original firm profiles"):
        load_initial_economic_profiles(file)

"""Read the canonical approved population without producing economic results."""
from pathlib import Path

from interfirm_abm.task_based_firm import load_approved_population


ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / "data/firms/task_based_100_firms_profiles.csv"
TASKS = ROOT / "data/firms/task_based_100_firms_tasks.csv"


def test_canonical_population_loads():
    firms = load_approved_population(PROFILES, TASKS)
    assert len(firms) == 100
    assert len({firm.firm_id for firm in firms}) == 100
    assert all(len(firm.tasks) == 20 for firm in firms)
    assert sum(len(firm.tasks) for firm in firms) == 2000
    assert all(firm.capital_endowment >= 0 for firm in firms)
    assert all(firm.labor_endowment >= 0 for firm in firms)

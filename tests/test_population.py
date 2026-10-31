"""Tests for the researcher's balanced heterogeneous population."""
import numpy as np
import pandas as pd
import pytest

from interfirm_abm.population import generate_population, TECHNOLOGIES, QUOTAS, STRATA


def test_exact_population_and_technology_quotas():
    p = generate_population(2026)
    assert len(p) == 100
    assert p.firm_id.is_unique
    assert sorted(p.firm_id.tolist()) == list(range(1, 101))
    assert p.technology.value_counts().to_dict() == {t: 25 for t in TECHNOLOGIES}
    for technology, quotas in zip(TECHNOLOGIES, QUOTAS):
        subset = p[p.technology == technology]
        for (stratum, low, high), quota in zip(STRATA, quotas):
            s = subset[subset.stratum == stratum]
            assert len(s) == quota
            assert s.alpha.between(low, high, inclusive="neither").all()


def test_exact_orientation_balance():
    p = generate_population(2026)
    assert int((p.alpha < 0.5).sum()) == 50
    assert int((p.alpha > 0.5).sum()) == 50
    assert not (p.alpha == 0.5).any()


def test_fixed_productivity_and_reproducibility():
    p = generate_population(2026)
    pd.testing.assert_frame_equal(p, generate_population(2026))
    assert p.A.eq(1.0).all()
    assert p.budget.eq(100.0).all()
    assert p.initial_capital_share.eq(0.5).all()
    assert p[p.technology == "CES"].rho.eq(-0.5).all()
    assert p[p.technology != "CES"].rho.isna().all()
    assert not np.array_equal(p.alpha.to_numpy(), generate_population(2027).alpha.to_numpy())


@pytest.mark.parametrize("seed", [-1, 1.5, "2026"])
def test_invalid_seed(seed):
    with pytest.raises(ValueError):
        generate_population(seed)

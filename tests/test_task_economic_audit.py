from interfirm_abm.task_layer_registry import iter_strategies
from interfirm_abm.task_economic_audit import audit_strategy, catalog_audit_summary, REQUIRED
import pytest


def test_no_nominal_strategy_is_removed_or_automatically_approved():
    summary = catalog_audit_summary()
    assert summary["nominal_cells"] == 12288
    assert summary["specify_clone_count_and_market_size"] == 3072


def test_default_specification_is_unresolved():
    record = next(iter_strategies())
    audit = audit_strategy(record)
    assert audit.status == "requires_research_review"
    assert audit.missing == REQUIRED


def test_cross_layer_flags_are_conditional():
    record = next(s for s in iter_strategies() if dict(s.choices)["L1"] == "ces"
                  and dict(s.choices)["L2"] == "ces"
                  and dict(s.choices)["L5"] == "cournot"
                  and dict(s.choices)["L6"] == "softmax")
    flags = audit_strategy(record).review_flags
    assert "distinguish_within_and_across_task_elasticities" in flags
    assert "distinguish_learning_from_cournot_equilibrium" in flags


def test_even_documented_specs_require_research_review():
    record = next(iter_strategies())
    result = audit_strategy(record, REQUIRED)
    assert result.missing == ()
    assert result.status == "requires_research_review"


def test_unknown_approval_key_rejected():
    with pytest.raises(ValueError):
        audit_strategy(next(iter_strategies()), ("not_a_real_key",))

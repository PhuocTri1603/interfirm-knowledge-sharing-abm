import pytest
from interfirm_abm.task_technology_review import (
    REQUIRED, iter_technology_reviews, review_technology,
)


def test_twelve_unique_cells_retained():
    rows = tuple(iter_technology_reviews())
    assert len(rows) == 12
    assert len({row.cell_id for row in rows}) == 12
    assert all(row.status == "requires_research_review" for row in rows)


def test_leontief_eligibility_conflict_is_review_not_exclusion():
    row = review_technology("leontief", "linear")
    assert "review_joint_input_requirement_vs_automation_eligibility" in row.flags
    assert row.unresolved == REQUIRED


def test_two_ces_elasticities_not_conflated():
    row = review_technology("ces", "ces")
    assert "keep_within_task_and_cross_task_elasticities_distinct" in row.flags


def test_leontief_aggregator_requires_task_essentiality_review():
    assert "review_all_tasks_essential_and_positive_requirements" in review_technology(
        "assignment", "leontief"
    ).flags


def test_fully_specified_still_requires_research_approval():
    row = review_technology("assignment", "linear", REQUIRED)
    assert not row.unresolved
    assert row.status == "requires_research_review"


def test_unknown_inputs_rejected():
    with pytest.raises(ValueError):
        review_technology("cobb_douglas", "linear")
    with pytest.raises(ValueError):
        review_technology("ces", "linear", ("unsupported",))

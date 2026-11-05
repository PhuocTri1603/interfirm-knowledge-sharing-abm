from interfirm_abm.task_strategy_audit import audit_strategy_semantics


def test_audit_reports_unresolved_semantics():
    result = audit_strategy_semantics()
    assert result['strategy_count'] == 256
    assert result['semantic_conflict_count'] == 16
    assert result['ready_for_scientific_comparison'] is False
    assert all(item['resolution_status'] == 'requires_researcher_decision' for item in result['conflicts'])

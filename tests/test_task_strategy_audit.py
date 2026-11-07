from interfirm_abm.task_strategy_audit import audit_strategy_semantics


def test_audit_reports_unresolved_semantics():
    result = audit_strategy_semantics()
    assert result['strategy_count'] == 256
    assert result['semantic_conflict_count'] == 0
    assert result['ready_for_scientific_comparison'] is True
    assert result['resolved_adaptive_imitation_count'] == 16
    assert all(item['mechanism'] == 'self_imitation_from_own_completed_realized_payoffs' for item in result['resolved'])

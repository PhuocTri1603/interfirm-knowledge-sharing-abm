from interfirm_abm.task_layer_registry import LAYERS, ANALYSIS_LENSES, iter_strategies, iter_reporting_keys


def test_strategy_count():
    records = list(iter_strategies())
    assert len(records) == 12288
    assert len({r.strategy_id for r in records}) == 12288
    assert all(len(r.choices) == 7 for r in records)
    assert all(r.specification_status == 'not_yet_specified' for r in records)


def test_reporting_count():
    keys = list(iter_reporting_keys())
    assert len(ANALYSIS_LENSES) == 4
    assert len(keys) == 49152
    assert len(set(keys)) == 49152
    assert len({key[0] for key in keys}) == 12288

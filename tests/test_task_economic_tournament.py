from interfirm_abm.task_economic_tournament import run_economic_sequential

def test_empty_configurations_rejected():
    try:
        run_economic_sequential((), {}, 200)
    except ValueError:
        return
    raise AssertionError('Expected ValueError')

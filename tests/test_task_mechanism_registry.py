import pytest
from interfirm_abm.task_layer_registry import LAYERS
from interfirm_abm.task_mechanism_registry import MechanismSpecification, audit_mechanism_registry


def test_registry_requires_all_options():
    with pytest.raises(ValueError, match='coverage mismatch'):
        audit_mechanism_registry({})


def test_registry_requires_validation():
    specs = {}
    for layer, options in LAYERS:
        if layer == 'L7':
            continue
        for option in options:
            specs[(layer, option)] = MechanismSpecification(layer, option, 'Economic mechanism', 'Literature source', 'implementation.py', 'test_implementation.py')
    result = audit_mechanism_registry(specs)
    assert result['required_options'] == 23
    assert not result['research_ready']
    with pytest.raises(ValueError, match='must be validated'):
        audit_mechanism_registry(specs, require_validated=True)

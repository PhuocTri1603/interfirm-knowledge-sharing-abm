"""Auditable L1-L6 mechanism specification registry.

A strategy label is not an executable economic mechanism. This module
records explicit provenance and requires option-level coverage before a
full mixed-market run may be called research-ready.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from interfirm_abm.task_layer_registry import LAYERS


@dataclass(frozen=True)
class MechanismSpecification:
    layer: str
    option: str
    economic_definition: str
    literature_reference: str
    implementation_module: str
    verification_test: str
    status: str = "proposed"

    def __post_init__(self):
        if self.status not in ("proposed", "implemented", "validated"):
            raise ValueError("invalid mechanism status")
        if not all((self.economic_definition.strip(), self.literature_reference.strip(),
                    self.implementation_module.strip(), self.verification_test.strip())):
            raise ValueError("mechanism definition, source, implementation and test required")


def audit_mechanism_registry(
    specifications: Mapping[tuple[str, str], MechanismSpecification],
    *,
    require_validated: bool = False,
) -> dict:
    expected = {(layer, option) for layer, options in LAYERS if layer in ("L3", "L4", "L5", "L6")
                for option in options}
    if set(specifications) != expected:
        missing = sorted(expected - set(specifications))
        extra = sorted(set(specifications) - expected)
        raise ValueError(f"L3-L6 mechanism coverage mismatch: missing={missing}; extra={extra}")
    for key, spec in specifications.items():
        if (spec.layer, spec.option) != key:
            raise ValueError("registry key does not match mechanism identity")
    counts = {status: sum(s.status == status for s in specifications.values())
              for status in ("proposed", "implemented", "validated")}
    if require_validated and counts["validated"] != len(expected):
        raise ValueError("all L3-L6 mechanisms must be validated before research-ready execution")
    return {
        "required_options": len(expected),
        "status_counts": counts,
        "research_ready": counts["validated"] == len(expected),
    }

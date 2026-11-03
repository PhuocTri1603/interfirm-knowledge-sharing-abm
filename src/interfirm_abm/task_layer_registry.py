"""Data-only approved strategy-layer catalog; no simulations."""
from dataclasses import dataclass
from itertools import product

LAYERS = (
 ("L1", ("assignment", "ces", "leontief", "hybrid")),
 ("L2", ("linear", "leontief", "ces")),
 ("L3", ("flexible", "capacity", "adjustment", "investment")),
 ("L4", ("eligibility", "efficiency", "adoption_cost", "combined")),
 ("L5", ("competitive", "cournot", "price", "adaptive")),
 ("L6", ("optimization", "trial_error", "softmax", "imitation")),
 ("L7", ("separate", "mixed", "clones", "stratified")),
)
ANALYSIS_LENSES = ("firm", "market", "welfare", "learning")
CATALOG_VERSION = "2026-11-03-approved-scope"

@dataclass(frozen=True)
class StrategyRecord:
    strategy_id: str
    choices: tuple[tuple[str, str], ...]
    specification_status: str = "not_yet_specified"
    catalog_version: str = CATALOG_VERSION

def iter_strategies():
    for combination in product(*(options for _, options in LAYERS)):
        choices = tuple((layer, option) for (layer, _), option in zip(LAYERS, combination))
        yield StrategyRecord("|".join(f"{layer}={option}" for layer, option in choices), choices)

def iter_reporting_keys():
    for record in iter_strategies():
        for lens in ANALYSIS_LENSES:
            yield (record.strategy_id, lens)

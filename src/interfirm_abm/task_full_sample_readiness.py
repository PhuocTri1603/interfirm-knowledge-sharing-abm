"""Fail-closed readiness audit for the agreed 100-profile × 256-player Game 1.

Never represent catalog labels as executable economic policies.
"""
from __future__ import annotations

import json
from pathlib import Path
from interfirm_abm.task_experiment_dimensions import strategy_player_ids
from interfirm_abm.task_initial_profile_bridge import load_initial_economic_profiles

def audit_full_sample(profile_csv: str | Path) -> dict:
    profiles = load_initial_economic_profiles(profile_csv)
    ids = strategy_player_ids()
    # Only two separate mechanisms have been implemented as a controlled experiment;
    # neither implements all the L3/L4/L5 choices in the 256-label catalog.
    return {
        "status": "blocked_not_full_sample_research_experiment",
        "initial_profiles_loaded": len(profiles),
        "profiles_approved": sum(p.profile_status != "illustrative_unapproved" for p in profiles),
        "distinct_technologies": sorted({p.technology for p in profiles}),
        "strategy_catalog_labels": len(ids),
        "fully_specified_executable_catalog_strategies": 0,
        "rounds_per_market": 200,
        "planned_player_rounds": len(profiles) * len(ids) * 200,
        "blocking_requirements": [
            "Researcher approval of 100 illustrative source profiles",
            "Researcher-approved mapping from Cobb-Douglas/Leontief/Linear/CES to task production (or direct production evaluation)",
            "Executable, economically distinct policies for L3/L4/L5/L6 rather than label aliases",
            "Researcher-approved common inverse demand and input costs",
            "Researcher-approved semantics of L7 market-design regimes",
        ],
        "warning": "Do not publish a 256-strategy ranking: the catalog is not 256 implemented behaviors.",
    }

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("profiles", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = audit_full_sample(args.profiles)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()

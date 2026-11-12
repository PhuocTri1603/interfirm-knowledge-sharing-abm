"""Section 3.2 evidence safeguards: no invented mechanism data."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from analyze_paper_section3_2 import A,B,REQUIRED,UNOBSERVED,describe

def test_paired_statistical_definition():
    v=np.arange(100,dtype=float)-49.5
    z=describe(v,"A_minus_B",.5)
    assert z["n"]==100 and z["positive"]==50 and z["negative"]==50
    assert z["tied"]==0 and z["mean"]==pytest.approx(0)
    assert z["descriptive95_lower"]<0<z["descriptive95_upper"]

def test_no_cost_components_or_task_activity_in_original_archive():
    assert "variable_cost" in UNOBSERVED and "task_activity" in UNOBSERVED
    assert "capital_used" in UNOBSERVED and "labor_used" in UNOBSERVED
    assert "profit" in REQUIRED and "active_ai_count" in REQUIRED

def test_focal_policy_identity():
    assert A=="L3=cost_adjusted|L4=profit_based"
    assert B=="L3=productivity|L4=profit_based"

def test_output_validation_when_available():
    out=Path("results/paper/section3")
    if not (out/"section3_2_validation.json").exists():
        pytest.skip("Evidence job validates archived data")
    import json
    z=json.loads((out/"section3_2_validation.json").read_text())
    assert z["observations"]==540000 and z["matched_profiles"]==100
    assert z["max_section3_1_baseline_mean_residual"]<1e-7
    assert z["research_validated"] is False
    assert z["independent_component_cost_reconciliation"] is False
    d=pd.read_csv(out/"section3_2_pairwise.csv")
    assert len(d)==6 and d.n.eq(100).all()
    assert d[["mean","median","sd"]].notna().all().all()
    assert (d.positive+d.negative+d.tied).eq(100).all()

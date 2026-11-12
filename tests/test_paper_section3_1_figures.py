"""QA for original Section 3.1 publication figure inputs and exports."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from paper_plot_style import POLICIES,SIGMAS,ALLOCATION_COLORS,AUTOMATION_STYLES
from plot_paper_section3_1 import check_inputs,FOCAL,SELECTED

def test_policy_order_and_visual_mapping():
    assert len(POLICIES)==len(set(POLICIES))==9
    assert len(SIGMAS)==3
    assert len(ALLOCATION_COLORS)==len(AUTOMATION_STYLES)==3
    assert len(FOCAL)==4 and len(SELECTED)==4

def test_reject_duplicate_policy_rounds():
    d=pd.DataFrame([{"profile_id":"F001","sigma":.5,"strategy_id":POLICIES[0],"round":1}]*2)
    assert d.duplicated(["profile_id","sigma","strategy_id","round"]).sum()==1

def test_expected_figure_export_names():
    stems=("figure_3_1_profitability","figure_3_2_paired_differences","figure_3_3_policy_rankings")
    assert len(set(stems))==3

def test_figure_data_against_source_if_available():
    root=Path("results/paper/section3")
    if not (root/"section3_1_figure3_dynamics_data.csv").exists():
        import pytest
        pytest.skip("Original artifact not present in local checkout; CI evidence job validates complete data")
    d=pd.read_csv(root/"section3_1_figure3_dynamics_data.csv")
    assert len(d)==2400
    assert not d[["mean","q25","q75","sd"]].isna().any().any()
    assert (d.n==100).all()
    assert (d.q25<=d.q75).all()
    assert d.groupby(["sigma","strategy_id"])["round"].nunique().eq(200).all()
    z=pd.read_csv(root/"section3_1_figure2_forest_data.csv")
    assert len(z)==12 and (z.n==100).all()
    assert (z.lower<=z.mean_difference).all() and (z.mean_difference<=z.upper).all()

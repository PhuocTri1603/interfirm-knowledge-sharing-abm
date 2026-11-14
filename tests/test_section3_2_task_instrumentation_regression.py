"""Regression: opt-in task instrumentation must not alter the economic trajectory."""
import pytest
from interfirm_abm.task_a6_market import approved_profiles
from interfirm_abm.game1_nine_strategy import run_game1
from scripts.reproduce_paper_section3_2 import params

@pytest.mark.parametrize("sigma",[0.5,1.0,2.0])
def test_task_audit_is_observational(sigma):
    firm=approved_profiles()[0]
    baseline=run_game1(firm,sigma,params(),rounds=2,audit=False)
    tasks=[]
    audited=run_game1(firm,sigma,params(),rounds=2,audit=True,task_audit=tasks)
    assert baseline["players"]==[{k:v for k,v in r.items() if k in baseline["players"][0]} for r in audited["players"]]
    assert baseline["market"]==audited["market"]
    assert baseline["ranking"]==audited["ranking"]
    assert len(tasks)==2*9*20
    for r in audited["players"]:
        rows=[x for x in tasks if x["round"]==r["round"] and x["strategy_id"]==r["strategy_id"]]
        assert len(rows)==20
        assert sum(x["labor_allocation"] for x in rows)==pytest.approx(r["labor_used"],abs=1e-8)
        assert sum(x["capital_allocation"] for x in rows)==pytest.approx(r["capital_used"],abs=1e-8)
        assert sum(x["actual_ai_use"] for x in rows)==r["active_ai_count"]
        assert r["profit"]==pytest.approx(r["revenue"]-r["variable_cost"]-r["adjustment_cost"]-r["adoption_cost"],abs=1e-8)

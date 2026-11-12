"""Section 3.2 archived-evidence-only audit. No simulation or economic-model changes.

Original run 42463803820, commit c614b86d9192a57fb402b4772b3c3bb6bf80b79f.
Unobserved component costs and task allocations are NOT reconstructed from profit.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from paper_plot_style import apply_style,save_figure,ALLOCATION_COLORS,SIGMAS

A="L3=cost_adjusted|L4=profit_based"
B="L3=productivity|L4=profit_based"
POLICIES=(A,B)
SOURCE_COMMIT="c614b86d9192a57fb402b4772b3c3bb6bf80b79f"
REQUIRED=("profile_id","sigma","round","strategy_id","action","output","price",
          "profit","cumulative_profit","adopted_count","active_ai_count")
UNOBSERVED=("task_activity","task_labor","task_capital","capital_used","labor_used",
            "variable_cost","adjustment_cost","adoption_cost","eligible_tasks",
            "task_mode_switches","capacity_utilization")
TOL=1e-8

def describe(values,kind,sigma):
    x=np.asarray(values,dtype=float)
    assert len(x)==100 and np.isfinite(x).all()
    sd=float(x.std(ddof=1))
    return dict(contrast=kind,sigma=sigma,n=100,mean=float(x.mean()),
                median=float(np.median(x)),sd=sd,p25=float(np.quantile(x,.25)),
                p75=float(np.quantile(x,.75)),minimum=float(x.min()),
                maximum=float(x.max()),positive=int((x>TOL).sum()),
                negative=int((x< -TOL).sum()),tied=int((abs(x)<=TOL).sum()),
                descriptive95_lower=float(x.mean()-1.96*sd/10),
                descriptive95_upper=float(x.mean()+1.96*sd/10))

def audit(d,summary31):
    assert set(REQUIRED).issubset(d.columns)
    assert len(d)==540000 and d.duplicated(["profile_id","sigma","strategy_id","round"]).sum()==0
    assert set(d.sigma)==set(SIGMAS) and d.profile_id.nunique()==100
    assert d.groupby(["profile_id","sigma","strategy_id"]).size().eq(200).all()
    assert not d[list(REQUIRED)].isna().any().any()
    # Only archived quantities, no inferred cost components.
    x=d[d.strategy_id.isin(POLICIES)].copy()
    assert len(x)==120000
    x["revenue"]=x.output*x.price
    x["implied_total_cost"]=x.revenue-x.profit
    x["shutdown"]=(x.action=="shutdown").astype(int)
    x["ai_task_share"]=x.active_ai_count/20.
    x["ever_adopted_share"]=x.adopted_count/20.
    x["capacity_action_budget"]=x.action.map({"shutdown":0.,"b1":.30,"b2":.48,"b3":.66,"b4":.84})
    assert x.capacity_action_budget.notna().all()
    # Do not describe implied_total_cost as independent component-level cost measurement.
    per=x.groupby(["profile_id","sigma","strategy_id"],as_index=False).agg(
        cumulative_profit=("profit","sum"),terminal_cumulative_profit=("cumulative_profit","last"),
        mean_output=("output","mean"),mean_price=("price","mean"),
        mean_revenue=("revenue","mean"),mean_implied_total_cost=("implied_total_cost","mean"),
        mean_active_ai_tasks=("active_ai_count","mean"),mean_ai_task_share=("ai_task_share","mean"),
        mean_ever_adopted_share=("ever_adopted_share","mean"),
        mean_action_budget=("capacity_action_budget","mean"),
        shutdown_share=("shutdown","mean"))
    assert len(per)==600
    max_terminal=float((per.cumulative_profit-per.terminal_cumulative_profit).abs().max())
    assert max_terminal<1e-7
    baseline=summary31.set_index(["sigma","strategy_id"]).mean_cumulative_profit
    observed=per.groupby(["sigma","strategy_id"]).cumulative_profit.mean()
    max_baseline=float((baseline.loc[observed.index]-observed).abs().max())
    assert max_baseline<1e-7
    # Same 100 profile IDs across each sigma: paired scenario design.
    profiles=[set(per[per.sigma==s].profile_id) for s in SIGMAS]
    assert all(v==profiles[0] for v in profiles)
    # No same-sigma technology parameters changed by the sigma aggregator itself.
    wide=per.pivot(index=["profile_id","sigma"],columns="strategy_id",values="cumulative_profit")
    dif=(wide[A]-wide[B]).unstack("sigma").loc[:,list(SIGMAS)]
    assert dif.shape==(100,3) and not dif.isna().any().any()
    pairs=[describe(dif[s].values,"A_minus_B",s) for s in SIGMAS]
    for s,t in ((.5,1.),(1.,2.),(.5,2.)):
        pairs.append(describe((dif[t]-dif[s]).values,f"D_{t:g}_minus_D_{s:g}",t))
    pairs=pd.DataFrame(pairs)
    means=per.groupby(["sigma","strategy_id"],as_index=False).agg(
        n_profiles=("profile_id","nunique"),
        mean_cumulative_profit=("cumulative_profit","mean"),
        median_cumulative_profit=("cumulative_profit","median"),
        sd_cumulative_profit=("cumulative_profit","std"),
        mean_output=("mean_output","mean"),mean_price=("mean_price","mean"),
        mean_revenue=("mean_revenue","mean"),
        mean_implied_total_cost=("mean_implied_total_cost","mean"),
        mean_active_ai_tasks=("mean_active_ai_tasks","mean"),
        mean_ai_task_share=("mean_ai_task_share","mean"),
        mean_ever_adopted_share=("mean_ever_adopted_share","mean"),
        mean_action_budget=("mean_action_budget","mean"),
        mean_shutdown_share=("shutdown_share","mean"))
    checks=dict(original_run=42463803820,original_commit=SOURCE_COMMIT,
        source="archived round CSV; no rerun",observations=len(d),
        focal_observations=len(x),profile_sigma_policy_trajectories=len(per),
        matched_profiles=100,profile_ids_consistent_across_sigma=True,
        max_terminal_cumulative_profit_residual=max_terminal,
        max_section3_1_baseline_mean_residual=max_baseline,
        revenue_identity_max_error=float((x.revenue-x.price*x.output).abs().max()),
        implied_cost_identity_max_error=float((x.profit-(x.revenue-x.implied_total_cost)).abs().max()),
        independent_component_cost_reconciliation=False,
        task_allocation_observed=False,capital_labor_observed=False,
        eligible_task_count_observed=False,unobserved_fields=list(UNOBSERVED),
        exact_sigma_comparability="same fixed task profile and reference; CES sigma changes; endogenous choices and prices also change",
        research_validated=False)
    return x,per,means,pairs,checks

def figures(per,means,out):
    apply_style()
    # Figure 3.4: actual output, profit, and algebraically implied cost with transparent qualification.
    fig,axs=plt.subplots(1,3,figsize=(7.05,2.75),layout="constrained")
    metrics=(("mean_output","Mean output per round, $q$"),
             ("mean_implied_total_cost","Mean implied cost per round"),
             ("mean_cumulative_profit","Cumulative profit, $\Pi$"))
    for j,(metric,label) in enumerate(metrics):
        ax=axs[j]
        for policy,offset in ((A,-.09),(B,.09)):
            z=means[means.strategy_id==policy].set_index("sigma").loc[list(SIGMAS)]
            ax.plot(np.arange(3)+offset,z[metric],marker="o",markersize=4,
                    color=ALLOCATION_COLORS["cost_adjusted" if policy==A else "productivity"],
                    label="Cost-adjusted" if policy==A else "Productivity")
        ax.set_xticks(range(3),[rf"$\sigma={s:g}$" for s in SIGMAS])
        ax.set_title(f"({chr(97+j)}) {label}",loc="left")
        ax.grid(axis="y",alpha=.45);ax.set_axisbelow(True)
        if j==1:
            ax.text(.5,-.28,"Derived as revenue − profit;\nnot independently measured",ha="center",
                    va="top",transform=ax.transAxes,fontsize=6.2)
    fig.legend(*axs[0].get_legend_handles_labels(),loc="outside upper center",ncol=2,frameon=False)
    save_figure(fig,out,"figure_3_4_production_profitability");plt.close(fig)
    # Figure 3.5: Do not fabricate 20 task activities from aggregate output.
    fig,ax=plt.subplots(figsize=(7.05,2.45),layout="constrained")
    ax.set_axis_off()
    ax.text(.5,.73,"Task-level allocation: not identifiable from archived outputs",
            ha="center",va="center",fontsize=11,fontweight="bold",transform=ax.transAxes)
    ax.text(.5,.44,"Original CSVs contain aggregate output and AI task counts,\n"
            "but no task activity, normalized task index, or task-level K/L allocation.\n"
            "A 20-task distribution would require verified observational instrumentation\n"
            "and baseline-matched reproduction of the original simulation.",
            ha="center",va="center",fontsize=8,transform=ax.transAxes)
    ax.text(.5,.12,"Evidence gap — no task-level values are plotted",ha="center",fontsize=8,
            color="#9a4c00",transform=ax.transAxes)
    save_figure(fig,out,"figure_3_5_task_allocation");plt.close(fig)
    # Figure 3.6: observed actual AI use; unavailable K/L shown explicitly.
    fig,axs=plt.subplots(1,3,figsize=(7.05,2.6),layout="constrained")
    for ax,title in zip(axs,("(a) Capital used, K","(b) Labor used, L",
                              "(c) Active AI tasks (0–20)")):
        ax.set_title(title,loc="left")
    for ax in axs[:2]:
        ax.set_axis_off()
        ax.text(.5,.5,"Not archived\nCannot reconstruct from counts",ha="center",va="center",
                transform=ax.transAxes,color="#8c5200",fontsize=8)
    ax=axs[2]
    for policy in POLICIES:
        z=means[means.strategy_id==policy].set_index("sigma").loc[list(SIGMAS)]
        ax.plot(range(3),z.mean_active_ai_tasks,marker="o",markersize=4,
                color=ALLOCATION_COLORS["cost_adjusted" if policy==A else "productivity"],
                label="Cost-adjusted" if policy==A else "Productivity")
    ax.set_xticks(range(3),[rf"$\sigma={s:g}$" for s in SIGMAS])
    ax.set_ylim(bottom=0);ax.set_ylabel("Mean active tasks / round")
    ax.grid(axis="y",alpha=.45)
    fig.legend(*ax.get_legend_handles_labels(),loc="outside upper center",ncol=2,frameon=False)
    save_figure(fig,out,"figure_3_6_resource_automation");plt.close(fig)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True)
    p.add_argument("--out",default="results/paper/section3")
    a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    paths=sorted(Path(a.input).rglob("sigma_*_batch_*_rounds.csv"))
    assert len(paths)==30
    d=pd.concat([pd.read_csv(path) for path in paths],ignore_index=True)
    summary31=pd.read_csv(out/"section3_1_summary.csv")
    x,per,means,pairs,checks=audit(d,summary31)
    means.to_csv(out/"section3_2_summary.csv",index=False)
    pairs.to_csv(out/"section3_2_pairwise.csv",index=False)
    per.to_csv(out/"section3_2_profile_metrics.csv",index=False)
    checks["round_level_derived_total_cost"]="revenue minus realized profit (algebraic, not independently verified)"
    (out/"section3_2_validation.json").write_text(json.dumps(checks,indent=2)+"\n")
    figures(per,means,out)
    rows=["# Section 3.2 — Technological substitutability: evidence audit",
          "","## Provenance",
          f"Archived original run #42463803820, commit `{SOURCE_COMMIT}`, seed 11; "
          "Section 3.1 baseline. No simulation rerun or economic-model changes.",
          "","## Observed results",
          "Paired unit: one of 100 synthetic technology profiles, identical profile IDs "
          "across three sigma conditions. 200 rounds per policy trajectory. "
          "A = cost_adjusted + profit_based; B = productivity + profit_based.",
          "","| Sigma | Mean profit A | Mean profit B | Mean D=A−B | Median D | SD D | D>0 | D<0 | Descriptive 95% interval |",
          "|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for s in SIGMAS:
        aa=means[(means.sigma==s)&(means.strategy_id==A)].iloc[0]
        bb=means[(means.sigma==s)&(means.strategy_id==B)].iloc[0]
        v=pairs[(pairs.sigma==s)&(pairs.contrast=="A_minus_B")].iloc[0]
        rows.append(f"| {s:g} | {aa.mean_cumulative_profit:.3f} | {bb.mean_cumulative_profit:.3f} | "
                    f"{v['mean']:.3f} | {v['median']:.3f} | {v.sd:.3f} | "
                    f"{v.positive} | {v.negative} | [{v.descriptive95_lower:.3f}, {v.descriptive95_upper:.3f}] |")
    rows+=["","## Within-profile sigma contrasts",""]
    for _,v in pairs[pairs.contrast!="A_minus_B"].iterrows():
        rows.append(f"- {v.contrast}: mean {v['mean']:.4f}; median {v['median']:.4f}; "
                    f"SD {v.sd:.4f}; positive {v.positive}/100; negative {v.negative}/100; "
                    f"95% descriptive [{v.descriptive95_lower:.4f}, {v.descriptive95_upper:.4f}].")
    rows+=["","## Accounting and data availability",
           "Archived round fields: profile ID, sigma, round, policy, action, output, "
           "market price, realized profit, cumulative profit, adopted task count and active AI task count. "
           "Revenue is computed exactly as P×q. **Total cost is only an algebraic residual** "
           "P×q−profit, NOT an independent cost measurement. Variable input cost, adjustment "
           "cost, adoption cost, K, L, task-level allocation and task-level normalized activities "
           "are absent. No independent component-level profit reconciliation is possible.",
           "",
           "AI active task count measures **actual use**, not eligible task count; adopted_count "
           "is cumulative history, not currently active modes. Share of eligible tasks automated "
           "is unavailable. Action-budget category is observed, but does not measure actual "
           "capacity utilization. Changes in adopted_count can describe first-time adoption "
           "events, not reversals of mode or total switching frequency.",
           "",
           "## Technology comparability",
           "Original generator calls approved_profiles() and uses technology_for_profile(firm,sigma). "
           "The A5 reference_for_profile(firm) is fixed from each profile's labor productivities "
           "and labor endowment, independent of sigma. Sigma changes the CES aggregator, "
           "not the stored task productivity coefficients. The same profile IDs occur across "
           "sigma. Endogenous choices, prices and learning paths may nevertheless differ.",
           "",
           "## Figure captions",
           "**Figure 3.4.** Panels (a)–(c) show mean realized output per round, "
           "mean **algebraically implied** total cost per round (Pq−profit), and mean "
           "200-round cumulative realized profit, respectively, for the two profit-based "
           "automation policies at sigma 0.5, 1 and 2. Means are across 100 matched "
           "synthetic technology profiles per condition, seed 11. Colors identify "
           "allocation policy. Panel (b) is not an independent component-cost measurement; "
           "no causal cost mechanism is established.",
           "",
           "**Figure 3.5.** Evidence-availability panel. The archived original experiment "
           "does not include normalized activity or resource allocation for any of the "
           "20 tasks. Accordingly no task distribution is displayed. Reconstructing "
           "task rankings from aggregate output would be invalid. A verified baseline-matched "
           "instrumented reproduction is required before this figure can become a task-level plot.",
           "",
           "**Figure 3.6.** Panels (a) and (b) explicitly indicate unavailable capital "
           "and labor utilization. Panel (c) plots the mean number of tasks actively "
           "using AI per firm-round for both policies and all three sigma conditions. "
           "Values are averages over 100 synthetic technology profiles and 200 rounds; "
           "counts (0–20) do not represent eligibility, adoption history, or capital stock. "
           "No uncertainty interval is inferred from missing K/L measurements.",
           "",
           "## Mechanism-consistent patterns",
           "Any co-movement of observed output, AI task use and profit across sigma is "
           "descriptive and may be consistent with alternative production-allocation "
           "mechanisms. It cannot independently identify task concentration, cost channels "
           "or price causation.",
           "",
           "## Unresolved mechanisms and validation status",
           "To test task-level concentration and component costs, instrument the original "
           "engine observationally (task activity, task K/L, eligible task count, "
           "new adoptions, switching, variable/adjustment/adoption costs, actual capacity). "
           "A rerun may be called a reproduction only after matching original "
           "per-profile/sigma/policy cumulative profits and rankings at documented "
           "numerical tolerances. Existing cross-workflow numerical solver discrepancies "
           "make this a substantive gate, not a formality. "
           "Single-seed synthetic outcomes are not externally calibrated; "
           "no global optimum or causal identification is claimed. `research_validated=false`.",
           ""]
    (out/"section3_2_evidence.md").write_text("\n".join(rows))
    for stem in ("figure_3_4_production_profitability","figure_3_5_task_allocation",
                 "figure_3_6_resource_automation"):
        for ext in ("pdf","svg","png"):
            assert (out/f"{stem}.{ext}").stat().st_size>1000
    print("SECTION_3_2_ARCHIVE_AUDIT_PASS",json.dumps(checks,sort_keys=True))
if __name__=="__main__":
    main()

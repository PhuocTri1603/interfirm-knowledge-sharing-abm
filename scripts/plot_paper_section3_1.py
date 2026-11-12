"""Publication figures from archived original nine-policy round-level outputs.

No economic simulation is run. All plotted values are exported as CSV first.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.lines import Line2D
from paper_plot_style import (POLICIES,SIGMAS,ALLOCATION_COLORS,AUTOMATION_MARKERS,
    AUTOMATION_STYLES,parse_policy,policy_label,apply_style,save_figure,allocation_legend,automation_legend)

FOCAL=((POLICIES[8],POLICIES[5]),(POLICIES[8],POLICIES[2]),
       (POLICIES[8],POLICIES[7]),(POLICIES[8],POLICIES[6]))
FOCAL_LABELS=("Cost-adj. − Productivity\nProfit-based",
              "Cost-adj. − Uniform\nProfit-based",
              "Profit-based − Cost-based\nCost-adjusted",
              "Profit-based − No automation\nCost-adjusted")
SELECTED=(POLICIES[2],POLICIES[5],POLICIES[8],POLICIES[7])

def check_inputs(summary,pairs,rounds):
    assert summary.shape[0]==27
    assert not summary.duplicated(["sigma","strategy_id"]).any()
    assert set(summary.sigma)==set(SIGMAS)
    assert set(summary.strategy_id)==set(POLICIES)
    assert pairs.shape[0]==108 and not pairs.duplicated(["sigma","policy_a","policy_b"]).any()
    assert rounds.shape[0]==540000
    assert not rounds.duplicated(["profile_id","sigma","strategy_id","round"]).any()
    assert rounds.profile_id.nunique()==100
    assert set(rounds.sigma)==set(SIGMAS)
    assert set(rounds.strategy_id)==set(POLICIES)
    assert set(rounds["round"])==set(range(1,201))
    assert rounds.groupby(["profile_id","sigma","strategy_id"]).size().eq(200).all()
    assert summary.select_dtypes("number").replace([np.inf,-np.inf],np.nan).notna().all().all()
    assert pairs.select_dtypes("number").replace([np.inf,-np.inf],np.nan).notna().all().all()
    assert rounds[["cumulative_profit","profit","output","price"]].replace([np.inf,-np.inf],np.nan).notna().all().all()
    assert list(POLICIES)==[f"L3={a}|L4={b}" for a in ("uniform","productivity","cost_adjusted") for b in ("no_automation","cost_based","profit_based")]
    # Verify plotted means against raw terminal cumulative profits.
    terminal=rounds.loc[rounds["round"]==200]
    direct=terminal.groupby(["sigma","strategy_id"]).cumulative_profit.mean()
    reported=summary.set_index(["sigma","strategy_id"]).mean_cumulative_profit
    assert float((direct-reported).abs().max())<1e-7

def create_figure1(summary,rounds,out):
    # Panel (a): complete mean-profit heatmap, no policy omissions.
    heat=summary.pivot(index="strategy_id",columns="sigma",values="mean_cumulative_profit").loc[list(POLICIES),list(SIGMAS)]
    heat.rename_axis(index="strategy_id",columns="sigma").to_csv(out/"section3_1_figure1_heatmap_data.csv")
    # Panel (b): original 100 profile observations for every policy x sigma.
    terminal=rounds[rounds["round"]==200][["profile_id","sigma","strategy_id","cumulative_profit"]].copy()
    terminal.to_csv(out/"section3_1_figure1_distribution_data.csv",index=False)
    fig=plt.figure(figsize=(7.05,6.25),layout="constrained")
    gs=fig.add_gridspec(1,2,width_ratios=[1.05,1.65],wspace=.13)
    ax=fig.add_subplot(gs[0]);bx=fig.add_subplot(gs[1])
    vals=heat.to_numpy()
    # Single sequential scale preserves exact magnitude and avoids arbitrary zero centering.
    im=ax.imshow(vals,aspect="auto",cmap="cividis",vmin=float(vals.min()),vmax=float(vals.max()))
    ax.set_xticks(range(3),[rf"$\sigma={s:g}$" for s in SIGMAS])
    ax.set_yticks(range(9),[policy_label(p,short=True) for p in POLICIES],fontsize=6.3)
    ax.set_title("(a) Mean cumulative profit",loc="left",fontweight="bold")
    for i in range(9):
        for j in range(3):
            value=vals[i,j]
            ax.text(j,i,f"{value:.0f}",ha="center",va="center",fontsize=6.5,
                    color="white" if im.norm(value)<.22 else "#111111")
    cbar=fig.colorbar(im,ax=ax,orientation="horizontal",shrink=.85,pad=.04)
    cbar.set_label(r"Mean $\Pi_{i,c}$ (200 rounds)",fontsize=7)
    # Horizontal box distributions: 9 policies x 3 sigmas, with aligned policy rows.
    offsets={.5:-.23,1.:0,2.:.23}
    for i,p in enumerate(POLICIES):
        a,b=parse_policy(p)
        for s in SIGMAS:
            data=terminal.loc[(terminal.strategy_id==p)&(terminal.sigma==s),"cumulative_profit"].to_numpy()
            assert len(data)==100
            y=i+offsets[s]
            artist=bx.boxplot([data],positions=[y],vert=False,widths=.19,patch_artist=True,
                showfliers=False,whis=(5,95),manage_ticks=False)
            artist["boxes"][0].set(facecolor=ALLOCATION_COLORS[a],alpha=.25,edgecolor=ALLOCATION_COLORS[a],linewidth=.65)
            for item in artist["whiskers"]+artist["caps"]:
                item.set(color=ALLOCATION_COLORS[a],linewidth=.65)
            artist["medians"][0].set(color="#222222",linewidth=.9)
            bx.plot(data.mean(),y,marker={.5:"o",1.:"s",2.:"D"}[s],ms=2.7,
                    color=ALLOCATION_COLORS[a],markeredgecolor="white",markeredgewidth=.25)
    bx.axvline(0,color="#555555",lw=.65)
    bx.set_yticks(range(9),[""]*9);bx.set_ylim(8.65,-.65)
    bx.set_xlabel(r"Cumulative realized profit, $\Pi_{i,c}$")
    bx.set_title("(b) Across-profile distributions",loc="left",fontweight="bold")
    bx.grid(axis="x");bx.set_axisbelow(True)
    bx.legend(handles=[Line2D([0],[0],marker=m,color="#555555",lw=0,ms=4,label=rf"$\sigma={s:g}$")
                for s,m in ((.5,"o"),(1.,"s"),(2.,"D"))],
                loc="upper right",frameon=False,title="Mean markers",title_fontsize=7)
    save_figure(fig,out,"figure_3_1_profitability")
    plt.close(fig)

def create_figure2(pairs,out):
    rows=[]
    for s in SIGMAS:
        for i,(a,b) in enumerate(FOCAL):
            z=pairs[(pairs.sigma==s)&(pairs.policy_a==a)&(pairs.policy_b==b)]
            # The source pairwise table stores pairs in canonical order, which may be reversed.
            sign=1
            if z.empty:
                z=pairs[(pairs.sigma==s)&(pairs.policy_a==b)&(pairs.policy_b==a)]
                sign=-1
            assert len(z)==1,(s,a,b)
            r=z.iloc[0]
            rows.append(dict(sigma=s,comparison=i,policy_a=a,policy_b=b,
                mean_difference=sign*r.mean_difference,
                lower=sign*(r.ci95_normal_lower if sign==1 else r.ci95_normal_upper),
                upper=sign*(r.ci95_normal_upper if sign==1 else r.ci95_normal_lower),
                positive_profiles=int(r.positive_profiles if sign==1 else r.negative_profiles),
                negative_profiles=int(r.negative_profiles if sign==1 else r.positive_profiles),
                tied_profiles=int(r.tied_profiles),n=100))
    d=pd.DataFrame(rows)
    d.to_csv(out/"section3_1_figure2_forest_data.csv",index=False)
    fig,axes=plt.subplots(1,3,figsize=(7.05,3.35),sharex=True,sharey=True,layout="constrained")
    low=float(d.lower.min());high=float(d.upper.max());margin=(high-low)*.08
    for ax,s in zip(axes,SIGMAS):
        z=d[d.sigma==s].sort_values("comparison")
        for _,r in z.iterrows():
            i=int(r.comparison);a,_=parse_policy(r.policy_a)
            color=ALLOCATION_COLORS[a]
            ax.plot([r.lower,r.upper],[i,i],color=color,lw=1.8,solid_capstyle="round")
            ax.plot(r.mean_difference,i,marker="D",color=color,ms=4)
            ax.annotate(f"{r.positive_profiles}/100",xy=(r.mean_difference,i),
                        xytext=(0,-10),textcoords="offset points",ha="center",fontsize=5.8,color="#555555")
        ax.axvline(0,color="#333333",lw=.9,linestyle="--")
        ax.set_xlim(low-margin,high+margin)
        ax.set_yticks(range(4),FOCAL_LABELS,fontsize=6.4)
        ax.set_ylim(3.55,-.55)
        ax.set_title(rf"$\sigma={s:g}$",fontweight="bold")
        ax.grid(axis="x");ax.set_axisbelow(True)
    fig.supxlabel(r"Paired mean difference in $\Pi_{i,c}$ (A − B)",fontsize=8)
    fig.suptitle("Dots: mean; bars: descriptive 95% interval; annotations: profiles with A > B",
                 fontsize=7.2)
    save_figure(fig,out,"figure_3_2_paired_differences")
    plt.close(fig)

def create_figure3(rounds,out):
    x=rounds.loc[rounds.strategy_id.isin(SELECTED),["profile_id","sigma","strategy_id","round","cumulative_profit"]]
    assert len(x)==100*3*len(SELECTED)*200
    agg=x.groupby(["sigma","strategy_id","round"]).cumulative_profit.agg(
        mean="mean",q25=lambda z:z.quantile(.25),q75=lambda z:z.quantile(.75),
        sd="std",n="size").reset_index()
    assert len(agg)==3*len(SELECTED)*200 and agg.n.eq(100).all()
    agg.to_csv(out/"section3_1_figure3_dynamics_data.csv",index=False)
    fig,axes=plt.subplots(1,3,figsize=(7.05,3.2),sharex=True,sharey=True,layout="constrained")
    ymin=float(agg.q25.min());ymax=float(agg.q75.max());padding=(ymax-ymin)*.07
    for ax,s in zip(axes,SIGMAS):
        for p in SELECTED:
            z=agg[(agg.sigma==s)&(agg.strategy_id==p)].sort_values("round")
            a,b=parse_policy(p);color=ALLOCATION_COLORS[a]
            ax.plot(z["round"],z["mean"],color=color,linestyle=AUTOMATION_STYLES[b],
                    lw=1.55,label=policy_label(p,short=True))
            ax.fill_between(z["round"].to_numpy(),z.q25.to_numpy(),z.q75.to_numpy(),
                            color=color,alpha=.105,linewidth=0)
        ax.set_title(rf"({chr(97+list(SIGMAS).index(s))}) $\sigma={s:g}$",loc="left",fontweight="bold")
        ax.set_xlim(1,200);ax.set_ylim(ymin-padding,ymax+padding)
        ax.axhline(0,color="#666666",lw=.6)
        ax.grid(axis="y");ax.set_axisbelow(True)
        ax.set_xlabel("Round, $t$")
    axes[0].set_ylabel(r"Mean cumulative profit, $\Pi_{i,c}(t)$")
    fig.legend(handles=[Line2D([0],[0],color=ALLOCATION_COLORS[parse_policy(p)[0]],
                 linestyle=AUTOMATION_STYLES[parse_policy(p)[1]],lw=1.8,
                 label=policy_label(p,short=True)) for p in SELECTED],
               loc="outside lower center",ncol=2,frameon=False)
    save_figure(fig,out,"figure_3_3_policy_dynamics")
    plt.close(fig)

CAPTIONS="""
## Publication figure captions (replacement figures)

**Figure 3.1. Profitability across allocation and automation policies.** Panel (a) reports the mean 200-round cumulative realized profit, \(\Pi_{i,c}=\sum_{t=1}^{200}\pi_{ict}\), for each of the nine simultaneously competing policies and each task-substitution elasticity \(\sigma\in\{0.5,1,2\}\). Cell labels are means over 100 synthetic technology profiles; the common heatmap scale encodes magnitude. Panel (b) shows the distribution of the same 100 profile-level cumulative profits for each policy and elasticity. Boxes denote the interquartile range with median lines, whiskers the 5th–95th percentiles, and markers the profile means (circle: 0.5; square: 1; diamond: 2). Allocation is encoded consistently by color (blue: uniform; vermilion: productivity; green: cost-adjusted). All policies are displayed, including low performers. Observations are generated by the original nine-policy simulation (one seed, 11; 200 rounds); profiles are synthetic, not independent real-world firms. Descriptive distributions are not causal intervals.

**Figure 3.2. Within-profile paired profitability differences.** Each panel reports four prespecified comparisons at a fixed elasticity \(\sigma\). The horizontal axis is the difference in cumulative realized profit for policy A minus policy B, paired by identical synthetic technology profile (100 matched profiles per comparison and elasticity). Diamonds denote the sample mean and bars denote mean \(\pm1.96s_d/\sqrt{100}\), where \(s_d\) is the sample standard deviation of the 100 paired differences (ddof = 1). The dashed vertical line marks zero; text below each point gives the count of profiles where A exceeds B, with ties defined by absolute differences no greater than \(10^{-8}\). Intervals summarize synthetic-profile variation, not empirical causal confidence intervals. Policies interact in the same endogenous-price market, so these are descriptive policy contrasts rather than isolated causal effects.

**Figure 3.3. Dynamics of cumulative realized profitability.** Panels (a)–(c) display the mean trajectory \(\Pi_{i,c}(t)=\sum_{\tau=1}^{t}\pi_{ic\tau}\) over rounds \(t=1,\ldots,200\) for selected prespecified policies under \(\sigma=0.5,1,2\), respectively. Lines are profile means and translucent bands represent the 25th–75th percentiles of 100 synthetic technology profiles at each round; these bands describe cross-profile heterogeneity rather than estimation uncertainty. Colors identify allocation (blue: uniform; vermilion: productivity; green: cost-adjusted), while solid lines identify profit-based automation and dashed lines cost-based automation. Axes are shared across panels. Trajectories are computed from archived original round-level cumulative-profit observations, not interpolated from terminal totals. Four of nine policies are shown to preserve legibility; the complete nine-policy terminal comparison is in Figure 3.1. Single seed (11), uncalibrated model parameters, and endogenous joint market interactions limit external and causal interpretation.
"""

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True)
    p.add_argument("--out",default="results/paper/section3")
    a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    apply_style()
    summary=pd.read_csv(out/"section3_1_summary.csv")
    pairs=pd.read_csv(out/"section3_1_pairwise.csv")
    paths=sorted(Path(a.input).rglob("sigma_*_batch_*_rounds.csv"))
    assert len(paths)==30
    rounds=pd.concat([pd.read_csv(p) for p in paths],ignore_index=True)
    check_inputs(summary,pairs,rounds)
    create_figure1(summary,rounds,out)
    create_figure2(pairs,out)
    create_figure3(rounds,out)
    evidence=out/"section3_1_evidence.md"
    text=evidence.read_text()
    # Single canonical report, deterministic on repeated execution.
    text=text.split("## Publication figure captions (replacement figures)")[0]
    if "## Figure captions" in text and "## Interpretation and limits" in text:
        prefix,tail=text.split("## Figure captions",1)
        text=prefix+"## Interpretation and limits"+tail.split("## Interpretation and limits",1)[1]
    text=text.rstrip()
    evidence.write_text(text+"\n\n"+CAPTIONS.strip()+"\n")
    manifest=dict(figures=["figure_3_1_profitability","figure_3_2_paired_differences",
                           "figure_3_3_policy_dynamics"],
                  formats=["pdf","svg","png"],png_dpi=300,
                  profile_replicates_per_sigma=100,
                  figure3_selected_policies=list(SELECTED),
                  figure3_input_rows=len(rounds),plotting_style="scripts/paper_plot_style.py",
                  integrity="PASS",research_validated=False)
    (out/"section3_1_figure_qa.json").write_text(json.dumps(manifest,indent=2)+"\n")
    for stem in manifest["figures"]:
        for ext in manifest["formats"]:
            assert (out/f"{stem}.{ext}").stat().st_size>1000
    print("FIGURE_QA_PASS",json.dumps(manifest))

if __name__=="__main__":
    main()

"""Section 3.1 evidence from the ORIGINAL 9-policy full sample, run 42463803820."""
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

POLICIES=[f"L3={a}|L4={b}" for a in ("uniform","productivity","cost_adjusted") for b in ("no_automation","cost_based","profit_based")]
SIGMAS=(.5,1.,2.)
SOURCE="c614b86d9192a57fb402b4772b3c3bb6bf80b79f"
ARTIFACT=13618500797

def analyze(root,out):
    root=Path(root);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    paths=sorted(root.rglob("sigma_*_batch_*_rounds.csv"))
    metas=sorted(root.rglob("sigma_*_batch_*_metadata.json"))
    assert len(paths)==len(metas)==30,(len(paths),len(metas))
    metadata=[json.loads(p.read_text()) for p in metas]
    assert {(m["sigma"],m["batch"]) for m in metadata}=={(s,b) for s in SIGMAS for b in range(10)}
    assert all(m["profiles"]==10 and m["strategies"]==9 and m["rounds"]==200 for m in metadata)
    assert len({json.dumps(m["params"],sort_keys=True) for m in metadata})==1
    params=metadata[0]["params"]
    assert params["seed"]==11
    d=pd.concat([pd.read_csv(p) for p in paths],ignore_index=True)
    keys=["profile_id","sigma","strategy_id","round"]
    duplicates=int(d.duplicated(keys).sum())
    assert len(d)==540000 and duplicates==0
    assert d.profile_id.nunique()==100 and set(d.sigma)==set(SIGMAS)
    assert set(d.strategy_id)==set(POLICIES) and set(d["round"])==set(range(1,201))
    counts=d.groupby(keys[:-1]).size()
    assert len(counts)==2700 and counts.eq(200).all()
    assert d[["profit","cumulative_profit","output","price","active_ai_count"]].notna().all().all()
    d=d.sort_values(keys)
    cumulative_error=float((d.groupby(keys[:-1],sort=False).profit.cumsum()-d.cumulative_profit).abs().max())
    m=d.groupby(["profile_id","sigma","round"]).agg(pmin=("price","min"),pmax=("price","max"),quantity=("output","sum"),n=("strategy_id","size"))
    assert len(m)==60000 and m.n.eq(9).all()
    price_spread=float((m.pmax-m.pmin).abs().max())
    demand_error=float((m.pmin-np.maximum(0,params["demand_intercept"]-params["demand_slope"]*m.quantity)).abs().max())
    totals=d.groupby(keys[:-1],as_index=False).agg(profit=("profit","sum"),mean_output=("output","mean"),mean_active_ai_tasks=("active_ai_count","mean"))
    terminal=d[d["round"]==200][keys[:-1]+["cumulative_profit"]]
    totals=totals.merge(terminal,on=keys[:-1],validate="one_to_one")
    terminal_error=float((totals.profit-totals.cumulative_profit).abs().max())
    assert max(cumulative_error,terminal_error,price_spread,demand_error)<1e-7
    # Equal fractional credit for any first-place ties within absolute 1e-8.
    top=totals.groupby(["profile_id","sigma"]).profit.transform("max")
    totals["winner"]=np.isclose(totals.profit,top,atol=1e-8,rtol=0)
    totals["win_credit"]=totals.winner/totals.groupby(["profile_id","sigma"]).winner.transform("sum")
    summary=totals.groupby(["sigma","strategy_id"]).agg(
        n_profiles=("profit","size"),mean_cumulative_profit=("profit","mean"),
        median_cumulative_profit=("profit","median"),sd_cumulative_profit=("profit","std"),
        min_cumulative_profit=("profit","min"),p25_cumulative_profit=("profit",lambda x:x.quantile(.25)),
        p75_cumulative_profit=("profit",lambda x:x.quantile(.75)),
        max_cumulative_profit=("profit","max"),first_place_credit=("win_credit","sum"),
        first_place_profiles_including_ties=("winner","sum"),
        positive_profit_profiles=("profit",lambda x:(x>1e-8).sum()),
        mean_realized_output=("mean_output","mean"),
        mean_active_ai_tasks=("mean_active_ai_tasks","mean")).reset_index()
    summary["first_place_pct"]=summary.first_place_credit
    summary["positive_profit_pct"]=summary.positive_profit_profiles
    summary.to_csv(out/"section3_1_summary.csv",index=False)
    wide=totals.pivot(index=["profile_id","sigma"],columns="strategy_id",values="profit")
    comparisons=[]
    for s in SIGMAS:
        x=wide.xs(s,level="sigma")
        for i,a in enumerate(POLICIES):
            for b in POLICIES[i+1:]:
                v=(x[a]-x[b]).to_numpy();mean=float(v.mean());sd=float(v.std(ddof=1))
                comparisons.append(dict(sigma=s,policy_a=a,policy_b=b,n=100,
                    mean_difference=mean,median_difference=float(np.median(v)),sd_difference=sd,
                    positive_profiles=int((v>1e-8).sum()),negative_profiles=int((v< -1e-8).sum()),
                    tied_profiles=int((abs(v)<=1e-8).sum()),
                    ci95_normal_lower=mean-1.96*sd/10,ci95_normal_upper=mean+1.96*sd/10))
    pd.DataFrame(comparisons).to_csv(out/"section3_1_pairwise.csv",index=False)
    labels=[x.replace("L3=","").replace("|L4="," + ") for x in POLICIES]
    def save(fig,stem):
        fig.savefig(out/(stem+".png"),dpi=240,bbox_inches="tight")
        fig.savefig(out/(stem+".svg"),bbox_inches="tight")
        plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(18,7),sharey=True,layout="constrained")
    for ax,s in zip(axes,SIGMAS):
        z=summary[summary.sigma==s].set_index("strategy_id").loc[POLICIES]
        y=np.arange(9);ax.barh(y,z.mean_cumulative_profit,color="#38688e",label="Mean")
        ax.hlines(y,z.p25_cumulative_profit,z.p75_cumulative_profit,color="#d47b32",linewidth=4,label="Profile IQR")
        ax.set_yticks(y,labels);ax.invert_yaxis();ax.axvline(0,color="black",lw=.8)
        ax.set_title(f"σ = {s:g}");ax.set_xlabel("Cumulative profit (200 rounds)");ax.grid(axis="x",alpha=.2)
    axes[0].legend(loc="lower right")
    save(fig,"figure_3_1_profitability")
    focal=[(POLICIES[8],POLICIES[5]),(POLICIES[8],POLICIES[2]),(POLICIES[8],POLICIES[7]),(POLICIES[8],POLICIES[6])]
    flabels=["Cost-adjusted vs productivity\n(profit-based)","Cost-adjusted vs uniform\n(profit-based)","Profit-based vs cost-based\n(cost-adjusted)","Profit-based vs no automation\n(cost-adjusted)"]
    fig,axes=plt.subplots(1,3,figsize=(18,6),sharey=True,layout="constrained")
    for ax,s in zip(axes,SIGMAS):
        x=wide.xs(s,level="sigma")
        values=[(x[a]-x[b]).to_numpy() for a,b in focal]
        ax.boxplot(values,vert=False,positions=range(1,5),patch_artist=True,boxprops={"facecolor":"#c7dce9"})
        ax.scatter([v.mean() for v in values],range(1,5),marker="D",color="#ad422b",s=35,label="Mean",zorder=4)
        ax.axvline(0,color="black",ls="--",lw=1);ax.set_yticks(range(1,5),flabels);ax.invert_yaxis()
        ax.set_title(f"σ = {s:g}");ax.set_xlabel("Within-profile profit difference (A − B)");ax.grid(axis="x",alpha=.2)
    axes[0].legend(loc="lower right")
    save(fig,"figure_3_2_paired_differences")
    fig,axes=plt.subplots(1,3,figsize=(18,7),sharey=True,layout="constrained")
    for ax,s in zip(axes,SIGMAS):
        z=summary[summary.sigma==s].set_index("strategy_id").loc[POLICIES]
        ax.barh(range(9),z.first_place_credit,color="#527e70")
        ax.set_yticks(range(9),labels);ax.invert_yaxis();ax.set_title(f"σ = {s:g}")
        ax.set_xlabel("First-place profile credit (out of 100)");ax.grid(axis="x",alpha=.2)
    save(fig,"figure_3_3_policy_rankings")
    checks=dict(source_run=42463803820,source_commit=SOURCE,artifact_id=ARTIFACT,
        parameters=params,expected_firm_rounds=540000,observed_firm_rounds=len(d),
        profiles=100,sigma_conditions=3,policies=9,rounds_per_trajectory=200,
        trajectories=len(counts),market_rounds=len(m),duplicate_keys=duplicates,
        max_cumulative_round_residual=cumulative_error,max_terminal_sum_residual=terminal_error,
        max_same_market_price_spread=price_spread,max_inverse_demand_residual=demand_error,
        first_place_tied_markets=int((totals.groupby(["profile_id","sigma"]).winner.sum()>1).sum()),
        independent_cost_accounting_available=False,research_validated=False)
    (out/"section3_1_validation.json").write_text(json.dumps(checks,indent=2)+"\n")
    report=["# Section 3.1 — Nine-policy evidence (not manuscript conclusions)","",
        f"**Original source commit:** `{SOURCE}`; **run:** #42463803820; **artifact:** {ARTIFACT}. Re-analysis of existing original outputs, not a new experiment.","",
        f"**Original parameters and seed:** `{json.dumps(params,sort_keys=True)}`. 100 synthetic profiles × 3 σ × 9 simultaneously competing policies × 200 rounds.","",
        "## Integrity",f"540,000/540,000 firm-rounds; 2,700 complete trajectories; {duplicates} duplicate keys; {len(m)} market-rounds.",
        f"Max cumulative-profit error {cumulative_error:.3e}; terminal sum error {terminal_error:.3e}; same-market price spread {price_spread:.3e}; inverse-demand error {demand_error:.3e}.","",
        "## Statistical definitions","Technology profiles are the paired units, n=100 per sigma. SD is sample SD (ddof=1); intervals mean ± 1.96×SD/√100 (descriptive synthetic-profile variation, not empirical causal confidence intervals). All 36 unordered policy pairs per sigma are in the pairwise CSV. Ties within absolute 1e-8 share first-place credit equally; positive profit means >1e-8.","",
        "## Numerical findings"]
    for s in SIGMAS:
        z=summary[summary.sigma==s];mean=z.loc[z.mean_cumulative_profit.idxmax()];wins=z.loc[z.first_place_credit.idxmax()]
        report.append(f"- σ={s:g}: highest mean profit: `{mean.strategy_id}` ({mean.mean_cumulative_profit:.4f}); highest win credit: `{wins.strategy_id}` ({wins.first_place_credit:.0f}/100). These are different metrics.")
    report+=["","## Figure captions",
        "1. **Figure 3.1:** Mean cumulative realized profit and profile interquartile range for all nine policies, faceted by σ.",
        "2. **Figure 3.2:** Within-profile paired differences for four comparisons; boxplots show median, IQR, 1.5-IQR whiskers and outliers, diamonds show means; dashed zero reference.",
        "3. **Figure 3.3:** Fractionally tie-adjusted first-place profile credit by policy and σ, distinct from mean profitability.","",
        "## Interpretation and limits",
        "The data support descriptive heterogeneity of realized profitability across policies and sigma conditions. They do not establish global optimality or independently identify price causation. Original parameters are exploratory and uncalibrated; only seed 11 was run. Original round panels omit revenue and disaggregated variable/adjustment/adoption costs, so independent component-level profit accounting cannot be verified from these artifacts. Original engine uses endogenous market clearing and learning; rankings are conditional on this design. Cross-workflow numerical reproducibility of separate later AI/no-AI experiments remains unresolved. `research_validated=false`.",""]
    (out/"section3_1_evidence.md").write_text("\n".join(report))
    print("PASS",json.dumps(checks,sort_keys=True))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--input",required=True);p.add_argument("--out",default="results/paper/section3");a=p.parse_args();analyze(a.input,a.out)

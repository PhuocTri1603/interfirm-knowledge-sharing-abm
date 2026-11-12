"""Shared scientific plotting conventions for ABM paper Sections 3.1–3.5."""
from __future__ import annotations
import matplotlib as mpl
from matplotlib.lines import Line2D

ALLOCATIONS=("uniform","productivity","cost_adjusted")
AUTOMATIONS=("no_automation","cost_based","profit_based")
POLICIES=tuple(f"L3={a}|L4={b}" for a in ALLOCATIONS for b in AUTOMATIONS)
SIGMAS=(0.5,1.0,2.0)
# Okabe-Ito colorblind-safe subset; allocation is encoded by color.
ALLOCATION_COLORS={"uniform":"#0072B2","productivity":"#D55E00","cost_adjusted":"#009E73"}
AUTOMATION_STYLES={"no_automation":(0,(1.5,1.5)),"cost_based":(0,(5,2)),"profit_based":"solid"}
AUTOMATION_MARKERS={"no_automation":"o","cost_based":"s","profit_based":"D"}

def parse_policy(s):
    a,b=s.split("|")
    return a.removeprefix("L3="),b.removeprefix("L4=")

def policy_label(s,short=False):
    a,b=parse_policy(s)
    if short:
        return f"{a.replace('_','-')} / {b.replace('_','-')}"
    return f"{a.replace('_',' ').title()} + {b.replace('_',' ').title()}"

def apply_style():
    mpl.rcParams.update({
        "font.family":"DejaVu Sans","font.size":8,"axes.titlesize":9,
        "axes.labelsize":8,"xtick.labelsize":7,"ytick.labelsize":7,
        "legend.fontsize":7,"figure.facecolor":"white","axes.facecolor":"white",
        "savefig.facecolor":"white","axes.spines.top":False,
        "axes.spines.right":False,"axes.linewidth":0.7,
        "grid.color":"#d9d9d9","grid.linewidth":0.45,
        "grid.alpha":0.65,"pdf.fonttype":42,"ps.fonttype":42,
        "svg.fonttype":"none","figure.dpi":120
    })

def allocation_legend():
    return [Line2D([0],[0],color=ALLOCATION_COLORS[a],lw=2,label=a.replace("_"," ").title()) for a in ALLOCATIONS]

def automation_legend():
    return [Line2D([0],[0],color="#444444",linestyle=AUTOMATION_STYLES[a],
                   marker=AUTOMATION_MARKERS[a],markersize=3,lw=1.5,
                   label=a.replace("_"," ").title()) for a in AUTOMATIONS]

def save_figure(fig,folder,stem):
    from pathlib import Path
    p=Path(folder)
    p.mkdir(parents=True,exist_ok=True)
    for extension in ("pdf","svg","png"):
        fig.savefig(p/f"{stem}.{extension}",dpi=300,bbox_inches="tight",pad_inches=0.08)

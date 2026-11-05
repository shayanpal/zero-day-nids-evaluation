import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from scipy import stats

# Usage: python make_figs.py [results_dir] [out_dir]   (defaults: ../results, ../figures)
BASE = os.path.dirname(os.path.abspath(__file__))
DATA = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "..", "results")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(BASE, "..", "figures")
os.makedirs(OUT, exist_ok=True)

INK, INK2, GRID, SURF = "#1f1f1e", "#5f5e5a", "#e4e3df", "#ffffff"
C = {"RF": "#2a78d6", "XGB": "#eb6834", "ENS": "#1baf7a", "IF": "#eda100"}
REL = [("cic2017", "CIC-IDS2017 (original)"), ("cic2017i", "CIC-IDS2017 (corrected)"),
       ("cic2018", "CSE-CIC-IDS2018 (original)")]
RELC = {"cic2017": "#2a78d6", "cic2017i": "#eb6834", "cic2018": "#1baf7a"}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK,
    "xtick.color": INK2, "ytick.color": INK2, "text.color": INK, "axes.linewidth": 0.6,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "legend.frameon": False,
    "pdf.fonttype": 42, "savefig.dpi": 300,
})

R = {ds: pd.read_csv(os.path.join(DATA, f"results_{ds}.csv")) for ds, _ in REL}


def ci(x):
    x = np.asarray(x, float)
    if len(x) < 2:
        return x.mean(), 0.0
    return x.mean(), stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))


def style(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.yaxis.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)


def save(fig, name):
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"), bbox_inches="tight", facecolor=SURF)
    plt.close(fig)


# ---------------- Figure 1: protocol ----------------
fig, ax = plt.subplots(figsize=(7.2, 2.0))
ax.set_xlim(-0.5, 101); ax.set_ylim(-4, 22); ax.axis("off")
steps = [
    ("1  Clean release", "drop identifiers,\nNaN/Inf rows,\nlabel conflicts,\nduplicates"),
    ("2  Split per seed", "each family 70/30\ntrain / test;\nbenign validation\n= 20% of train"),
    ("3  Hold out f", "train on benign +\nother families;\nfeature selection\ninside the fold"),
    ("4  Set threshold", "99th / 99.9th\npercentile of benign\nvalidation scores\n(1% / 0.1% FPR)"),
    ("5  Evaluate", "detection of unseen f,\nknown and rare\nfamilies; test FPR,\nAUROC"),
]
w, gap, x0 = 18.2, 2.2, 0.4
for i, (t, d) in enumerate(steps):
    x = x0 + i * (w + gap)
    ax.add_patch(FancyBboxPatch((x, 0.5), w, 19.5, boxstyle="round,pad=0.2,rounding_size=1.0",
                                fc="#e6f0fb" if i == 2 else "#f3f7fd", ec="#2a78d6", lw=0.9))
    ax.text(x + w / 2, 17.0, t, ha="center", va="center", fontsize=7.0, weight="bold")
    ax.text(x + w / 2, 8.2, d, ha="center", va="center", fontsize=6.3, color=INK2, linespacing=1.3)
    if i < len(steps) - 1:
        ax.annotate("", xy=(x + w + gap - 0.15, 10.2), xytext=(x + w + 0.15, 10.2),
                    arrowprops=dict(arrowstyle="-|>", color=INK2, lw=0.8, mutation_scale=7))
ax.text(50, -2.6, "Steps 3-5 repeat for every held-out family and 5 seeds; each pitfall changes exactly one step.",
        ha="center", fontsize=6.8, color=INK2, style="italic")
save(fig, "fig1_protocol")

# ---------------- Figure 2: per-family unseen detection ----------------
models = ["RF", "XGB", "ENS", "IF"]
fig, axes = plt.subplots(3, 1, figsize=(7.2, 6.4), sharey=True)
for ax, (ds, title) in zip(axes, REL):
    u = R[ds][(R[ds].role == "unseen") & (R[ds].fs == "all") & (R[ds].model.isin(models))]
    fams = sorted(u.heldout.unique(), key=lambda f: -u[(u.heldout == f) & (u.model == "ENS")].det_fpr1.mean())
    bw = 0.19
    for j, m in enumerate(models):
        xs = np.arange(len(fams)) + (j - 1.5) * (bw + 0.015)
        means = [u[(u.heldout == f) & (u.model == m)].det_fpr1.mean() for f in fams]
        ax.bar(xs, means, width=bw, color=C[m], ec=SURF, lw=0.8, label=m, zorder=2)
        for x, f in zip(xs, fams):
            sv = u[(u.heldout == f) & (u.model == m)].det_fpr1.to_numpy()
            ax.scatter(np.full(len(sv), x) + np.linspace(-0.05, 0.05, len(sv)), sv, s=5, color=INK,
                       lw=0, zorder=3, label="single seed" if (m == "RF" and f == fams[0]) else None)
    ens_mean = u[u.model == "ENS"].groupby("seed").det_fpr1.mean().mean()
    ax.axhline(ens_mean, color=C["ENS"], lw=0.9, ls="--", zorder=1)
    ax.text(len(fams) - 0.45, ens_mean + 0.03, f"ENS mean {ens_mean:.2f}", ha="right", fontsize=6.8, color=INK2)
    ax.set_xticks(range(len(fams))); ax.set_xticklabels(fams)
    ax.set_ylim(0, 1.05); ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_title(title, loc="left", fontsize=8.5, weight="bold")
    ax.set_ylabel("Detection at 1% FPR")
    style(ax)
axes[0].legend(ncol=5, loc="upper right", bbox_to_anchor=(1.0, 1.32), fontsize=7.5, handlelength=1.2)
axes[-1].set_xlabel("Held-out (unseen) family, sorted by ENS detection (bars: mean of 5 seeds; dots: single seeds)")
fig.tight_layout(h_pad=1.2)
save(fig, "fig2_per_family")

# ---------------- Figure 4: known vs unseen by feature-selection method ----------------
methods = [("all", "All features"), ("ga", "GA"), ("mi", "MI"), ("rfimp", "RF importance")]
fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.7), sharey=True)
for ax, (ds, title) in zip(axes, REL):
    r = R[ds][R[ds].model == "ENS"]
    for role, col, mk, lab, dx in (("known", INK2, "o", "Known families", -0.1),
                                   ("unseen", C["ENS"], "D", "Unseen family", 0.1)):
        pts = []
        for fs, _ in methods:
            q = r[(r.role == role) & (r.fs == fs)]
            pts.append(ci(q.groupby("seed").det_fpr1.mean()))
        xs = np.arange(len(methods)) + dx
        ax.errorbar(xs, [p[0] for p in pts], yerr=[p[1] for p in pts], fmt=mk, color=col, ms=5.5,
                    mfc=col if role == "unseen" else SURF, mec=col, mew=1.1, elinewidth=0.8, capsize=2,
                    label=lab, zorder=3)
        if role == "unseen":
            for x, p in zip(xs, pts):
                ax.text(x + 0.13, p[0], f"{p[0]:.2f}", fontsize=6.6, va="center", color=INK)
    ax.set_xticks(range(len(methods))); ax.set_xticklabels([m[1] for m in methods], rotation=20, ha="right")
    ax.set_xlim(-0.5, len(methods) - 0.3); ax.set_ylim(0, 1.06)
    ax.set_title(title, loc="left", fontsize=8.2, weight="bold")
    style(ax)
axes[0].set_ylabel("ENS detection at 1% FPR")
axes[0].legend(loc="lower left", fontsize=7, handletextpad=0.3)
fig.tight_layout(w_pad=0.8)
save(fig, "fig4_feature_selection")

# ---------------- Figure 3: AUROC vs detection at 1% FPR ----------------
fig, ax = plt.subplots(figsize=(3.5, 3.3))
ax.plot([0.6, 1], [0.6, 1], color="#c9c8c2", lw=1.0, ls="--", zorder=1)
ax.fill_between([0.9, 1.01], -0.02, 0.3, color="#f3f2ee", zorder=0, lw=0)
for ds, title in REL:
    u = R[ds][(R[ds].role == "unseen") & (R[ds].fs == "all") & (R[ds].model.isin(["RF", "XGB", "ENS"]))]
    g = u.groupby(["heldout", "model"])[["auroc", "det_fpr1"]].mean()
    ax.scatter(g.auroc, g.det_fpr1, s=22, color=RELC[ds], ec=SURF, lw=0.7, label=title, zorder=3)
ax.set_xlim(0.6, 1.01); ax.set_ylim(-0.02, 1.02)
allpts = pd.concat([R[d][(R[d].role == "unseen") & (R[d].fs == "all") & (R[d].model.isin(["RF", "XGB", "ENS"]))]
                    .groupby(["heldout", "model"])[["auroc", "det_fpr1"]].mean() for d, _ in REL])
n_hi = int(((allpts.auroc >= 0.9) & (allpts.det_fpr1 <= 0.3)).sum())
ax.annotate(f"{n_hi} of {len(allpts)} cases with\nAUROC >= 0.9 but\ndetection <= 0.3 (shaded)",
            xy=(0.905, 0.22), xytext=(0.615, 0.36), fontsize=6.3, color=INK2, va="center",
            arrowprops=dict(arrowstyle="-|>", color=INK2, lw=0.6, mutation_scale=6))
fig.canvas.draw()
p1, p2 = ax.transData.transform([(0.62, 0.62), (0.7, 0.7)])
ang = np.degrees(np.arctan2(p2[1] - p1[1], p2[0] - p1[0]))
ax.text(0.655, 0.6, "detection = AUROC", rotation=ang, rotation_mode="anchor", fontsize=6.4, color=INK2)
ax.set_xlabel("AUROC (unseen family vs. benign)")
ax.set_ylabel("Detection at 1% FPR")
ax.xaxis.grid(True, color=GRID, lw=0.6)
style(ax)
ax.legend(loc="upper left", bbox_to_anchor=(0.0, 1.0), fontsize=6.4, handletextpad=0.2, title="RF, XGB, ENS per held-out family", title_fontsize=6.2, alignment="left")
save(fig, "fig3_auroc_vs_fpr")
print("saved to", OUT)

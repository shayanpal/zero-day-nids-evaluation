import os
import numpy as np
import pandas as pd
from scipy import stats

# Paper tables with 95% CIs and paired tests (Holm-corrected per table and dataset).
# Unit of analysis: the seed (mean over held-out families within a seed), as in Zaro (2026);
# a Wilcoxon test over (seed, held-out family) pairs is reported as a secondary test.

D = os.path.expanduser("~/thesis/loao")
OUT = os.path.join(D, "tables")
os.makedirs(OUT, exist_ok=True)
DATASETS = ["cic2017", "cic2018", "cic2017i"]


def read(path):
    return pd.read_csv(path) if os.path.exists(path) else None


main = {ds: read(os.path.join(D, f"results_{ds}.csv")) for ds in DATASETS}
pit = {ds: read(os.path.join(D, f"pitfalls_{ds}.csv")) for ds in DATASETS}
noisy18 = read(os.path.join(D, "old_2018_with_infiltration", "results_cic2018.csv"))


def ci(x):
    x = np.asarray(x, float)
    m = x.mean()
    if len(x) < 2:
        return m, np.nan
    return m, stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))


def holm(p):
    p = np.asarray(p, float)
    out = np.full_like(p, np.nan)
    ok = ~np.isnan(p)
    m = int(ok.sum())
    if m == 0:
        return out
    pv = p[ok]
    idx = np.argsort(pv)
    adj = np.minimum(np.maximum.accumulate((m - np.arange(m)) * pv[idx]), 1.0)
    tmp = np.empty(m)
    tmp[idx] = adj
    out[ok] = tmp
    return out


def unseen(df, **flt):
    q = df[df.role == "unseen"]
    for k, v in flt.items():
        q = q[q[k] == v]
    return q.set_index(["seed", "heldout"])


def compare(a, b, metric="det_fpr1"):
    """a, b: unseen tables indexed by (seed, heldout). Returns stats of a - b on common units."""
    j = a[[metric]].join(b[[metric]], lsuffix="_a", rsuffix="_b", how="inner").dropna()
    if j.empty:
        return None
    d_unit = j[f"{metric}_a"] - j[f"{metric}_b"]
    per_seed = d_unit.groupby(level="seed").mean()
    ma, _ = ci(j[f"{metric}_a"].groupby(level="seed").mean())
    mb, _ = ci(j[f"{metric}_b"].groupby(level="seed").mean())
    md, hw = ci(per_seed)
    p_t = stats.ttest_1samp(per_seed, 0).pvalue if len(per_seed) > 1 and per_seed.std() > 0 else np.nan
    p_w = stats.wilcoxon(d_unit).pvalue if (d_unit != 0).sum() > 0 else np.nan
    return dict(A=ma, B=mb, delta=md, ci95=hw, p_t=p_t, p_wilcoxon=p_w,
                n_seeds=len(per_seed), n_units=len(d_unit), seeds_positive=int((per_seed > 0).sum()))


def finish(rows, name):
    t = pd.DataFrame(rows)
    if t.empty:
        print(f"[{name}] no data")
        return
    t["p_t_holm"] = np.nan
    for ds in t.dataset.unique():
        m = t.dataset == ds
        t.loc[m, "p_t_holm"] = holm(t.loc[m, "p_t"].to_numpy())
    num = ["A", "B", "delta", "ci95"]
    t[num] = t[num].round(3)
    for c in ("p_t", "p_t_holm", "p_wilcoxon"):
        t[c] = t[c].map(lambda v: f"{v:.2g}" if pd.notna(v) else "")
    t.to_csv(os.path.join(OUT, f"{name}.csv"), index=False)
    try:
        with open(os.path.join(OUT, f"{name}.md"), "w") as f:
            f.write(t.to_markdown(index=False))
    except ImportError:
        pass
    print(f"\n===== {name} =====")
    print(t.to_string(index=False))


# ---------- Table 1: evaluation pitfalls (inflation = pitfall - clean) ----------
rows = []
for ds in DATASETS:
    r, p = main[ds], pit[ds]
    for model in ("RF", "ENS"):
        if r is not None:
            ref = unseen(r, fs="all", model=model)
            pairs = [("shortcut features kept (all vs noshortcut)", ref, unseen(r, fs="noshortcut", model=model))]
            if (r.fs == "ga_seen").any():
                pairs.append(("held-out family visible to GA (ga_seen vs ga)",
                              unseen(r, fs="ga_seen", model=model), unseen(r, fs="ga", model=model)))
            if (r.fs == "ga_global").any():
                pairs.append(("thesis GA saw all families (ga_global vs ga)",
                              unseen(r, fs="ga_global", model=model), unseen(r, fs="ga", model=model)))
            if ds == "cic2018" and noisy18 is not None:
                pairs.append(("label-noisy family (Infiltration) in training",
                              unseen(noisy18, fs="all", model=model), ref))
            for name, a, b in pairs:
                res = compare(a, b)
                if res:
                    rows.append(dict(dataset=ds, pitfall=name, model=model, **res))
        if p is not None:
            clean = unseen(p, variant="clean", model=model)
            for v, name in (("thr_test", "threshold calibrated on test benign"),
                            ("dup", "no de-duplication")):
                res = compare(unseen(p, variant=v, model=model), clean)
                if res:
                    rows.append(dict(dataset=ds, pitfall=name, model=model, **res))
finish(rows, "table1_pitfalls")

# ---------- Table 2: feature selection on known attacks vs unseen detection ----------
rows = []
for ds in DATASETS:
    r = main[ds]
    if r is None:
        continue
    for model in ("RF", "XGB", "ENS"):
        ref = unseen(r, fs="all", model=model)
        for fs in ("ga", "mi", "rfimp"):
            res = compare(unseen(r, fs=fs, model=model), ref)
            if not res:
                continue
            kn = r[(r.role == "known") & (r.model == model)]
            k_fs = kn[kn.fs == fs].groupby("seed")["det_fpr1"].mean().mean()
            k_all = kn[kn.fs == "all"].groupby("seed")["det_fpr1"].mean().mean()
            rows.append(dict(dataset=ds, fs=fs, model=model, **res, known_fs=round(k_fs, 3),
                             known_all=round(k_all, 3)))
finish(rows, "table2_feature_selection")

# ---------- Table 3: cascade vs supervised ensemble ----------
rows = []
for ds in DATASETS:
    r = main[ds]
    if r is None:
        continue
    for metric in ("det_fpr1", "det_fpr01"):
        res = compare(unseen(r, fs="all", model="CASCADE"), unseen(r, fs="all", model="ENS"), metric)
        if res:
            rows.append(dict(dataset=ds, comparison=f"CASCADE - ENS (unseen, {metric})", **res))
    rare = r[(r.role == "rare") & (r.fs == "all")]
    for fam in rare.eval_family.unique():
        for model in ("IF", "ENS", "CASCADE"):
            x = rare[(rare.eval_family == fam) & (rare.model == model)].groupby("seed")["det_fpr1"].mean()
            m, hw = ci(x)
            rows.append(dict(dataset=ds, comparison=f"rare {fam}: {model}", A=m, ci95=hw,
                             n_seeds=len(x), p_t=np.nan, p_wilcoxon=np.nan))
finish(rows, "table3_cascade")

# ---------- Table 4: per-family unseen detection (all features), mean +/- CI over seeds ----------
rows = []
for ds in DATASETS:
    r = main[ds]
    if r is None:
        continue
    u = r[(r.role == "unseen") & (r.fs == "all")]
    for (fold, model), g in u.groupby(["heldout", "model"]):
        m, hw = ci(g["det_fpr1"])
        rows.append(dict(dataset=ds, heldout=fold, model=model, det_fpr1=round(m, 3), ci95=round(hw, 3),
                         auroc=round(g["auroc"].mean(), 3), n_test=int(g["n"].mean())))
t4 = pd.DataFrame(rows)
if not t4.empty:
    t4.to_csv(os.path.join(OUT, "table4_per_family.csv"), index=False)
    print("\n===== table4_per_family =====")
    print(t4.pivot_table(index=["dataset", "heldout"], columns="model", values="det_fpr1").round(3).to_string())

print("\nTables written to", OUT)

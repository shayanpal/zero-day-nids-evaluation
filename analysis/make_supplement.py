"""Build supplementary tables S1, S3a and S5 (markdown + csv) from the per-seed result files.

Usage: python make_supplement.py <results_dir> <out_dir>
<results_dir> must contain results_<ds>.csv and pitfalls_<ds>.csv as written by loao.py / pitfalls.py.
"""
import os
import sys
import numpy as np
import pandas as pd
from scipy import stats

RES, OUT = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ("data", "out")
os.makedirs(OUT, exist_ok=True)
REL = [("cic2017", "CIC-IDS2017 (original)"), ("cic2017i", "CIC-IDS2017 (corrected)"),
       ("cic2018", "CSE-CIC-IDS2018 (original)")]
MODELS = ["RF", "XGB", "ENS", "IF", "CASCADE"]
FS = [("all", "All features"), ("noshortcut", "No shortcut fields"), ("ga", "GA (per fold)"),
      ("mi", "MI (per fold)"), ("rfimp", "RFimp (per fold)"), ("ga_seen", "GA (saw all families)"),
      ("mi_seen", "MI (saw all families)"), ("rfimp_seen", "RFimp (saw all families)"),
      ("ga_global", "Thesis GA")]


def ci(x):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    if len(x) == 0:
        return np.nan, np.nan
    if len(x) < 2:
        return x.mean(), np.nan
    return x.mean(), stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))


def fmt(m, h):
    if np.isnan(m):
        return "-"
    return f"{m:.3f}" if np.isnan(h) else f"{m:.3f} ± {h:.3f}"


def md(df):
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(str(v) for v in r.values) + " |")
    return "\n".join(lines)


def write(df, name, title):
    df.to_csv(os.path.join(OUT, f"{name}.csv"), index=False)
    with open(os.path.join(OUT, f"{name}.md"), "w") as f:
        f.write(f"### {title}\n\n{md(df)}\n")
    print(f"[ok] {name}: {len(df)} rows")


R = {ds: pd.read_csv(os.path.join(RES, f"results_{ds}.csv")) for ds, _ in REL}
P = {ds: pd.read_csv(os.path.join(RES, f"pitfalls_{ds}.csv")) for ds, _ in REL
     if os.path.exists(os.path.join(RES, f"pitfalls_{ds}.csv"))}

# ---------- S1: per held-out family, per model, per seed (all features) ----------
for ds, title in REL:
    r = R[ds][R[ds].fs == "all"]
    rows = []
    for fam in sorted(r.heldout.unique()):
        for m in MODELS:
            q = r[(r.heldout == fam) & (r.model == m)]
            u = q[q.role == "unseen"].set_index("seed")
            kn = q[q.role == "known"].groupby("seed").det_fpr1.mean()
            row = {"Held-out family": fam, "Model": m}
            for s in range(5):
                row[f"seed {s}"] = f"{u.det_fpr1.get(s, np.nan):.3f}"
            row["Mean ± 95% CI"] = fmt(*ci(u.det_fpr1))
            row["AUROC"] = f"{u.auroc.mean():.3f}"
            row["Known families"] = f"{kn.mean():.3f}"
            row["Test FPR"] = f"{u.test_fpr1.mean():.4f}"
            row["n test"] = int(u.n.mean())
            rows.append(row)
    write(pd.DataFrame(rows), f"S1_{ds}", f"S1 ({title}): unseen-family detection at 1% FPR, all features")

# ---------- S1 (rare families) ----------
rows = []
for ds, title in REL:
    r = R[ds][(R[ds].fs == "all") & (R[ds].role == "rare")]
    for fam in sorted(r.eval_family.unique()):
        for m in MODELS:
            q = r[(r.eval_family == fam) & (r.model == m)]
            per_seed = q.groupby("seed").det_fpr1.mean()
            per_seed01 = q.groupby("seed").det_fpr01.mean()
            rows.append({"Release": title, "Rare family": fam, "Model": m, "n": int(q.n.mean()),
                         "Detection at 1% FPR": fmt(*ci(per_seed)),
                         "Detection at 0.1% FPR": fmt(*ci(per_seed01))})
write(pd.DataFrame(rows), "S1_rare", "S1 (rare families, never trained on): detection, mean over folds within a seed")

# ---------- S1 (per family, every feature-selection method, ENS) ----------
rows = []
for ds, title in REL:
    r = R[ds][(R[ds].role == "unseen") & (R[ds].model == "ENS")]
    for fam in sorted(r.heldout.unique()):
        row = {"Release": title, "Held-out family": fam}
        for fs, lab in FS:
            q = r[(r.heldout == fam) & (r.fs == fs)]
            row[lab] = fmt(*ci(q.det_fpr1)) if len(q) else "n/a"
        rows.append(row)
write(pd.DataFrame(rows), "S1_fs_by_family", "S1 (ENS, unseen family): detection at 1% FPR by feature-selection method")

# ---------- S3a: number of selected features per fold ----------
rows = []
for ds, title in REL:
    r = R[ds][R[ds].model == "ENS"]
    for fs, lab in FS:
        q = r[r.fs == fs]
        if q.empty:
            continue
        k = q.groupby("heldout").n_feats.first()
        rows.append({"Release": title, "Method": lab, **{f: int(v) for f, v in k.items()}})
s3 = pd.DataFrame(rows).astype(object).where(lambda d: d.notna(), "-")
for c in s3.columns[2:]:
    s3[c] = s3[c].map(lambda v: v if v == "-" else str(int(v)))
write(s3, "S3_k", "S3a: number of features used per held-out fold")

# ---------- S5: every configuration at 1% and 0.1% FPR ----------
rows = []
for ds, title in REL:
    r = R[ds]
    for fs, lab in FS:
        for m in MODELS:
            q = r[(r.fs == fs) & (r.model == m)]
            if q.empty:
                continue
            u = q[q.role == "unseen"].groupby("seed")
            kn = q[q.role == "known"].groupby("seed")
            rows.append({"Release": title, "Features": lab, "Model": m,
                         "Unseen @1%": fmt(*ci(u.det_fpr1.mean())), "Unseen @0.1%": fmt(*ci(u.det_fpr01.mean())),
                         "Known @1%": fmt(*ci(kn.det_fpr1.mean())), "Known @0.1%": fmt(*ci(kn.det_fpr01.mean())),
                         "Test FPR @0.1%": f"{q[q.role == 'unseen'].test_fpr01.mean():.4f}"})
    if ds in P:
        p = P[ds]
        for v, lab in (("clean", "Pitfall run: clean"), ("thr_test", "Pitfall run: threshold on test"),
                       ("dup", "Pitfall run: no de-duplication")):
            for m in ("RF", "ENS"):
                q = p[(p.variant == v) & (p.model == m)]
                if q.empty:
                    continue
                u = q[q.role == "unseen"].groupby("seed")
                kn = q[q.role == "known"].groupby("seed")
                rows.append({"Release": title, "Features": lab, "Model": m,
                             "Unseen @1%": fmt(*ci(u.det_fpr1.mean())), "Unseen @0.1%": fmt(*ci(u.det_fpr01.mean())),
                             "Known @1%": fmt(*ci(kn.det_fpr1.mean())), "Known @0.1%": fmt(*ci(kn.det_fpr01.mean())),
                             "Test FPR @0.1%": f"{q[q.role == 'unseen'].test_fpr01.mean():.4f}"})
write(pd.DataFrame(rows), "S5_all_configs", "S5: mean detection over held-out families (mean ± 95% CI over 5 seeds)")
print("done ->", OUT)

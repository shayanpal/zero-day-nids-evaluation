import os
import sys
import json
import time
import argparse
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import roc_auc_score
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from loao_common import load, split, MAIN, RARE, SHORTCUTS, OUT_DIR, HOME

# Leave-one-attack-family-out evaluation at a fixed false-positive rate.
# Thresholds are set ONLY on the benign validation split (never on test data).
# One CSV row per (seed, held-out family, feature set, model, evaluated family).

ap = argparse.ArgumentParser()
ap.add_argument("dataset", choices=["cic2017", "cic2018", "cic2017i"])
ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
ap.add_argument("--fs", nargs="+", default=["all", "noshortcut", "ga", "mi", "rfimp", "ga_global"])
ap.add_argument("--models", nargs="+", default=["RF", "XGB", "ENS", "CASCADE", "IF"])
args = ap.parse_args()

FPRS = {"fpr1": 0.01, "fpr01": 0.001}
os.makedirs(OUT_DIR, exist_ok=True)
out_csv = os.path.join(OUT_DIR, f"results_{args.dataset}.csv")
done = set()
if os.path.exists(out_csv):
    prev = pd.read_csv(out_csv)
    done = set(zip(prev["seed"], prev["heldout"], prev["fs"], prev["model"]))

df, feats = load(args.dataset)
X_all = df[feats].to_numpy()
fam_all = df["Family"].to_numpy().astype(object)
print(f"{args.dataset}: {len(df):,} rows, {len(feats)} features", flush=True)

fs_path = os.path.join(OUT_DIR, f"fs_{args.dataset}.json")
fs_sel = json.load(open(fs_path)) if os.path.exists(fs_path) else {}
ga_global_path = os.path.join(HOME, "thesis", "data", "processed_v2", "selected_features.json")
ga_global = json.load(open(ga_global_path)) if (args.dataset == "cic2017" and os.path.exists(ga_global_path)) else None


def columns(fs, fold):
    if fs == "all":
        return feats
    if fs == "noshortcut":
        return [c for c in feats if c not in SHORTCUTS[args.dataset]]
    if fs == "ga_global":
        return ga_global
    if fs.endswith("_seen"):
        return fs_sel.get("_all", {}).get(fs[:-5])
    if fs in ("ga", "mi", "rfimp"):
        return fs_sel.get(fold, {}).get(fs)
    raise ValueError(fs)


def ix(cols):
    return [feats.index(c) for c in cols]


def fit_score(model, Xtr, ytr, parts):
    """Train a binary detector; return attack scores for every evaluation part."""
    if model == "RF":   # Zaro (2026) configuration
        clfs = [RandomForestClassifier(n_estimators=100, class_weight="balanced", n_jobs=-1, random_state=0)]
    elif model == "XGB":  # Zaro (2026) configuration
        clfs = [XGBClassifier(n_estimators=300, max_depth=8, tree_method="hist", n_jobs=-1,
                              random_state=0, eval_metric="logloss")]
    elif model == "ENS":  # thesis stage-1 ensemble (soft voting)
        clfs = [RandomForestClassifier(n_estimators=150, max_depth=18, n_jobs=-1, random_state=0),
                XGBClassifier(n_estimators=150, max_depth=8, tree_method="hist", n_jobs=-1,
                              random_state=0, eval_metric="logloss"),
                LGBMClassifier(n_estimators=150, max_depth=8, n_jobs=-1, random_state=0, verbosity=-1,
                               deterministic=True, force_row_wise=True)]
    else:
        raise ValueError(model)
    for c in clfs:
        c.fit(Xtr, ytr)
    return {k: np.mean([c.predict_proba(v)[:, 1] for c in clfs], axis=0) for k, v in parts.items()}


def thresholds(s_val):
    return {k: np.quantile(s_val, 1 - f) for k, f in FPRS.items()}


def cascade_thresholds(s1_val, s2_val, fpr, share1=0.5):
    """Stage 1 gets share1 of the alert budget; stage 2 fills the rest among stage-1 negatives."""
    t1 = np.quantile(s1_val, 1 - fpr * share1)
    flag1 = s1_val > t1
    n2 = int(np.floor(fpr * len(s1_val))) - int(flag1.sum())
    rest = np.sort(s2_val[~flag1])[::-1]
    t2 = np.inf if n2 <= 0 else rest[min(n2, len(rest) - 1)]
    return t1, t2


def emit(rows, seed, fold, fs, ncols, model, pred_fn, s_parts, roles):
    """pred_fn(part_name, fpr_key) -> boolean predictions; s_parts used for AUROC."""
    ben = s_parts["benign_test"]
    test_fpr = {k: float(pred_fn("benign_test", k).mean()) for k in FPRS}
    for name, role in roles.items():
        s = s_parts[name]
        y = np.r_[np.zeros(len(ben)), np.ones(len(s))]
        auroc = roc_auc_score(y, np.r_[ben, s]) if len(s) else np.nan
        row = dict(dataset=args.dataset, seed=seed, heldout=fold, fs=fs, n_feats=ncols, model=model,
                   eval_family=name, role=role, n=len(s), auroc=auroc,
                   test_fpr1=test_fpr["fpr1"], test_fpr01=test_fpr["fpr01"])
        for k in FPRS:
            row[f"det_{k}"] = float(pred_fn(name, k).mean()) if len(s) else np.nan
        rows.append(row)


for seed in args.seeds:
    sp = split(df, args.dataset, seed)
    t_seed = time.time()

    # Benign-only Isolation Forest on all features: independent of the held-out family
    iso = IsolationForest(n_estimators=200, n_jobs=-1, random_state=seed).fit(X_all[sp["train"]["Benign"]])
    def iso_score(idx):
        return -iso.score_samples(X_all[idx])
    iso_parts = {"val": iso_score(sp["val"]), "benign_test": iso_score(sp["test"]["Benign"])}
    for f, idx in {**sp["test"], **sp["rare"]}.items():
        if f != "Benign":
            iso_parts[f] = iso_score(idx)

    for fold in MAIN[args.dataset]:
        if fold not in sp["test"]:
            continue
        known = [f for f in sp["train"] if f not in ("Benign", fold)]
        tr_idx = np.concatenate([sp["train"]["Benign"]] + [sp["train"][f] for f in known])
        y_tr = (fam_all[tr_idx] != "Benign").astype(int)
        roles = {fold: "unseen", **{f: "known" for f in known}, **{f: "rare" for f in sp["rare"]}}
        part_idx = {"val": sp["val"], "benign_test": sp["test"]["Benign"],
                    **{f: (sp["test"][f] if f in sp["test"] else sp["rare"][f]) for f in roles}}
        rows = []

        if "IF" in args.models and (seed, fold, "all", "IF") not in done:
            th = thresholds(iso_parts["val"])
            emit(rows, seed, fold, "all", len(feats), "IF",
                 lambda n, k: iso_parts[n] > th[k], iso_parts, roles)

        for fs in args.fs:
            cols = columns(fs, fold)
            if not cols:
                print(f"  [seed {seed} | {fold} | {fs}] no feature list, skipped", flush=True)
                continue
            c = ix(cols)
            Xtr = X_all[tr_idx][:, c]
            parts = {k: X_all[v][:, c] for k, v in part_idx.items()}
            ens_scores = None
            for model in ("RF", "XGB", "ENS"):
                need = model in args.models and (seed, fold, fs, model) not in done
                need_cascade = (model == "ENS" and "CASCADE" in args.models
                                and (seed, fold, fs, "CASCADE") not in done)
                if not (need or need_cascade):
                    continue
                t0 = time.time()
                s = fit_score(model, Xtr, y_tr, parts)
                if need:
                    th = thresholds(s["val"])
                    emit(rows, seed, fold, fs, len(cols), model, lambda n, k: s[n] > th[k], s, roles)
                if model == "ENS":
                    ens_scores = s
                print(f"  [seed {seed} | {fold} | {fs} ({len(cols)}) | {model}] {time.time()-t0:.0f}s", flush=True)

            if "CASCADE" in args.models and ens_scores is not None and (seed, fold, fs, "CASCADE") not in done:
                ct = {k: cascade_thresholds(ens_scores["val"], iso_parts["val"], f) for k, f in FPRS.items()}
                # AUROC for the cascade uses the stage-1 score (cascade has no single score)
                emit(rows, seed, fold, fs, len(cols), "CASCADE",
                     lambda n, k: (ens_scores[n] > ct[k][0]) | (iso_parts[n] > ct[k][1]), ens_scores, roles)

        if rows:
            pd.DataFrame(rows).to_csv(out_csv, mode="a", header=not os.path.exists(out_csv), index=False)
            unseen = [r for r in rows if r["role"] == "unseen"]
            summary = ", ".join(f"{r['fs']}/{r['model']}={r['det_fpr1']:.3f}" for r in unseen)
            print(f"[seed {seed} | held-out {fold}] unseen det@1%FPR: {summary}", flush=True)
    print(f"=== seed {seed} done in {(time.time()-t_seed)/60:.1f} min ===", flush=True)

print("ALL DONE ->", out_csv)

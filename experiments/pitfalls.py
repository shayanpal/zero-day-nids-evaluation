import os
import sys
import time
import argparse
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from loao_common import load, split, MAIN, FAM2017, OUT_DIR, HOME

# Controlled pitfall ablation under the same LOAO protocol (all features):
#   clean    : de-duplicated data, threshold from benign VALIDATION flows (reference)
#   thr_test : same models, threshold from benign TEST flows (test-set calibration)
#   dup      : data WITHOUT de-duplication / conflict removal, threshold from validation
# Other pitfalls (shortcut features, held-out family visible to feature selection,
# label-noisy family in training) come from the main LOAO runs.

ap = argparse.ArgumentParser()
ap.add_argument("dataset", choices=["cic2017", "cic2018", "cic2017i"])
ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
ap.add_argument("--models", nargs="+", default=["RF", "ENS"])
ap.add_argument("--variants", nargs="+", default=["clean", "thr_test", "dup"])
args = ap.parse_args()

FPRS = {"fpr1": 0.01, "fpr01": 0.001}
out_csv = os.path.join(OUT_DIR, f"pitfalls_{args.dataset}.csv")
done = set()
if os.path.exists(out_csv):
    prev = pd.read_csv(out_csv)
    done = set(zip(prev["variant"], prev["seed"], prev["heldout"], prev["model"]))


def load_dup(dataset):
    if dataset == "cic2017":
        d = os.path.join(HOME, "thesis", "data", "processed")   # thesis v1 data (no de-duplication)
        df = pd.concat([pd.read_parquet(os.path.join(d, f"{p}.parquet")) for p in ("train", "test")],
                       ignore_index=True)
        df = df[[c for c in df.columns if not c.startswith("__index_level")]]
        df["Label"] = df["Label"].astype(str).str.strip()
        df["Family"] = df["Label"].map(FAM2017)
    else:
        df = pd.read_parquet(os.path.join(HOME, "thesis", "data_2018", "processed", "ids2018_withdup.parquet"))
    unmapped = df.loc[df["Family"].isna(), "Label"].unique().tolist()
    assert not unmapped, f"Unmapped labels: {unmapped}"
    feats = [c for c in df.columns if c not in ("Label", "Family")]
    df[feats] = df[feats].astype(np.float32)
    return df, feats


def fit_score(model, Xtr, ytr, parts):
    if model == "RF":
        clfs = [RandomForestClassifier(n_estimators=100, class_weight="balanced", n_jobs=-1, random_state=0)]
    elif model == "ENS":
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


def rows_for(variant, seed, fold, model, s, roles, thr_source):
    th = {k: np.quantile(s[thr_source], 1 - f) for k, f in FPRS.items()}
    ben = s["benign_test"]
    out = []
    for name, role in roles.items():
        x = s[name]
        y = np.r_[np.zeros(len(ben)), np.ones(len(x))]
        r = dict(dataset=args.dataset, variant=variant, seed=seed, heldout=fold, model=model,
                 eval_family=name, role=role, n=len(x),
                 auroc=roc_auc_score(y, np.r_[ben, x]) if len(x) else np.nan,
                 test_fpr1=float((ben > th["fpr1"]).mean()), test_fpr01=float((ben > th["fpr01"]).mean()))
        for k in FPRS:
            r[f"det_{k}"] = float((x > th[k]).mean()) if len(x) else np.nan
        out.append(r)
    return out


def run(variants, df, feats):
    X_all = df[feats].to_numpy()
    fam_all = df["Family"].to_numpy().astype(object)
    for seed in args.seeds:
        sp = split(df, args.dataset, seed)
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
            for model in args.models:
                todo = [v for v in variants if (v, seed, fold, model) not in done]
                if not todo:
                    continue
                t0 = time.time()
                s = fit_score(model, X_all[tr_idx], y_tr, {k: X_all[v] for k, v in part_idx.items()})
                for v in todo:
                    rows += rows_for(v, seed, fold, model, s, roles, "benign_test" if v == "thr_test" else "val")
                print(f"  [{'/'.join(todo)} | seed {seed} | {fold} | {model}] {time.time()-t0:.0f}s", flush=True)
            if rows:
                pd.DataFrame(rows).to_csv(out_csv, mode="a", header=not os.path.exists(out_csv), index=False)
                summ = ", ".join(f"{r['variant']}/{r['model']}={r['det_fpr1']:.3f}" for r in rows if r["role"] == "unseen")
                print(f"[seed {seed} | held-out {fold}] unseen det@1%: {summ}", flush=True)


clean_like = [v for v in args.variants if v in ("clean", "thr_test")]
if clean_like:
    df, feats = load(args.dataset)
    print(f"[clean data] {len(df):,} rows, {len(feats)} features", flush=True)
    run(clean_like, df, feats)
    del df
if "dup" in args.variants:
    df, feats = load_dup(args.dataset)
    print(f"[data with duplicates] {len(df):,} rows, {len(feats)} features", flush=True)
    run(["dup"], df, feats)
print("ALL DONE ->", out_csv)

import os
import sys
import json
import time
import random
import argparse
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import mutual_info_classif
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from loao_common import load, split, MAIN, OUT_DIR

# Per-fold feature selection: for each held-out family, GA / MI / RF-importance are run
# on seed-0 training data WITHOUT that family, so the selection never sees the unseen attack.

ap = argparse.ArgumentParser()
ap.add_argument("dataset", choices=["cic2017", "cic2018", "cic2017i"])
ap.add_argument("--pop", type=int, default=30)
ap.add_argument("--gens", type=int, default=60)
ap.add_argument("--patience", type=int, default=10)
args = ap.parse_args()

os.makedirs(OUT_DIR, exist_ok=True)
out_path = os.path.join(OUT_DIR, f"fs_{args.dataset}.json")
result = json.load(open(out_path)) if os.path.exists(out_path) else {}

df, feats = load(args.dataset)
sp = split(df, args.dataset, seed=0)
N = len(feats)
print(f"{args.dataset}: {len(df):,} rows, {N} features", flush=True)


def run_ga(Xtr, ytr, Xva, yva, fit_labels, seed=0):
    random.seed(seed)
    np.random.seed(seed)
    cache = {}

    def fitness(c):
        key = c.tobytes()
        if key not in cache:
            sel = np.flatnonzero(c)
            if len(sel) == 0:
                cache[key] = (0.0, 0.0)
            else:
                clf = RandomForestClassifier(n_estimators=30, max_depth=16, n_jobs=-1, random_state=seed)
                clf.fit(Xtr[:, sel], ytr)
                f1 = f1_score(yva, clf.predict(Xva[:, sel]), labels=fit_labels, average="macro", zero_division=0)
                cache[key] = (0.9 * f1 + 0.1 * (1 - len(sel) / N), f1)
        return cache[key][0]

    def rand_c():
        c = np.random.randint(0, 2, N)
        if c.sum() == 0:
            c[random.randrange(N)] = 1
        return c

    def mutate(c):
        for i in range(N):
            if random.random() < 0.02:
                c[i] = 1 - c[i]
        if c.sum() == 0:
            c[random.randrange(N)] = 1
        return c

    def tourn(pop, fits):
        ids = random.sample(range(len(pop)), 3)
        return pop[max(ids, key=lambda i: fits[i])].copy()

    pop = [rand_c() for _ in range(args.pop)]
    best, best_c, stall, gen = -1.0, None, 0, 0
    for gen in range(1, args.gens + 1):
        fits = [fitness(c) for c in pop]
        i = int(np.argmax(fits))
        if fits[i] > best:
            best, best_c, stall = fits[i], pop[i].copy(), 0
        else:
            stall += 1
        print(f"    gen {gen:02d} best {best:.4f} (macroF1 {cache[best_c.tobytes()][1]:.4f}, "
              f"{int(best_c.sum())} feats) stall {stall}", flush=True)
        if stall >= args.patience:
            break
        order = np.argsort(fits)[::-1]
        new = [pop[j].copy() for j in order[:3]]
        while len(new) < args.pop:
            p1, p2 = tourn(pop, fits), tourn(pop, fits)
            if random.random() < 0.8:
                pt = random.randint(1, N - 1)
                p1, p2 = np.concatenate([p1[:pt], p2[pt:]]), np.concatenate([p2[:pt], p1[pt:]])
            new.append(mutate(p1))
            if len(new) < args.pop:
                new.append(mutate(p2))
        pop = new
    return best_c, best, cache[best_c.tobytes()][1], gen


for fold in MAIN[args.dataset] + ["_all"]:
    if fold in result:
        print(f"[{fold}] already done, skipping", flush=True)
        continue
    t0 = time.time()
    fams = [f for f in sp["train"] if f != fold]
    idx = np.concatenate([sp["train"][f] for f in fams])
    X = df[feats].to_numpy()[idx]
    lab = df["Label"].to_numpy()[idx].astype(object)
    famv = df["Family"].to_numpy()[idx].astype(object)
    # very small fine-grained labels are merged into the largest label of the same family
    # (or the family name if none), and classes still below 4 rows are dropped
    vc = pd.Series(lab).value_counts()
    fam_of = dict(zip(lab, famv))
    remap = {}
    for l in vc[vc < 10].index:
        big = [m for m in vc.index if fam_of[m] == fam_of[l] and vc[m] >= 10]
        remap[l] = big[0] if big else fam_of[l]
    lab = np.array([remap.get(l, l) for l in lab], dtype=object)
    vc2 = pd.Series(lab).value_counts()
    keep = ~np.isin(lab, list(vc2[vc2 < 4].index))
    X, lab = X[keep], lab[keep]
    le = LabelEncoder()
    y = le.fit_transform(lab)
    Xtr, Xva, ytr, yva = train_test_split(X, y, test_size=0.25, stratify=y, random_state=0)
    vcv = pd.Series(yva).value_counts()
    fit_labels = sorted(int(c) for c in vcv[vcv >= 10].index)
    print(f"[{fold}] held out | GA data: train {Xtr.shape}, val {Xva.shape}, "
          f"{len(le.classes_)} classes ({len(fit_labels)} in fitness)", flush=True)

    best_c, best_fit, best_f1, gens = run_ga(Xtr, ytr, Xva, yva, fit_labels)
    ga = [feats[i] for i in np.flatnonzero(best_c)]
    k = len(ga)

    sub = np.random.RandomState(0).choice(len(Xtr), size=min(60_000, len(Xtr)), replace=False)
    mi = mutual_info_classif(Xtr[sub], ytr[sub], random_state=0)
    mi_top = [feats[i] for i in np.argsort(mi)[::-1][:k]]

    rf = RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=0).fit(Xtr, ytr)
    rf_top = [feats[i] for i in np.argsort(rf.feature_importances_)[::-1][:k]]

    result[fold] = {"k": k, "ga": ga, "mi": mi_top, "rfimp": rf_top,
                    "ga_fitness": round(best_fit, 4), "ga_val_macroF1": round(best_f1, 4),
                    "ga_generations": gens, "minutes": round((time.time() - t0) / 60, 1)}
    json.dump(result, open(out_path, "w"), indent=2)
    print(f"[{fold}] done in {(time.time()-t0)/60:.1f} min | k={k} | GA: {ga}", flush=True)

print("ALL FOLDS DONE ->", out_path)

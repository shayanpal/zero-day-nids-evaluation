import os
import glob
import json
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import f1_score

# CSE-CIC-IDS2018 (original CICFlowMeter CSVs) -> cleaned, de-duplicated table with families.
# Memory-aware: files are read in chunks and de-duplicated per chunk before the global pass.
# No train/test split here: splits are made per seed / per LOAO fold later.

src_dir = os.path.expanduser("~/thesis/data_2018")
out_dir = os.path.join(src_dir, "processed")
os.makedirs(out_dir, exist_ok=True)

# Identifier columns (only present in the Thuesday-20-02 file, plus Timestamp everywhere)
ID_COLS = ["Flow ID", "Src IP", "Src Port", "Dst IP", "Timestamp"]

report = {"raw_rows": 0, "header_rows_removed": 0, "nan_inf_rows_removed": 0, "per_file": {}}
parts = []
feat_cols = None

for path in sorted(glob.glob(os.path.join(src_dir, "*.csv"))):
    name = os.path.basename(path)
    n_raw = n_kept = 0
    for chunk in pd.read_csv(path, chunksize=500_000, low_memory=False, dtype=str):
        chunk.columns = chunk.columns.str.strip()
        n_raw += len(chunk)
        hdr = chunk["Label"].astype(str).str.strip() == "Label"       # repeated header rows
        report["header_rows_removed"] += int(hdr.sum())
        chunk = chunk[~hdr].drop(columns=[c for c in ID_COLS if c in chunk.columns])
        if feat_cols is None:
            feat_cols = [c for c in chunk.columns if c != "Label"]
        assert [c for c in chunk.columns if c != "Label"] == feat_cols, f"Column mismatch in {name}"
        y = chunk["Label"].astype(str).str.strip()
        X = chunk[feat_cols].apply(pd.to_numeric, errors="coerce").astype(np.float64)
        X = X.replace([np.inf, -np.inf], np.nan)
        ok = X.notna().all(axis=1).to_numpy()
        report["nan_inf_rows_removed"] += int((~ok).sum())
        X = X[ok].astype(np.float32)
        y = y[ok]
        part = X.copy()
        part["Label"] = y.to_numpy()
        part["_h"] = pd.util.hash_pandas_object(X, index=False).to_numpy()
        part = part.drop_duplicates(subset=["_h", "Label"])           # within-chunk dedup
        n_kept += len(part)
        parts.append(part)
    report["raw_rows"] += n_raw
    report["per_file"][name] = {"raw": n_raw, "after_chunk_dedup": n_kept}
    print(f"{name}: raw {n_raw:,}, kept after chunk-level dedup {n_kept:,}", flush=True)

df = pd.concat(parts, ignore_index=True)
del parts
print(f"\nRows after chunk-level dedup: {len(df):,}", flush=True)

# Label conflicts (same feature vector, different labels), then global exact duplicates
n_lab = df.groupby("_h")["Label"].nunique()
conflict = n_lab[n_lab > 1].index
conf_mask = df["_h"].isin(conflict)
report["conflict_vectors"] = int(len(conflict))
report["conflict_rows_removed"] = int(conf_mask.sum())
report["conflict_rows_by_label"] = df.loc[conf_mask, "Label"].value_counts().to_dict()
df = df[~conf_mask]
before = len(df)
df = df.drop_duplicates(subset="_h").drop(columns="_h").reset_index(drop=True)
report["global_duplicates_removed"] = before - len(df)
report["unique_rows"] = len(df)

const = [c for c in feat_cols if df[c].nunique() <= 1]
df = df.drop(columns=const)
feat_cols = [c for c in feat_cols if c not in const]
report["constant_columns_removed"] = const
report["n_features"] = len(feat_cols)

FAMILY = {
    "Benign": "Benign",
    "DoS attacks-Hulk": "DoS", "DoS attacks-SlowHTTPTest": "DoS",
    "DoS attacks-GoldenEye": "DoS", "DoS attacks-Slowloris": "DoS",
    "DDOS attack-HOIC": "DDoS", "DDoS attacks-LOIC-HTTP": "DDoS", "DDOS attack-LOIC-UDP": "DDoS",
    "FTP-BruteForce": "BruteForce", "SSH-Bruteforce": "BruteForce",
    "Bot": "Botnet",
    "Brute Force -Web": "WebAttack", "Brute Force -XSS": "WebAttack", "SQL Injection": "WebAttack",
    "Infilteration": "Infiltration",
}
df["Family"] = df["Label"].map(FAMILY)
unmapped = df.loc[df["Family"].isna(), "Label"].unique().tolist()
assert not unmapped, f"Unmapped labels: {unmapped}"

report["unique_per_label"] = df["Label"].value_counts().to_dict()
report["unique_per_family"] = df["Family"].value_counts().to_dict()

print(f"\nHeader rows removed: {report['header_rows_removed']:,}")
print(f"NaN/Inf rows removed: {report['nan_inf_rows_removed']:,}")
print(f"Conflicting vectors: {len(conflict):,} ({report['conflict_rows_removed']:,} rows)")
print(f"Global duplicates removed: {report['global_duplicates_removed']:,}")
print(f"Unique rows: {len(df):,} | features: {len(feat_cols)} | constant removed: {const}")
print("\nUnique rows per label:")
print(df["Label"].value_counts().to_string())
print("\nUnique rows per family:")
print(df["Family"].value_counts().to_string())

# Shortcut check: single-column predictiveness for FAMILY (300k stratified sample)
print("\n=== Single-column predictiveness (family, top 15) ===", flush=True)
rng = np.random.RandomState(42)
y_all = df["Family"].astype(str).to_numpy(dtype=object)
frac = min(1.0, 300000 / len(df))
idx = []
for lab in np.unique(y_all):
    pos = np.flatnonzero(y_all == lab)
    k = max(10, int(round(len(pos) * frac)))
    idx.extend(rng.choice(pos, size=min(k, len(pos)), replace=False))
idx = np.sort(np.array(idx))
yy = y_all[idx]
cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
res = []
for c in feat_cols:
    x = df[c].to_numpy()[idx].reshape(-1, 1)
    pred = cross_val_predict(DecisionTreeClassifier(max_depth=8, random_state=42), x, yy, cv=cv)
    res.append((c, round(f1_score(yy, pred, average="macro"), 4)))
res.sort(key=lambda t: -t[1])
for c, v in res[:15]:
    print(f"{c:35s} {v:.4f}")
report["single_column_top15"] = dict(res[:15])

df.to_parquet(os.path.join(out_dir, "ids2018_clean.parquet"), index=False)
with open(os.path.join(out_dir, "preprocess_report.json"), "w") as f:
    json.dump(report, f, indent=2, default=int)
print(f"\nSaved {len(df):,} rows x {len(feat_cols)} features to {out_dir}")

import os, glob, json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

SEED = 42
data_dir = os.path.expanduser("~/thesis/data")
out_dir = os.path.expanduser("~/thesis/data/processed_v2")
os.makedirs(out_dir, exist_ok=True)
report = {}

# ---- Load and basic cleaning (same as v1) ----
csv_files = sorted(glob.glob(os.path.join(data_dir, "*.csv")))
df = pd.concat([pd.read_csv(f, low_memory=False) for f in csv_files], ignore_index=True)
df.columns = df.columns.str.strip()
if "Fwd Header Length.1" in df.columns:
    df = df.drop(columns=["Fwd Header Length.1"])
df["Label"] = df["Label"].str.replace("\ufffd", "-", regex=False).str.strip()
report["raw_rows"] = len(df)

df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.dropna(inplace=True)
report["after_nan_inf"] = len(df)
print(f"After NaN/Inf removal: {len(df):,}", flush=True)

feat = [c for c in df.columns if c != "Label"]
h = pd.util.hash_pandas_object(df[feat], index=False).values
df["_h"] = h

# ---- Remove feature vectors that carry more than one label ----
n_lab = df.groupby("_h")["Label"].nunique()
conflict_h = n_lab[n_lab > 1].index
conf_mask = df["_h"].isin(conflict_h)
report["conflict_vectors"] = int(len(conflict_h))
report["conflict_rows_removed"] = int(conf_mask.sum())
report["conflict_rows_by_label"] = df.loc[conf_mask, "Label"].value_counts().to_dict()
df = df[~conf_mask]
print(f"Conflicting vectors: {len(conflict_h):,}, rows removed: {conf_mask.sum():,}", flush=True)

# ---- Remove exact duplicates BEFORE any split ----
before = len(df)
df = df.drop_duplicates(subset="_h").drop(columns="_h")
report["duplicates_removed"] = before - len(df)
report["after_dedup"] = len(df)
print(f"Duplicates removed: {before - len(df):,}, remaining: {len(df):,}", flush=True)
report["class_counts_after_dedup"] = df["Label"].value_counts().to_dict()

# ---- Hold out unseen-attack families ----
zero_day = ["Infiltration", "Heartbleed", "Web Attack - XSS"]
zd_df = df[df["Label"].isin(zero_day)]
pool = df[~df["Label"].isin(zero_day)]

small = pool["Label"].value_counts()
small = small[small < 10]
if len(small):
    print(f"WARNING: very small classes: {small.to_dict()}", flush=True)

# ---- 70 / 10 / 20 stratified split ----
train_df, test_df = train_test_split(pool, test_size=0.20, stratify=pool["Label"], random_state=SEED)
train_df, val_df = train_test_split(train_df, test_size=0.125, stratify=train_df["Label"], random_state=SEED)
test_df = pd.concat([test_df, zd_df], ignore_index=True)

# ---- Sanity check: no overlap between splits ----
def hs(d): return set(pd.util.hash_pandas_object(d[feat], index=False).values)
htr, hva, hte = hs(train_df), hs(val_df), hs(test_df)
report["overlap_train_test"] = len(htr & hte)
report["overlap_train_val"] = len(htr & hva)
report["overlap_val_test"] = len(hva & hte)

for name, d in [("train", train_df), ("val", val_df), ("test", test_df)]:
    report[f"{name}_rows"] = len(d)
    report[f"{name}_counts"] = d["Label"].value_counts().to_dict()
    d.to_parquet(os.path.join(out_dir, f"{name}.parquet"), index=False)

with open(os.path.join(out_dir, "preprocess_report.json"), "w") as f:
    json.dump(report, f, indent=2, default=int)

print("\n=== SUMMARY ===")
for k in ["raw_rows", "after_nan_inf", "conflict_rows_removed", "duplicates_removed",
          "after_dedup", "train_rows", "val_rows", "test_rows",
          "overlap_train_test", "overlap_train_val", "overlap_val_test"]:
    print(f"{k}: {report[k]:,}")
print("\nTest counts:")
print(test_df["Label"].value_counts().to_string())
print(f"\nSaved to {out_dir}")

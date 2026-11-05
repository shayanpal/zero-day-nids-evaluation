import os
import pandas as pd
import numpy as np

data_dir = os.path.expanduser("~/thesis/data/processed")
train = pd.read_parquet(os.path.join(data_dir, "train.parquet"))
test = pd.read_parquet(os.path.join(data_dir, "test.parquet"))

feat = [c for c in train.columns if c != "Label" and not c.startswith("__index_level")]

def row_hash(df):
    return pd.util.hash_pandas_object(df[feat], index=False).values

h_tr = row_hash(train)
h_te = row_hash(test)

print("=== 1) Duplicates inside each split ===")
print(f"train: {len(train):,} rows, duplicated rows: {pd.Series(h_tr).duplicated().sum():,}")
print(f"test : {len(test):,} rows, duplicated rows: {pd.Series(h_te).duplicated().sum():,}")

print("\n=== 2) Test rows whose exact features also appear in train (leakage) ===")
in_train = np.isin(h_te, h_tr)
print(f"overall: {in_train.sum():,} / {len(test):,} ({100*in_train.mean():.2f}%)")
res = pd.DataFrame({"Label": test["Label"].values, "in_train": in_train})
per_class = res.groupby("Label")["in_train"].agg(["sum", "count"])
per_class["pct"] = (100 * per_class["sum"] / per_class["count"]).round(2)
print(per_class.sort_values("pct", ascending=False).to_string())

print("\n=== 3) Same features, different labels (label conflicts) ===")
allh = pd.DataFrame({"h": np.concatenate([h_tr, h_te]),
                     "Label": np.concatenate([train["Label"].values, test["Label"].values])})
n_labels = allh.groupby("h")["Label"].nunique()
conf = n_labels[n_labels > 1]
print(f"feature vectors with >1 label: {len(conf):,}")
if len(conf):
    sub = allh[allh["h"].isin(conf.index)]
    print(sub.groupby("Label").size().sort_values(ascending=False).head(15).to_string())

print("\n=== 4) Zero-day rows identical to some training row ===")
for zd in ["Infiltration", "Heartbleed", "Web Attack - XSS"]:
    m = (test["Label"] == zd).values
    print(f"{zd}: {in_train[m].sum()} / {m.sum()} identical to a training row")

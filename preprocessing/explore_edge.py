import os
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import f1_score

# Read-only exploration of Edge-IIoTset (DNN version). Writes nothing except the log.

path = os.path.expanduser("~/thesis/data_edge/DNN-EdgeIIoT-dataset.csv")
df = pd.read_csv(path, low_memory=False)
df.columns = df.columns.str.strip()
print(f"Shape: {df.shape}", flush=True)

print("\n=== Attack_type counts ===")
print(df["Attack_type"].value_counts().to_string())
print("\n=== Attack_label counts ===")
print(df["Attack_label"].value_counts().to_string())

feat = [c for c in df.columns if c not in ("Attack_label", "Attack_type")]

print("\n=== Column profile ===")
rows = []
for c in feat:
    s = df[c]
    rows.append({"col": c, "dtype": str(s.dtype), "nunique": s.nunique(dropna=False),
                 "pct_null": round(100 * s.isna().mean(), 2),
                 "sample": str(s.dropna().astype(str).unique()[:3].tolist())[:60]})
prof = pd.DataFrame(rows)
print(prof.to_string(index=False))

# Single-column predictiveness: a shallow tree on ONE column at a time.
# Very high macro-F1 from a column that is an identifier (time, IP, checksum,
# stream index, sequence number) indicates a shortcut feature.
print("\n=== Single-column predictiveness (depth-8 tree, 3-fold CV, 300k stratified sample) ===", flush=True)
rng = np.random.RandomState(42)
y_all = df["Attack_type"].astype(str).to_numpy(dtype=object)
frac = min(1.0, 300000 / len(df))
idx = []
for lab in np.unique(y_all):
    pos = np.flatnonzero(y_all == lab)
    k = max(3, int(round(len(pos) * frac)))
    idx.extend(rng.choice(pos, size=min(k, len(pos)), replace=False))
idx = np.sort(np.array(idx))
sub = df.iloc[idx]
y = y_all[idx]
cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
res = []
for c in feat:
    s = sub[c]
    if not pd.api.types.is_numeric_dtype(s):
        x = pd.factorize(s.astype(str).to_numpy(dtype=object))[0].reshape(-1, 1)
    else:
        x = s.fillna(-1).to_numpy().reshape(-1, 1)
    pred = cross_val_predict(DecisionTreeClassifier(max_depth=8, random_state=42), x, y, cv=cv)
    res.append({"col": c, "macroF1_alone": round(f1_score(y, pred, average="macro"), 4)})
res = pd.DataFrame(res).sort_values("macroF1_alone", ascending=False)
print(res.to_string(index=False))

# Duplicates after removing obvious identifier columns
obvious_ids = ["frame.time", "ip.src_host", "ip.dst_host", "arp.src.proto_ipv4", "arp.dst.proto_ipv4",
               "icmp.transmit_timestamp", "tcp.checksum", "icmp.checksum", "tcp.ack_raw", "udp.stream",
               "mbtcp.trans_id", "tcp.srcport", "tcp.dstport", "udp.port"]
keep = [c for c in feat if c not in obvious_ids]
h = pd.util.hash_pandas_object(df[keep].astype(str), index=False)
print(f"\n=== Duplicates after dropping obvious identifier columns ({len(obvious_ids)}) ===")
print(f"duplicated rows: {h.duplicated().sum():,} / {len(df):,}")
tmp = pd.DataFrame({"h": h.to_numpy(), "y": y_all})
nlab = tmp.groupby("h")["y"].nunique()
print(f"feature vectors with >1 Attack_type: {(nlab > 1).sum():,}")
dup_by_class = tmp[tmp["h"].duplicated(keep="first")]["y"].value_counts()
print("duplicate rows by class:")
print(dup_by_class.to_string())

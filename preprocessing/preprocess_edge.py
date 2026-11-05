import os
import json
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import f1_score

# Edge-IIoTset (DNN version) -> cleaned, de-duplicated table with attack families.
# No train/test split here: splits are made per seed / per LOAO fold later.

src = os.path.expanduser("~/thesis/data_edge/DNN-EdgeIIoT-dataset.csv")
out_dir = os.path.expanduser("~/thesis/data_edge/processed")
os.makedirs(out_dir, exist_ok=True)
report = {}

df = pd.read_csv(src, low_memory=False)
df.columns = df.columns.str.strip()
report["raw_rows"] = len(df)

# 1) Columns removed, with the reason recorded for the paper
DROP = {
    # time / host identifiers
    "frame.time": "timestamp", "ip.src_host": "host id", "ip.dst_host": "host id",
    "arp.src.proto_ipv4": "host id", "arp.dst.proto_ipv4": "host id",
    "icmp.transmit_timestamp": "timestamp",
    # ports
    "tcp.srcport": "port", "tcp.dstport": "port", "udp.port": "port",
    # sequence numbers, stream indices, checksums
    "tcp.seq": "sequence number", "tcp.ack": "sequence number", "tcp.ack_raw": "sequence number",
    "icmp.seq_le": "sequence number", "udp.stream": "stream index", "mbtcp.trans_id": "transaction id",
    "tcp.checksum": "checksum", "icmp.checksum": "checksum",
    # raw payload / free text (signature-like, high cardinality)
    "tcp.payload": "raw payload", "tcp.options": "raw options string", "http.file_data": "raw payload",
    "http.request.full_uri": "raw URI", "http.request.uri.query": "raw URI", "mqtt.msg": "raw payload",
    "dns.qry.name": "mis-parsed column",
}
report["dropped_columns"] = DROP
df = df.drop(columns=[c for c in DROP if c in df.columns])

# 2) Low-cardinality categorical columns -> one-hot (normalise '0' / '0.0' / NaN)
CAT = ["http.request.method", "http.referer", "http.request.version", "dns.qry.name.len",
       "mqtt.conack.flags", "mqtt.protoname", "mqtt.topic"]
CAT = [c for c in CAT if c in df.columns]
for c in CAT:
    s = df[c].astype(str).str.strip()
    df[c] = s.replace({"0.0": "0", "nan": "0", "": "0"})
df = pd.get_dummies(df, columns=CAT, prefix=CAT, dtype=np.uint8)

labels = ["Attack_label", "Attack_type"]
feat = [c for c in df.columns if c not in labels]
for c in feat:
    if not pd.api.types.is_numeric_dtype(df[c]):
        df[c] = pd.to_numeric(df[c], errors="coerce")
df[feat] = df[feat].fillna(0)

const = [c for c in feat if df[c].nunique() <= 1]
df = df.drop(columns=const)
feat = [c for c in feat if c not in const]
report["constant_columns_removed"] = const
report["n_features"] = len(feat)
print(f"Features after cleaning: {len(feat)} (constant removed: {const})", flush=True)

# 3) Remove feature vectors that carry more than one label, then exact duplicates
h = pd.util.hash_pandas_object(df[feat], index=False).to_numpy()
df["_h"] = h
n_lab = df.groupby("_h")["Attack_type"].nunique()
conflict = n_lab[n_lab > 1].index
conf_mask = df["_h"].isin(conflict)
report["conflict_vectors"] = int(len(conflict))
report["conflict_rows_removed"] = int(conf_mask.sum())
df = df[~conf_mask]
before = len(df)
df = df.drop_duplicates(subset="_h").drop(columns="_h").reset_index(drop=True)
report["duplicates_removed"] = before - len(df)
report["unique_rows"] = len(df)
print(f"Conflicting vectors: {len(conflict):,} ({conf_mask.sum():,} rows); "
      f"duplicates removed: {before - len(df):,}; unique rows: {len(df):,}", flush=True)

# 4) Attack families (Ferrag et al., 2022 grouping)
FAMILY = {
    "Normal": "Normal",
    "DDoS_UDP": "DDoS", "DDoS_ICMP": "DDoS", "DDoS_TCP": "DDoS", "DDoS_HTTP": "DDoS",
    "SQL_injection": "Injection", "XSS": "Injection", "Uploading": "Injection",
    "Backdoor": "Malware", "Password": "Malware", "Ransomware": "Malware",
    "Port_Scanning": "Scanning", "Vulnerability_scanner": "Scanning", "Fingerprinting": "Scanning",
    "MITM": "MITM",
}
df["Family"] = df["Attack_type"].map(FAMILY)
assert df["Family"].notna().all(), f"Unmapped labels: {df.loc[df['Family'].isna(), 'Attack_type'].unique()}"
report["unique_per_type"] = df["Attack_type"].value_counts().to_dict()
report["unique_per_family"] = df["Family"].value_counts().to_dict()
print("\nUnique rows per attack type:")
print(df["Attack_type"].value_counts().to_string())
print("\nUnique rows per family:")
print(df["Family"].value_counts().to_string())

# 5) Shortcut re-check on the cleaned feature set (same test as explore_edge.py)
print("\n=== Single-column predictiveness after cleaning (top 15) ===", flush=True)
rng = np.random.RandomState(42)
y_all = df["Attack_type"].astype(str).to_numpy(dtype=object)
frac = min(1.0, 300000 / len(df))
idx = []
for lab in np.unique(y_all):
    pos = np.flatnonzero(y_all == lab)
    k = max(3, int(round(len(pos) * frac)))
    idx.extend(rng.choice(pos, size=min(k, len(pos)), replace=False))
idx = np.sort(np.array(idx))
y = y_all[idx]
cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
res = []
for c in feat:
    x = df[c].to_numpy()[idx].reshape(-1, 1)
    pred = cross_val_predict(DecisionTreeClassifier(max_depth=8, random_state=42), x, y, cv=cv)
    res.append((c, round(f1_score(y, pred, average="macro"), 4)))
res.sort(key=lambda t: -t[1])
for c, v in res[:15]:
    print(f"{c:45s} {v:.4f}")
report["single_column_top15"] = dict(res[:15])

df.to_parquet(os.path.join(out_dir, "edge_clean.parquet"), index=False)
with open(os.path.join(out_dir, "preprocess_report.json"), "w") as f:
    json.dump(report, f, indent=2, default=int)
print(f"\nSaved {len(df):,} rows x {len(feat)} features to {out_dir}")

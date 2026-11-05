import os
import glob
import json
import numpy as np
import pandas as pd

# Improved CIC-IDS2017 (Liu et al., CNS 2022) -> cleaned, de-duplicated table with families.
# "Attempted" flows are relabelled BENIGN (dataset authors' recommendation, as in Zaro 2026).
# "Attempted Category" is derived from the label and is dropped (it would leak the label).

src = os.path.expanduser("~/thesis/data_2017_improved")
out_dir = os.path.join(src, "processed")
os.makedirs(out_dir, exist_ok=True)
report = {}

DROP = ["id", "Flow ID", "Src IP", "Src Port", "Dst IP", "Timestamp", "Attempted Category"]
FAMILY = {
    "BENIGN": "Benign",
    "DoS Hulk": "DoS", "DoS GoldenEye": "DoS", "DoS Slowloris": "DoS", "DoS Slowhttptest": "DoS",
    "DDoS": "DDoS", "Portscan": "PortScan",
    "FTP-Patator": "BruteForce", "SSH-Patator": "BruteForce",
    "Botnet": "Botnet",
    "Web Attack - Brute Force": "WebAttack", "Web Attack - XSS": "WebAttack",
    "Web Attack - SQL Injection": "WebAttack",
    "Infiltration": "Infiltration", "Heartbleed": "Heartbleed",
    "Infiltration - Portscan": "InfilPortscan",
}

parts = []
for f in sorted(glob.glob(os.path.join(src, "*.csv"))):
    d = pd.read_csv(f, low_memory=False)
    d.columns = d.columns.str.strip()
    parts.append(d)
    print(f"{os.path.basename(f)}: {len(d):,} rows", flush=True)
df = pd.concat(parts, ignore_index=True)
del parts
report["raw_rows"] = len(df)

lab = df["Label"].astype(str).str.strip()
attempted = lab.str.endswith("- Attempted")
report["attempted_relabelled_benign"] = int(attempted.sum())
lab = lab.where(~attempted, "BENIGN")
df = df.drop(columns=[c for c in DROP if c in df.columns])
df["Label"] = lab

feat = [c for c in df.columns if c != "Label"]
df[feat] = df[feat].apply(pd.to_numeric, errors="coerce")
df[feat] = df[feat].replace([np.inf, -np.inf], np.nan)
before = len(df)
df = df.dropna()
report["nan_inf_removed"] = before - len(df)
df[feat] = df[feat].astype(np.float32)

h = pd.util.hash_pandas_object(df[feat], index=False).to_numpy()
df["_h"] = h
n_lab = df.groupby("_h")["Label"].nunique()
conflict = n_lab[n_lab > 1].index
conf = df["_h"].isin(conflict)
report["conflict_vectors"] = int(len(conflict))
report["conflict_rows_removed"] = int(conf.sum())
report["conflict_rows_by_label"] = df.loc[conf, "Label"].value_counts().to_dict()
df = df[~conf]
before = len(df)
df = df.drop_duplicates(subset="_h").drop(columns="_h").reset_index(drop=True)
report["duplicates_removed"] = before - len(df)
report["unique_rows"] = len(df)

const = [c for c in feat if df[c].nunique() <= 1]
df = df.drop(columns=const)
report["constant_columns_removed"] = const
report["n_features"] = len(feat) - len(const)

df["Family"] = df["Label"].map(FAMILY)
unmapped = df.loc[df["Family"].isna(), "Label"].unique().tolist()
assert not unmapped, f"Unmapped labels: {unmapped}"
report["unique_per_label"] = df["Label"].value_counts().to_dict()
report["unique_per_family"] = df["Family"].value_counts().to_dict()

print(f"\nAttempted -> BENIGN: {report['attempted_relabelled_benign']:,}")
print(f"NaN/Inf removed: {report['nan_inf_removed']:,}")
print(f"Conflicting vectors: {len(conflict):,} ({report['conflict_rows_removed']:,} rows)")
print(f"Duplicates removed: {report['duplicates_removed']:,}")
print(f"Unique rows: {len(df):,} | features: {report['n_features']} | constant removed: {const}")
print("\nUnique rows per family:")
print(df["Family"].value_counts().to_string())

df.to_parquet(os.path.join(out_dir, "cic2017i_clean.parquet"), index=False)
with open(os.path.join(out_dir, "preprocess_report.json"), "w") as fh:
    json.dump(report, fh, indent=2, default=int)
print("\nSaved to", out_dir)

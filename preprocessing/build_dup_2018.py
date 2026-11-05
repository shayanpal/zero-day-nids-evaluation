import os
import glob
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

# CSE-CIC-IDS2018 WITHOUT de-duplication and WITHOUT label-conflict removal.
# Same cleaning otherwise (header rows, identifier columns, NaN/Inf) and the same
# feature columns as the clean table, so the only difference is the duplicates.

src_dir = os.path.expanduser("~/thesis/data_2018")
clean_path = os.path.join(src_dir, "processed", "ids2018_clean.parquet")
out_path = os.path.join(src_dir, "processed", "ids2018_withdup.parquet")

clean_cols = [c for c in pq.read_schema(clean_path).names if c not in ("Label", "Family")]
ID_COLS = ["Flow ID", "Src IP", "Src Port", "Dst IP", "Timestamp"]
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

parts = []
for path in sorted(glob.glob(os.path.join(src_dir, "*.csv"))):
    n = 0
    for chunk in pd.read_csv(path, chunksize=500_000, low_memory=False, dtype=str):
        chunk.columns = chunk.columns.str.strip()
        chunk = chunk[chunk["Label"].astype(str).str.strip() != "Label"]
        chunk = chunk.drop(columns=[c for c in ID_COLS if c in chunk.columns])
        y = chunk["Label"].astype(str).str.strip()
        X = chunk[clean_cols].apply(pd.to_numeric, errors="coerce").astype(np.float64)
        X = X.replace([np.inf, -np.inf], np.nan)
        ok = X.notna().all(axis=1).to_numpy()
        part = X[ok].astype(np.float32)
        part["Label"] = y[ok].to_numpy()
        parts.append(part)
        n += int(ok.sum())
    print(f"{os.path.basename(path)}: kept {n:,} rows (duplicates kept)", flush=True)

df = pd.concat(parts, ignore_index=True)
del parts
df["Family"] = df["Label"].map(FAMILY)
unmapped = df.loc[df["Family"].isna(), "Label"].unique().tolist()
assert not unmapped, f"Unmapped labels: {unmapped}"
print(f"\nTotal rows (with duplicates): {len(df):,}")
print(df["Family"].value_counts().to_string())
df.to_parquet(out_path, index=False)
print("Saved", out_path)

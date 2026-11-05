import os
import numpy as np
import pandas as pd

# Shared data loading and per-seed splitting for the LOAO experiments.
# Protocol follows Zaro (2026): per family 70/30 disjoint train/test pools,
# capped samples, benign validation (20% of benign train) used ONLY for thresholds.

HOME = os.path.expanduser("~")

FAM2017 = {
    "BENIGN": "Benign",
    "DoS Hulk": "DoS", "DoS GoldenEye": "DoS", "DoS slowloris": "DoS", "DoS Slowhttptest": "DoS",
    "DDoS": "DDoS", "PortScan": "PortScan",
    "FTP-Patator": "BruteForce", "SSH-Patator": "BruteForce",
    "Bot": "Botnet",
    "Web Attack - Brute Force": "WebAttack", "Web Attack - XSS": "WebAttack",
    "Web Attack - Sql Injection": "WebAttack",
    "Infiltration": "Infiltration", "Heartbleed": "Heartbleed",
}

MAIN = {
    "cic2017": ["DoS", "DDoS", "PortScan", "BruteForce", "Botnet", "WebAttack"],
    "cic2018": ["DoS", "DDoS", "BruteForce", "Botnet", "WebAttack"],
    "cic2017i": ["DoS", "DDoS", "PortScan", "BruteForce", "Botnet", "WebAttack"],
}
# Families too small to hold out: never trained on, always evaluated as unseen (report only)
RARE = {"cic2017": ["Infiltration", "Heartbleed"], "cic2018": ["Infiltration"],
        "cic2017i": ["Infiltration", "Heartbleed", "InfilPortscan"]}

# Known shortcut-prone fields (destination port, initial TCP window sizes)
SHORTCUTS = {
    "cic2017": ["Destination Port", "Init_Win_bytes_forward", "Init_Win_bytes_backward"],
    "cic2018": ["Dst Port", "Init Fwd Win Byts", "Init Bwd Win Byts"],
    "cic2017i": ["Dst Port", "FWD Init Win Bytes", "Bwd Init Win Bytes"],
}

SIZES = dict(benign_train=100_000, val_frac=0.2, benign_test=40_000, att_train=15_000, att_test=5_000)

OUT_DIR = os.path.join(HOME, "thesis", "loao")


def load(dataset):
    if dataset == "cic2017":
        d = os.path.join(HOME, "thesis", "data", "processed_v2")
        df = pd.concat([pd.read_parquet(os.path.join(d, f"{p}.parquet")) for p in ("train", "val", "test")],
                       ignore_index=True)
        df["Label"] = df["Label"].astype(str).str.strip()
        df["Family"] = df["Label"].map(FAM2017)
    elif dataset == "cic2018":
        df = pd.read_parquet(os.path.join(HOME, "thesis", "data_2018", "processed", "ids2018_clean.parquet"))
        df["Label"] = df["Label"].astype(str).str.strip()
    elif dataset == "cic2017i":
        df = pd.read_parquet(os.path.join(HOME, "thesis", "data_2017_improved", "processed", "cic2017i_clean.parquet"))
        df["Label"] = df["Label"].astype(str).str.strip()
    else:
        raise ValueError(dataset)
    unmapped = df.loc[df["Family"].isna(), "Label"].unique().tolist()
    assert not unmapped, f"Unmapped labels: {unmapped}"
    feats = [c for c in df.columns if c not in ("Label", "Family")]
    df[feats] = df[feats].astype(np.float32)
    return df, feats


def split(df, dataset, seed):
    """Return index arrays: train[family], test[family], val (benign), rare[family]."""
    rng = np.random.RandomState(seed)
    out = {"train": {}, "test": {}, "rare": {}, "val": None}
    groups = df.groupby("Family").indices
    for fam in sorted(groups):
        idx = rng.permutation(groups[fam])
        if fam in RARE[dataset]:
            out["rare"][fam] = idx
            continue
        ntr = int(round(0.7 * len(idx)))
        tr, te = idx[:ntr], idx[ntr:]
        if fam == "Benign":
            tr = tr[:SIZES["benign_train"]]
            nval = int(len(tr) * SIZES["val_frac"])
            out["val"] = tr[:nval]
            out["train"][fam] = tr[nval:]
            out["test"][fam] = te[:SIZES["benign_test"]]
        else:
            out["train"][fam] = tr[:SIZES["att_train"]]
            out["test"][fam] = te[:SIZES["att_test"]]
    return out

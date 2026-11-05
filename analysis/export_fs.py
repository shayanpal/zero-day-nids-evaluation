"""Export supplement S3 (selected features per fold) and S4 (software versions).

Run on the server inside the venv:  python export_fs.py
Writes ~/thesis/loao/tables/S3_features.md and ~/thesis/loao/tables/S4_versions.txt
"""
import os
import sys
import json
import platform
from importlib import metadata

D = os.path.expanduser("~/thesis/loao")
OUT = os.path.join(D, "tables")
os.makedirs(OUT, exist_ok=True)
REL = [("cic2017", "CIC-IDS2017 (original)"), ("cic2017i", "CIC-IDS2017 (corrected)"),
       ("cic2018", "CSE-CIC-IDS2018 (original)")]

lines = ["### S3b: features selected in each fold (seed-0 training data, held-out family excluded)", ""]
for ds, title in REL:
    p = os.path.join(D, f"fs_{ds}.json")
    if not os.path.exists(p):
        print(f"[missing] {p}")
        continue
    fs = json.load(open(p))
    lines += [f"#### {title}", "",
              "| Fold | k | GA val. macro-F1 | GA generations | GA | MI | RFimp |", "|---|---|---|---|---|---|---|"]
    for fold, r in fs.items():
        name = "all families (seen)" if fold == "_all" else f"{fold} held out"
        lines.append(f"| {name} | {r['k']} | {r.get('ga_val_macroF1', '')} | {r.get('ga_generations', '')} | "
                     f"{', '.join(r['ga'])} | {', '.join(r['mi'])} | {', '.join(r['rfimp'])} |")
    lines.append("")
    print(f"[ok] {ds}: {len(fs)} folds")

ga_v4 = os.path.expanduser("~/thesis/data/processed_v2/selected_features.json")
if os.path.exists(ga_v4):
    lines += ["#### Thesis GA (original CIC-IDS2017, saw all families)", "", "```", open(ga_v4).read().strip(), "```", ""]

open(os.path.join(OUT, "S3_features.md"), "w").write("\n".join(lines) + "\n")

pk = ["numpy", "pandas", "scipy", "scikit-learn", "xgboost", "lightgbm", "pyarrow", "matplotlib"]
v = [f"python {sys.version.split()[0]}", f"os {platform.platform()}", f"cpu_count {os.cpu_count()}"]
for p in pk:
    try:
        v.append(f"{p} {metadata.version(p)}")
    except metadata.PackageNotFoundError:
        v.append(f"{p} not installed")
try:
    mem = [l for l in open("/proc/meminfo") if l.startswith("MemTotal")][0].split()[1]
    v.append(f"ram_gb {int(mem) / 1024 ** 2:.0f}")
except Exception:
    pass
open(os.path.join(OUT, "S4_versions.txt"), "w").write("\n".join(v) + "\n")
print("\n".join(v))
print("written:", os.path.join(OUT, "S3_features.md"), "and", os.path.join(OUT, "S4_versions.txt"))

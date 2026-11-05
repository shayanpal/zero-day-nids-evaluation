import os
import sys
import pandas as pd

# Quick summary of LOAO results: mean over seeds.
ds = sys.argv[1] if len(sys.argv) > 1 else "cic2017"
r = pd.read_csv(os.path.expanduser(f"~/thesis/loao/results_{ds}.csv"))
pd.set_option("display.width", 200)
print(f"{ds}: {len(r):,} rows, seeds {sorted(int(s) for s in r.seed.unique())}\n")

u = r[r.role == "unseen"]
print("=== Unseen family: detection at 1% FPR (mean over seeds) ===")
t = u.pivot_table(index="heldout", columns=["fs", "model"], values="det_fpr1", aggfunc="mean")
t.loc["MEAN"] = t.mean()
print(t.round(3).T.to_string())

print("\n=== Unseen mean: det@1%, det@0.1%, AUROC, test FPR@1% ===")
print(u.groupby(["fs", "model"])[["det_fpr1", "det_fpr01", "auroc", "test_fpr1"]].mean().round(3).to_string())

k = r[r.role == "known"]
print("\n=== Known families: mean detection at 1% FPR ===")
print(k.groupby(["fs", "model"])["det_fpr1"].mean().round(3).to_string())

rare = r[r.role == "rare"]
if len(rare):
    print("\n=== Rare families (never trained on): detection at 1% FPR ===")
    print(rare.pivot_table(index=["fs", "model"], columns="eval_family", values="det_fpr1", aggfunc="mean")
          .round(3).to_string())

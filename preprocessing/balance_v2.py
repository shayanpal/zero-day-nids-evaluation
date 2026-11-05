import os
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler, TomekLinks

SEED = 42
d = os.path.expanduser("~/thesis/data/processed_v2")
train = pd.read_parquet(os.path.join(d, "train.parquet"))
val = pd.read_parquet(os.path.join(d, "val.parquet"))
test = pd.read_parquet(os.path.join(d, "test.parquet"))

feat = [c for c in train.columns if c != "Label"]
print(f"Features: {len(feat)}", flush=True)

le = LabelEncoder()
y_tr = le.fit_transform(train["Label"])
print("Known classes:", list(le.classes_), flush=True)

scaler = MinMaxScaler()
X_tr = scaler.fit_transform(train[feat])          # fit on train only
X_val = scaler.transform(val[feat])
X_te = scaler.transform(test[feat])

print(f"Before balancing: {X_tr.shape}", flush=True)
print(pd.Series(train["Label"]).value_counts().to_string(), flush=True)

benign = le.transform(["BENIGN"])[0]
rus = RandomUnderSampler(sampling_strategy={benign: 200000}, random_state=SEED)
X_u, y_u = rus.fit_resample(X_tr, y_tr)
print(f"After RUS: {X_u.shape}", flush=True)

counts = pd.Series(y_u).value_counts()
smote = SMOTE(sampling_strategy={c: max(n, 5000) for c, n in counts.items()}, random_state=SEED)
X_s, y_s = smote.fit_resample(X_u, y_u)
print(f"After SMOTE: {X_s.shape}", flush=True)

X_bal, y_bal = TomekLinks(n_jobs=-1).fit_resample(X_s, y_s)
print(f"After Tomek: {X_bal.shape}", flush=True)
print(pd.Series(le.inverse_transform(y_bal)).value_counts().to_string(), flush=True)

np.save(os.path.join(d, "X_train_bal.npy"), X_bal)
np.save(os.path.join(d, "y_train_bal.npy"), y_bal)
np.save(os.path.join(d, "X_val_scaled.npy"), X_val)
np.save(os.path.join(d, "X_test_scaled.npy"), X_te)
val[["Label"]].to_parquet(os.path.join(d, "y_val.parquet"), index=False)
test[["Label"]].to_parquet(os.path.join(d, "y_test.parquet"), index=False)
joblib.dump(scaler, os.path.join(d, "scaler.pkl"))
joblib.dump(le, os.path.join(d, "label_encoder.pkl"))

print(f"\nX_val range: [{X_val.min():.3f}, {X_val.max():.3f}]")
print(f"X_test range: [{X_te.min():.3f}, {X_te.max():.3f}]")
print("Saved to", d)

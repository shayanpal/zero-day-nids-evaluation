# Thesis v1 preprocessing (NO de-duplication, NO label-conflict removal).
# Used only to build the "no de-duplication" pitfall data (P6) for original CIC-IDS2017.
import pandas as pd
import numpy as np
import glob
import os
from sklearn.model_selection import train_test_split

data_dir = os.path.expanduser("~/thesis/data")
csv_files = sorted(glob.glob(os.path.join(data_dir, "*.csv")))

print("Loading and concatenating CSV files ...", flush=True)
df_list = []
for f in csv_files:
    df = pd.read_csv(f, low_memory=False)
    df.columns = df.columns.str.strip()
    df_list.append(df)
full_df = pd.concat(df_list, ignore_index=True)
print(f"Loaded: {full_df.shape}", flush=True)

# Drop the duplicated column
if "Fwd Header Length.1" in full_df.columns:
    full_df = full_df.drop(columns=["Fwd Header Length.1"])

# Clean labels (fix broken dash encoding)
full_df["Label"] = full_df["Label"].str.replace("�", "-", regex=False).str.strip()
print("\nClass distribution after cleaning:")
print(full_df["Label"].value_counts())

# Replace Inf with NaN, then drop rows with NaN
full_df.replace([np.inf, -np.inf], np.nan, inplace=True)
before = full_df.shape[0]
full_df.dropna(inplace=True)
print(f"\n{before - full_df.shape[0]} rows removed for NaN/Inf. Remaining: {full_df.shape[0]}")

# Set aside the zero-day classes
zero_day_classes = ["Infiltration", "Heartbleed", "Web Attack - XSS"]
zero_day_df = full_df[full_df["Label"].isin(zero_day_classes)]
train_pool_df = full_df[~full_df["Label"].isin(zero_day_classes)]

print(f"\nSamples set aside as zero-day: {zero_day_df.shape[0]}")
print(zero_day_df["Label"].value_counts())

# Stratified 80/20 train/test split of the rest
train_df, test_df = train_test_split(
    train_pool_df, test_size=0.2, stratify=train_pool_df["Label"], random_state=42
)

# Add zero-day samples to the test set only
test_df = pd.concat([test_df, zero_day_df], ignore_index=True)

print(f"\nFinal training set: {train_df.shape}")
print(f"Final test set (incl. zero-day): {test_df.shape}")

os.makedirs(os.path.expanduser("~/thesis/data/processed"), exist_ok=True)
train_df.to_parquet(os.path.expanduser("~/thesis/data/processed/train.parquet"))
test_df.to_parquet(os.path.expanduser("~/thesis/data/processed/test.parquet"))
print("\nSaved to ~/thesis/data/processed/")

# How Much Do Evaluation Choices Inflate Zero-Day Intrusion Detection?

Code, per-seed results and figures for the paper of the same title (Shayan Kheirabadi et al., under review).

The study measures how seven common evaluation choices change the detection of **unseen attack families** under a
leave-one-attack-family-out (LOAO) protocol with thresholds set on benign validation flows at a fixed 1% (and 0.1%)
false-positive rate, over five seeds, on the original and corrected CIC-IDS2017 releases and on CSE-CIC-IDS2018,
plus an audit of Edge-IIoTset.

## Repository layout

| Folder | Contents |
|---|---|
| `preprocessing/` | Cleaning of each release: identifier removal, NaN/Inf rows, label-conflicting vectors, duplicates |
| `experiments/` | Shared splits (`loao_common.py`), per-fold feature selection, the LOAO runs and the pitfall ablation |
| `analysis/` | Statistics (paper Tables 3-5), figures (Figures 1-4), supplementary tables (S1-S5) |
| `results/` | Per-seed result files (`results_<release>.csv`, `pitfalls_<release>.csv`), selected features (`fs_<release>.json`), tables |
| `figures/` | Paper figures (PDF and PNG) |

Release keys: `cic2017` = CIC-IDS2017 original, `cic2017i` = CIC-IDS2017 corrected (Liu et al., CNS 2022),
`cic2018` = CSE-CIC-IDS2018 original.

## Data

The datasets are not redistributed here. Download them from their authors:

| Release | Source | Expected location |
|---|---|---|
| CIC-IDS2017 (original, MachineLearningCVE CSVs) | <https://www.unb.ca/cic/datasets/ids-2017.html> | `~/thesis/data/*.csv` |
| CIC-IDS2017 (corrected) | <https://intrusion-detection.distrinet-research.be/CNS2022/> | `~/thesis/data_2017_improved/*.csv` |
| CSE-CIC-IDS2018 (original, Processed Traffic Data for ML Algorithms) | <https://www.unb.ca/cic/datasets/ids-2018.html> | `~/thesis/data_2018/*.csv` |
| Edge-IIoTset (DNN-EdgeIIoT-dataset.csv) | <https://ieee-dataport.org/documents/edge-iiotset-new-comprehensive-realistic-cyber-security-dataset-iot-and-iiot-applications> | `~/thesis/data_edge/` |

All scripts read and write under `~/thesis/` (results go to `~/thesis/loao/`).

## Environment

Python 3.10 or newer. Exact versions used for the paper are in `results/S4_versions.txt`.

```bash
python -m venv ~/thesis/venv && source ~/thesis/venv/bin/activate
pip install -r requirements.txt
```

## Reproducing the paper

Run from the repository root. Long steps are marked; all are resumable (finished folds are skipped).

```bash
# 1. Clean each release
python preprocessing/check_duplicates.py          # duplicate / conflict audit of original CIC-IDS2017
python preprocessing/preprocess_v2.py             # original CIC-IDS2017 -> ~/thesis/data/processed_v2
python preprocessing/preprocess_2017i.py          # corrected CIC-IDS2017
python preprocessing/preprocess_2018.py           # CSE-CIC-IDS2018 (reads files in chunks)
python preprocessing/preprocess_edge.py           # Edge-IIoTset audit (supplement S2)
python preprocessing/explore_edge.py              # single-field predictiveness (supplement S2.1)

# 2. Data for the pitfall runs
python preprocessing/preprocess_v1_nodedup.py     # original CIC-IDS2017 without de-duplication (P6)
python preprocessing/build_dup_2018.py            # CSE-CIC-IDS2018 without de-duplication (P6)
python preprocessing/balance_v2.py && python experiments/ga_v4.py   # thesis GA (P3), original CIC-IDS2017 only

# 3. Per-fold feature selection (long: hours per release)
for ds in cic2017 cic2017i cic2018; do python experiments/fs_per_fold.py $ds; done

# 4. LOAO runs and pitfall ablation (long)
for ds in cic2017 cic2017i cic2018; do python experiments/loao.py $ds; done
for ds in cic2017 cic2018; do python experiments/pitfalls.py $ds; done
# P4 (label-noisy family): run loao.py cic2018 with Infiltration in MAIN instead of RARE
# (loao_common.py) and keep the output in ~/thesis/loao/old_2018_with_infiltration/

# 5. Tables, figures, supplement
python analysis/stats.py                          # paper Tables 3-5 -> ~/thesis/loao/tables
python analysis/make_figs.py results figures      # Figures 1-4
python analysis/make_supplement.py results results/tables   # supplement S1, S3a, S5
python analysis/export_fs.py                      # supplement S3b (feature lists), S4 (versions)
```

## Where each paper result comes from

| Paper item | Script | File |
|---|---|---|
| Table 2 (cleaning) | `preprocessing/*` | `results/report_<release>.json` |
| Table 3 (pitfalls P1-P7) | `analysis/stats.py` | `results/tables/table1_pitfalls.*` |
| Table 4 (feature selection) | `analysis/stats.py` | `results/tables/table2_feature_selection.*` |
| Table 5 (cascade) | `analysis/stats.py` | `results/tables/table3_cascade.*` |
| Figures 1-4 | `analysis/make_figs.py` | `figures/` |
| Supplement S1, S3a, S5 | `analysis/make_supplement.py` | `results/tables/S*.md` |
| Supplement S3b, S4 | `analysis/export_fs.py` | `results/tables/S3_features.md`, `results/S4_versions.txt` |

## Result file format

`results_<release>.csv`: one row per (seed, held-out family, feature set, model, evaluated family) with
`role` (unseen, known, rare), `n` (test flows), `auroc`, `test_fpr1` / `test_fpr01` (measured benign test FPR) and
`det_fpr1` / `det_fpr01` (detection at the 1% / 0.1% threshold). `pitfalls_<release>.csv` has the same columns with
`variant` (clean, thr_test, dup) in place of the feature set.

## License

Code: MIT (see `LICENSE`). Result files and figures: CC BY 4.0.

## Citation

Please cite the paper (reference to be added on acceptance). See `CITATION.cff`.

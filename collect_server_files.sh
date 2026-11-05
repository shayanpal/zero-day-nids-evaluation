#!/usr/bin/env bash
# Run ONCE on the server from the repository root, inside the venv:
#   cd ~/thesis/release/zero-day-nids-evaluation && source ~/thesis/venv/bin/activate && bash collect_server_files.sh
# Copies the scripts and outputs that exist only on the server into the repository,
# then writes supplement S3b/S4. It only READS from ~/thesis; it writes only inside this folder.
set -u
T=~/thesis
OK=0; MISS=0

find_one() {  # first match for a file name under ~/thesis, excluding this release folder
  find "$T" -maxdepth 3 -name "$1" -not -path "*/release/*" -not -path "*/venv/*" 2>/dev/null | head -1
}
take() {      # take <file name> <destination>
  local src; src=$(find_one "$1")
  if [ -n "$src" ]; then cp "$src" "$2" && echo "[ok]   $src -> $2" && OK=$((OK+1))
  else echo "[MISS] $1 not found under $T" && MISS=$((MISS+1)); fi
}

echo "== scripts that ran on the server (server copy wins) =="
take check_duplicates.py preprocessing/check_duplicates.py
take preprocess_v2.py    preprocessing/preprocess_v2.py
take balance_v2.py       preprocessing/balance_v2.py
take ga_v4.py            experiments/ga_v4.py
for f in loao_common.py fs_per_fold.py loao.py pitfalls.py summarize.py; do
  [ -f "$T/loao_code/$f" ] && cp "$T/loao_code/$f" experiments/ && echo "[ok]   loao_code/$f" && OK=$((OK+1)) || { echo "[MISS] loao_code/$f"; MISS=$((MISS+1)); }
done
for f in preprocess_2017i.py build_dup_2018.py; do
  [ -f "$T/loao_code/$f" ] && cp "$T/loao_code/$f" preprocessing/ && echo "[ok]   loao_code/$f" && OK=$((OK+1))
done
[ -f "$T/loao_code/stats.py" ] && cp "$T/loao_code/stats.py" analysis/ && echo "[ok]   loao_code/stats.py"

echo "== results =="
for ds in cic2017 cic2017i cic2018; do
  for f in results_$ds.csv fs_$ds.json; do
    [ -f "$T/loao/$f" ] && cp "$T/loao/$f" results/ && echo "[ok]   loao/$f" && OK=$((OK+1)) || { echo "[MISS] loao/$f"; MISS=$((MISS+1)); }
  done
done
for ds in cic2017 cic2018; do
  [ -f "$T/loao/pitfalls_$ds.csv" ] && cp "$T/loao/pitfalls_$ds.csv" results/ && echo "[ok]   loao/pitfalls_$ds.csv" && OK=$((OK+1)) || { echo "[MISS] loao/pitfalls_$ds.csv"; MISS=$((MISS+1)); }
done
mkdir -p results/old_2018_with_infiltration
[ -f "$T/loao/old_2018_with_infiltration/results_cic2018.csv" ] && cp "$T/loao/old_2018_with_infiltration/results_cic2018.csv" results/old_2018_with_infiltration/ && echo "[ok]   P4 results (Infiltration trained)" && OK=$((OK+1)) || { echo "[MISS] old_2018_with_infiltration/results_cic2018.csv"; MISS=$((MISS+1)); }
[ -d "$T/loao/tables" ] && cp "$T"/loao/tables/table*.{csv,md} results/tables/ 2>/dev/null && echo "[ok]   paper tables from stats.py"
[ -f "$T/data/processed_v2/selected_features.json" ] && cp "$T/data/processed_v2/selected_features.json" results/thesis_ga_features.json && echo "[ok]   thesis GA features"

echo "== cleaning reports (Table 2) =="
for p in "data_2017_improved:cic2017i" "data_2018:cic2018" "data_edge:edge"; do
  d=${p%%:*}; k=${p##*:}
  [ -f "$T/$d/processed/preprocess_report.json" ] && cp "$T/$d/processed/preprocess_report.json" "results/report_$k.json" && echo "[ok]   report_$k.json"
done
r=$(find "$T/data/processed_v2" -maxdepth 1 -name "*report*.json" 2>/dev/null | head -1)
[ -n "$r" ] && cp "$r" results/report_cic2017.json && echo "[ok]   report_cic2017.json"

echo "== supplement S3b / S4 =="
python analysis/export_fs.py && cp "$T/loao/tables/S3_features.md" results/tables/ && cp "$T/loao/tables/S4_versions.txt" results/

echo "== safety check: no data files or Persian text in the repo =="
find . -type f \( -name "*.parquet" -o -name "*.npy" -o -name "*.pkl" \) -not -path "./.git/*" | head
python - <<'PY'
import glob, re
bad = [f for f in glob.glob("**/*.py", recursive=True) if re.search("[\u0600-\u06FF]", open(f, encoding="utf-8", errors="ignore").read())]
print("files with Persian text (translate before pushing):", bad if bad else "none")
PY
du -sh .
echo "DONE: $OK copied, $MISS missing"

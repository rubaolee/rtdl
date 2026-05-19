#!/usr/bin/env bash
set -euo pipefail

ROOT="${RTDL_ROOT:-$(pwd)}"
OPTIX_PREFIX="${OPTIX_PREFIX:-/root/vendor/optix-sdk}"
CUDA_PREFIX="${CUDA_PREFIX:-/usr/local/cuda-12}"
STEP_TIMEOUT_SECONDS="${STEP_TIMEOUT_SECONDS:-900}"
REPEAT="${REPEAT:-5}"
RADIUS="${RADIUS:-0.02}"
K_MAX="${K_MAX:-50}"
OUT_DIR="${OUT_DIR:-docs/reports/goal2384_native_prepared_frn3d_ranked_summary_pod}"
BASE_DIR="${BASE_DIR:-docs/reports/goal2368_rtnn_prepared_column_pod}"

cd "$ROOT"
mkdir -p "$OUT_DIR" "$BASE_DIR"

echo "[goal2384] build-optix start root=$ROOT optix=$OPTIX_PREFIX cuda=$CUDA_PREFIX"
timeout "$STEP_TIMEOUT_SECONDS" make build-optix OPTIX_PREFIX="$OPTIX_PREFIX" CUDA_PREFIX="$CUDA_PREFIX"
echo "[goal2384] build-optix done"

export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY="$ROOT/build/librtdl_optix.so"

echo "[goal2384] correctness probe"
python3 - <<'PY'
import json
from pathlib import Path
from rtdsl import optix_runtime as rt

search = [
    {"id": 10, "x": 0.0, "y": 0.0, "z": 0.0},
    {"id": 12, "x": 0.1, "y": 0.0, "z": 0.0},
    {"id": 11, "x": 0.2, "y": 0.0, "z": 0.0},
    {"id": 99, "x": 1.0, "y": 0.0, "z": 0.0},
]
queries = [
    {"id": 20, "x": 0.0, "y": 0.0, "z": 0.0},
    {"id": 21, "x": 0.19, "y": 0.0, "z": 0.0},
]
expected = [
    {
        "query_id": 20,
        "neighbor_count": 2,
        "nearest_neighbor_id": 10,
        "kth_neighbor_id": 12,
        "nearest_distance": 0.0,
        "kth_distance": 0.1,
        "sum_distance": 0.1,
    },
    {
        "query_id": 21,
        "neighbor_count": 2,
        "nearest_neighbor_id": 11,
        "kth_neighbor_id": 12,
        "nearest_distance": 0.010000000000000009,
        "kth_distance": 0.09,
        "sum_distance": 0.10000000000000002,
    },
]

prepared = rt.prepare_optix_fixed_radius_neighbors_3d(search, max_radius=0.25)
try:
    rows = prepared.run_ranked_summary(queries, radius=0.25, k_max=2)
finally:
    prepared.close()

ok = len(rows) == len(expected)
for got, exp in zip(rows, expected):
    for key in ("query_id", "neighbor_count", "nearest_neighbor_id", "kth_neighbor_id"):
        ok = ok and int(got[key]) == int(exp[key])
    for key in ("nearest_distance", "kth_distance", "sum_distance"):
        ok = ok and abs(float(got[key]) - float(exp[key])) < 1.0e-9

payload = {
    "ok": ok,
    "rows": rows,
    "expected": expected,
    "phase_timings": rt.get_last_fixed_radius_neighbors_3d_phase_timings(),
}
out = Path("docs/reports/goal2384_native_prepared_frn3d_ranked_summary_pod/ranked_summary_correctness_small.json")
out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
print(json.dumps(payload, indent=2, sort_keys=True), flush=True)
raise SystemExit(0 if ok else 1)
PY

for count in 65536 262144; do
  point_file="$BASE_DIR/uniform3d_${count}.csv"
  if [[ ! -f "$point_file" ]]; then
    echo "[goal2384] generate count=$count"
    timeout "$STEP_TIMEOUT_SECONDS" python3 scripts/goal2348_rtnn_v2_2_external_runner.py generate \
      --point-file "$point_file" \
      --point-count "$count" \
      --dimension 3 \
      --seed "$count" \
      --json-out "$OUT_DIR/generate_${count}.json"
  fi

  echo "[goal2384] ranked-summary count=$count repeat=$REPEAT"
  timeout "$STEP_TIMEOUT_SECONDS" python3 scripts/goal2348_rtnn_v2_2_external_runner.py run-rtdl-current-3d-neighbors-smoke \
    --point-file "$point_file" \
    --radius "$RADIUS" \
    --k-max "$K_MAX" \
    --input-mode packed-columns \
    --execution-mode native-prepared-optix \
    --repeat "$REPEAT" \
    --result-mode ranked-summary-raw \
    --row-label "rtdl_packed_native_prepared_optix_3d_ranked_summary_${count}_r002_k50" \
    --json-out "$OUT_DIR/rtdl_packed_native_prepared_optix_3d_ranked_summary_${count}_r002_k50.json"
done

python3 - <<'PY'
import json
from pathlib import Path

summary_dir = Path("docs/reports/goal2384_native_prepared_frn3d_ranked_summary_pod")
ranked_dir = Path("docs/reports/goal2381_native_prepared_frn3d_ranked_rows_pod")
old_dir = Path("docs/reports/goal2371_native_prepared_frn3d_pod")
for count in (65536, 262144):
    summary = json.loads((summary_dir / f"rtdl_packed_native_prepared_optix_3d_ranked_summary_{count}_r002_k50.json").read_text())
    ranked = json.loads((ranked_dir / f"rtdl_packed_native_prepared_optix_3d_ranked_rows_{count}_r002_k50.json").read_text())
    old = json.loads((old_dir / f"rtdl_packed_native_prepared_optix_3d_{count}_r002_k50.json").read_text())
    print(
        "[goal2384] summary",
        "count=", count,
        "ranked_summary_warm=", summary["elapsed_sec"],
        "ranked_rows_warm=", ranked["elapsed_sec"],
        "old_rows_warm=", old["elapsed_sec"],
        "ranked_rows/summary=", ranked["elapsed_sec"] / summary["elapsed_sec"] if summary["elapsed_sec"] else 0.0,
        "old/summary=", old["elapsed_sec"] / summary["elapsed_sec"] if summary["elapsed_sec"] else 0.0,
        "summary_rows=", summary["row_count"],
        "ranked_rows=", ranked["row_count"],
        "mode=", summary["phase_timings"]["mode"] if summary["phase_timings"] else None,
    )
PY

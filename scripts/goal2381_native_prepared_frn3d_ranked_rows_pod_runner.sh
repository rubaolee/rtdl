#!/usr/bin/env bash
set -euo pipefail

ROOT="${RTDL_ROOT:-$(pwd)}"
OPTIX_PREFIX="${OPTIX_PREFIX:-/root/vendor/optix-sdk}"
CUDA_PREFIX="${CUDA_PREFIX:-/usr/local/cuda-12}"
STEP_TIMEOUT_SECONDS="${STEP_TIMEOUT_SECONDS:-900}"
REPEAT="${REPEAT:-5}"
RADIUS="${RADIUS:-0.02}"
K_MAX="${K_MAX:-50}"
OUT_DIR="${OUT_DIR:-docs/reports/goal2381_native_prepared_frn3d_ranked_rows_pod}"
BASE_DIR="${BASE_DIR:-docs/reports/goal2368_rtnn_prepared_column_pod}"

cd "$ROOT"
mkdir -p "$OUT_DIR" "$BASE_DIR"

echo "[goal2381] build-optix start root=$ROOT optix=$OPTIX_PREFIX cuda=$CUDA_PREFIX"
timeout "$STEP_TIMEOUT_SECONDS" make build-optix OPTIX_PREFIX="$OPTIX_PREFIX" CUDA_PREFIX="$CUDA_PREFIX"
echo "[goal2381] build-optix done"

export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY="$ROOT/build/librtdl_optix.so"

for count in 65536 262144; do
  point_file="$BASE_DIR/uniform3d_${count}.csv"
  if [[ ! -f "$point_file" ]]; then
    echo "[goal2381] generate count=$count"
    timeout "$STEP_TIMEOUT_SECONDS" python3 scripts/goal2348_rtnn_v2_2_external_runner.py generate \
      --point-file "$point_file" \
      --point-count "$count" \
      --dimension 3 \
      --seed "$count" \
      --json-out "$OUT_DIR/generate_${count}.json"
  fi

  echo "[goal2381] ranked-rows count=$count repeat=$REPEAT"
  timeout "$STEP_TIMEOUT_SECONDS" python3 scripts/goal2348_rtnn_v2_2_external_runner.py run-rtdl-current-3d-neighbors-smoke \
    --point-file "$point_file" \
    --radius "$RADIUS" \
    --k-max "$K_MAX" \
    --input-mode packed-columns \
    --execution-mode native-prepared-optix \
    --repeat "$REPEAT" \
    --result-mode ranked-raw \
    --row-label "rtdl_packed_native_prepared_optix_3d_ranked_rows_${count}_r002_k50" \
    --json-out "$OUT_DIR/rtdl_packed_native_prepared_optix_3d_ranked_rows_${count}_r002_k50.json"
done

python3 - <<'PY'
import json
from pathlib import Path

ranked_dir = Path("docs/reports/goal2381_native_prepared_frn3d_ranked_rows_pod")
exact_dir = Path("docs/reports/goal2379_native_prepared_frn3d_exact_rows_pod")
old_dir = Path("docs/reports/goal2371_native_prepared_frn3d_pod")
for count in (65536, 262144):
    ranked = json.loads((ranked_dir / f"rtdl_packed_native_prepared_optix_3d_ranked_rows_{count}_r002_k50.json").read_text())
    exact = json.loads((exact_dir / f"rtdl_packed_native_prepared_optix_3d_exact_rows_{count}_r002_k50.json").read_text())
    old = json.loads((old_dir / f"rtdl_packed_native_prepared_optix_3d_{count}_r002_k50.json").read_text())
    print(
        "[goal2381] summary",
        "count=", count,
        "ranked_warm=", ranked["elapsed_sec"],
        "exact_warm=", exact["elapsed_sec"],
        "old_warm=", old["elapsed_sec"],
        "old/ranked=", old["elapsed_sec"] / ranked["elapsed_sec"] if ranked["elapsed_sec"] else 0.0,
        "ranked/exact=", ranked["elapsed_sec"] / exact["elapsed_sec"] if exact["elapsed_sec"] else 0.0,
        "ranked_rows=", ranked["row_count"],
        "exact_rows=", exact["row_count"],
        "mode=", ranked["phase_timings"]["mode"] if ranked["phase_timings"] else None,
    )
PY

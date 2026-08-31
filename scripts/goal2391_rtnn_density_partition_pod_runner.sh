#!/usr/bin/env bash
set -euo pipefail

ROOT="${RTDL_ROOT:-$(pwd)}"
OPTIX_PREFIX="${OPTIX_PREFIX:-/root/vendor/optix-sdk}"
CUDA_PREFIX="${CUDA_PREFIX:-/usr/local/cuda-12}"
STEP_TIMEOUT_SECONDS="${STEP_TIMEOUT_SECONDS:-1200}"
OUT_DIR="${OUT_DIR:-docs/reports/goal2391_rtnn_density_partition_pod}"
DATA_DIR="${DATA_DIR:-$OUT_DIR/data}"
REPEAT="${REPEAT:-3}"
RADIUS="${RADIUS:-0.02}"
K_MAX="${K_MAX:-50}"
RTDL_BATCH_SIZE="${RTDL_BATCH_SIZE:-65536}"
ADAPTIVE_DIVISIONS="${ADAPTIVE_DIVISIONS:-8}"

cd "$ROOT"
rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR" "$DATA_DIR" scratch

echo "[goal2391] environment"
date -u +"%Y-%m-%dT%H:%M:%SZ" | tee "$OUT_DIR/started_utc.txt"
git rev-parse HEAD | tee "$OUT_DIR/rtdl_commit.txt"
(nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader || true) | tee "$OUT_DIR/gpu.txt"

echo "[goal2391] build RTDL OptiX"
timeout "$STEP_TIMEOUT_SECONDS" make build-optix OPTIX_PREFIX="$OPTIX_PREFIX" CUDA_PREFIX="$CUDA_PREFIX"
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY="$ROOT/build/librtdl_optix.so"

echo "[goal2391] ensure CuPy"
if ! python3 - <<'PY'
import cupy
print(cupy.__version__)
PY
then
  timeout "$STEP_TIMEOUT_SECONDS" python3 -m pip install --quiet --break-system-packages cupy-cuda12x
fi

for dist in uniform clustered shell; do
  point_file="$DATA_DIR/${dist}_3d_65536.csv"
  echo "[goal2391] generate dist=$dist count=65536"
  timeout "$STEP_TIMEOUT_SECONDS" python3 scripts/goal2348_rtnn_v2_2_external_runner.py generate \
    --point-file "$point_file" \
    --point-count 65536 \
    --dimension 3 \
    --distribution "$dist" \
    --seed 65536 \
    --json-out "$OUT_DIR/generate_${dist}_65536.json"

  echo "[goal2391] CuPy grid baseline dist=$dist count=65536"
  timeout "$STEP_TIMEOUT_SECONDS" python3 scripts/goal2348_rtnn_v2_2_external_runner.py run-cupy-grid-3d-ranked-summary \
    --point-file "$point_file" \
    --radius "$RADIUS" \
    --k-max "$K_MAX" \
    --repeat "$REPEAT" \
    --row-label "cupy_grid_${dist}_65536_r002_k50" \
    --json-out "$OUT_DIR/cupy_grid_${dist}_65536_r002_k50.json"
done

cluster_file="$DATA_DIR/clustered_3d_262144.csv"
echo "[goal2391] generate clustered count=262144"
timeout "$STEP_TIMEOUT_SECONDS" python3 scripts/goal2348_rtnn_v2_2_external_runner.py generate \
  --point-file "$cluster_file" \
  --point-count 262144 \
  --dimension 3 \
  --distribution clustered \
  --seed 262144 \
  --json-out "$OUT_DIR/generate_clustered_262144.json"

echo "[goal2391] RTDL baseline clustered count=262144"
timeout "$STEP_TIMEOUT_SECONDS" python3 scripts/goal2348_rtnn_v2_2_external_runner.py run-rtdl-batched-3d-neighbors \
  --point-file "$cluster_file" \
  --radius "$RADIUS" \
  --k-max "$K_MAX" \
  --query-batch-size "$RTDL_BATCH_SIZE" \
  --result-mode ranked-summary-raw \
  --repeat "$REPEAT" \
  --row-label "rtdl_batched_clustered_262144_r002_k50" \
  --json-out "$OUT_DIR/rtdl_batched_clustered_262144_r002_k50.json"

echo "[goal2391] RTDL adaptive clustered count=262144"
timeout "$STEP_TIMEOUT_SECONDS" python3 scripts/goal2348_rtnn_v2_2_external_runner.py run-rtdl-adaptive-3d-neighbors \
  --point-file "$cluster_file" \
  --radius "$RADIUS" \
  --k-max "$K_MAX" \
  --partition-divisions "$ADAPTIVE_DIVISIONS" \
  --repeat "$REPEAT" \
  --row-label "rtdl_adaptive_clustered_262144_div${ADAPTIVE_DIVISIONS}_r002_k50" \
  --json-out "$OUT_DIR/rtdl_adaptive_clustered_262144_div${ADAPTIVE_DIVISIONS}_r002_k50.json"

echo "[goal2391] CuPy grid clustered count=262144"
timeout "$STEP_TIMEOUT_SECONDS" python3 scripts/goal2348_rtnn_v2_2_external_runner.py run-cupy-grid-3d-ranked-summary \
  --point-file "$cluster_file" \
  --radius "$RADIUS" \
  --k-max "$K_MAX" \
  --repeat "$REPEAT" \
  --row-label "cupy_grid_clustered_262144_r002_k50" \
  --json-out "$OUT_DIR/cupy_grid_clustered_262144_r002_k50.json"

python3 - <<'PY'
import json
from pathlib import Path

out = Path("docs/reports/goal2391_rtnn_density_partition_pod")
rows = []
for path in sorted(out.glob("*.json")):
    if path.name.startswith(("rtdl_", "cupy_grid_")):
        payload = json.loads(path.read_text())
        rows.append({
            "file": path.name,
            "external": payload.get("external"),
            "mode": payload.get("mode"),
            "row": payload.get("row"),
            "ok": payload.get("ok"),
            "elapsed_sec": payload.get("elapsed_sec"),
            "query_count": payload.get("query_count"),
            "search_count": payload.get("search_count"),
        })
summary = {
    "runner": "goal2391_rtnn_density_partition_pod_runner",
    "rows": rows,
    "boundary": {
        "native_abi_changed_for_rtnn": False,
        "adaptive_python_policy_measured": True,
        "stronger_cuda_core_grid_baseline_measured": True,
        "release_claim_authorized": False,
    },
}
(out / "goal2391_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(json.dumps(summary, indent=2, sort_keys=True), flush=True)
PY

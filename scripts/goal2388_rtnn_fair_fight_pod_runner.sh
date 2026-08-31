#!/usr/bin/env bash
set -euo pipefail

ROOT="${RTDL_ROOT:-$(pwd)}"
OPTIX_PREFIX="${OPTIX_PREFIX:-/root/vendor/optix-sdk}"
CUDA_PREFIX="${CUDA_PREFIX:-/usr/local/cuda-12}"
STEP_TIMEOUT_SECONDS="${STEP_TIMEOUT_SECONDS:-900}"
OUT_DIR="${OUT_DIR:-docs/reports/goal2388_rtnn_fair_fight_pod}"
DATA_DIR="${DATA_DIR:-$OUT_DIR/data}"
REPEAT="${REPEAT:-3}"
RADIUS="${RADIUS:-0.02}"
K_MAX="${K_MAX:-50}"
RTDL_BATCH_SIZE="${RTDL_BATCH_SIZE:-65536}"
CUPY_BATCH_SIZE="${CUPY_BATCH_SIZE:-256}"
CUPY_COUNTS="${CUPY_COUNTS:-65536}"
RTDL_COUNTS="${RTDL_COUNTS:-65536 262144}"
DISTRIBUTIONS="${DISTRIBUTIONS:-uniform clustered shell}"
RTNN_ROOT="${RTNN_ROOT:-scratch/rtnn_goal2388}"

cd "$ROOT"
mkdir -p "$OUT_DIR" "$DATA_DIR" scratch

echo "[goal2388] environment"
date -u +"%Y-%m-%dT%H:%M:%SZ" | tee "$OUT_DIR/started_utc.txt"
git rev-parse HEAD | tee "$OUT_DIR/rtdl_commit.txt"
(nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader || true) | tee "$OUT_DIR/gpu.txt"

echo "[goal2388] build RTDL OptiX"
timeout "$STEP_TIMEOUT_SECONDS" make build-optix OPTIX_PREFIX="$OPTIX_PREFIX" CUDA_PREFIX="$CUDA_PREFIX"
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY="$ROOT/build/librtdl_optix.so"

echo "[goal2388] ensure CuPy"
if ! python3 - <<'PY'
import cupy
print(cupy.__version__)
PY
then
  timeout "$STEP_TIMEOUT_SECONDS" python3 -m pip install --quiet --break-system-packages cupy-cuda12x
fi

echo "[goal2388] optional RTNN source setup"
RTNN_BINARY=""
RTNN_STATUS="$OUT_DIR/rtnn_status.json"
if [[ ! -d "$RTNN_ROOT/.git" ]]; then
  timeout "$STEP_TIMEOUT_SECONDS" git clone --depth 1 https://github.com/horizon-research/rtnn "$RTNN_ROOT" || true
fi
if [[ -d "$RTNN_ROOT/.git" ]]; then
  python3 scripts/goal2348_rtnn_v2_2_external_runner.py patch-rtnn-cuda12 \
    --rtnn-root "$RTNN_ROOT" \
    --json-out "$OUT_DIR/rtnn_cuda12_patch.json" || true
  mkdir -p "$RTNN_ROOT/src/build"
  (
    cd "$RTNN_ROOT/src/build"
    timeout "$STEP_TIMEOUT_SECONDS" cmake -DKNN="$K_MAX" .. &&
    timeout "$STEP_TIMEOUT_SECONDS" make -j"$(nproc)"
  ) || true
  RTNN_BINARY="$(find "$RTNN_ROOT" -name optixNSearch -type f 2>/dev/null | head -1 || true)"
  if [[ -n "$RTNN_BINARY" ]]; then
    RTNN_BINARY="$(realpath "$RTNN_BINARY")"
  fi
fi
python3 - <<PY
import json
from pathlib import Path
payload = {
    "rtnn_root": "$RTNN_ROOT",
    "rtnn_binary": "$RTNN_BINARY",
    "available": bool("$RTNN_BINARY"),
    "boundary": {
        "optional_external_baseline": True,
        "rtdl_goal_not_blocked_by_rtnn_build": True
    }
}
Path("$RTNN_STATUS").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\\n")
print(json.dumps(payload, indent=2, sort_keys=True), flush=True)
PY

for dist in $DISTRIBUTIONS; do
  for count in $RTDL_COUNTS; do
    point_file="$DATA_DIR/${dist}_3d_${count}.csv"
    echo "[goal2388] generate dist=$dist count=$count"
    timeout "$STEP_TIMEOUT_SECONDS" python3 scripts/goal2348_rtnn_v2_2_external_runner.py generate \
      --point-file "$point_file" \
      --point-count "$count" \
      --dimension 3 \
      --distribution "$dist" \
      --seed "$count" \
      --json-out "$OUT_DIR/generate_${dist}_${count}.json"

    echo "[goal2388] RTDL batched ranked-summary dist=$dist count=$count"
    timeout "$STEP_TIMEOUT_SECONDS" python3 scripts/goal2348_rtnn_v2_2_external_runner.py run-rtdl-batched-3d-neighbors \
      --point-file "$point_file" \
      --radius "$RADIUS" \
      --k-max "$K_MAX" \
      --query-batch-size "$RTDL_BATCH_SIZE" \
      --result-mode ranked-summary-raw \
      --repeat "$REPEAT" \
      --row-label "rtdl_batched_ranked_summary_${dist}_${count}_r002_k50" \
      --json-out "$OUT_DIR/rtdl_batched_ranked_summary_${dist}_${count}_r002_k50.json"

    if [[ -n "$RTNN_BINARY" ]]; then
      echo "[goal2388] RTNN official optional dist=$dist count=$count"
      timeout "$STEP_TIMEOUT_SECONDS" python3 scripts/goal2348_rtnn_v2_2_external_runner.py run-rtnn \
        --rtnn-binary "$RTNN_BINARY" \
        --rtnn-cwd "$(dirname "$RTNN_BINARY")" \
        --point-file "$ROOT/$point_file" \
        --search-mode radius \
        --radius "$RADIUS" \
        --k-max "$K_MAX" \
        --partition \
        --auto-batch \
        --timeout-sec "$STEP_TIMEOUT_SECONDS" \
        --row-label "rtnn_official_radius_${dist}_${count}_r002_k50" \
        --json-out "$OUT_DIR/rtnn_official_radius_${dist}_${count}_r002_k50.json" || true
    fi
  done

  for count in $CUPY_COUNTS; do
    point_file="$DATA_DIR/${dist}_3d_${count}.csv"
    echo "[goal2388] CuPy CUDA-core exact ranked-summary dist=$dist count=$count"
    timeout "$STEP_TIMEOUT_SECONDS" python3 scripts/goal2348_rtnn_v2_2_external_runner.py run-cupy-3d-ranked-summary \
      --point-file "$point_file" \
      --radius "$RADIUS" \
      --k-max "$K_MAX" \
      --query-batch-size "$CUPY_BATCH_SIZE" \
      --dtype float32 \
      --repeat "$REPEAT" \
      --row-label "cupy_exact_ranked_summary_${dist}_${count}_r002_k50" \
      --json-out "$OUT_DIR/cupy_exact_ranked_summary_${dist}_${count}_r002_k50.json"
  done
done

python3 - <<'PY'
import json
from pathlib import Path

out = Path("docs/reports/goal2388_rtnn_fair_fight_pod")
rows = []
for path in sorted(out.glob("*.json")):
    if path.name.startswith(("rtdl_batched", "cupy_exact", "rtnn_official")):
        payload = json.loads(path.read_text())
        rows.append({
            "file": path.name,
            "external": payload.get("external"),
            "row": payload.get("row"),
            "ok": payload.get("ok", payload.get("returncode") == 0),
            "elapsed_sec": payload.get("elapsed_sec"),
            "query_count": payload.get("query_count"),
            "search_count": payload.get("search_count"),
            "result_mode": payload.get("result_mode"),
            "mode": payload.get("mode"),
        })
summary = {
    "runner": "goal2388_rtnn_fair_fight_pod_runner",
    "rows": rows,
    "boundary": {
        "paper_equivalent_rtnn_reproduction": False,
        "same_contract_rtdl_vs_cupy_ranked_summary": True,
        "official_rtnn_optional": True,
    },
}
(out / "goal2388_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(json.dumps(summary, indent=2, sort_keys=True), flush=True)
PY

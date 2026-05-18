#!/usr/bin/env bash
set -euo pipefail

echo "[goal2340] start $(date -Is)"
echo "[goal2340] cwd=$PWD"

if command -v nvidia-smi >/dev/null 2>&1; then
  echo "[goal2340] gpu"
  nvidia-smi --query-gpu=name,driver_version --format=csv,noheader || true
fi

if [ -d /usr/local/cuda-12 ]; then
  export CUDA_HOME=/usr/local/cuda-12
  export PATH=/usr/local/cuda-12/bin:$PATH
  export LD_LIBRARY_PATH=/usr/local/cuda-12/targets/x86_64-linux/lib:/usr/local/cuda-12/lib64:/usr/local/cuda-12/compat:${LD_LIBRARY_PATH:-}
  export RTDL_OPTIX_PTX_ARCH=${RTDL_OPTIX_PTX_ARCH:-compute_86}
  export RTDL_OPTIX_PTX_COMPILER=${RTDL_OPTIX_PTX_COMPILER:-nvcc}
  export RTDL_NVCC=${RTDL_NVCC:-/usr/local/cuda-12/bin/nvcc}
  export RTDL_NVCC_CCBIN=${RTDL_NVCC_CCBIN:-/usr/bin/g++}
  echo "[goal2340] using CUDA_HOME=$CUDA_HOME"
fi

if ! python3 - <<'PY'
try:
    import cupy  # noqa: F401
    print("[goal2340] CuPy already installed")
except Exception:
    raise SystemExit(1)
PY
then
  echo "[goal2340] installing cupy-cuda12x"
  python3 -m pip install --upgrade pip
  python3 -m pip install cupy-cuda12x
fi

echo "[goal2340] ensuring OptiX SDK"
mkdir -p /root/vendor
if [ ! -d /root/vendor/optix-sdk/.git ]; then
  git clone --depth 1 --branch v8.0.0 https://github.com/NVIDIA/optix-sdk /root/vendor/optix-sdk
fi
ln -sfn /root/vendor/optix-sdk /opt/optix

echo "[goal2340] build OptiX"
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk ${CUDA_HOME:+CUDA_PREFIX=$CUDA_HOME}
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
export PYTHONPATH=src:.

OUT_DIR=docs/reports/goal2340_hausdorff_v2_1_pod
mkdir -p "$OUT_DIR"
COMMIT=$(git rev-parse HEAD)
echo "[goal2340] commit=$COMMIT"

echo "[goal2340] run xhd-graphics 262144 auto-group"
python3 scripts/goal2126_public_hausdorff_dataset_perf.py \
  --case-suite xhd-graphics \
  --sample-count 262144 \
  --warmup 1 \
  --commit-label "$COMMIT" \
  --json-out "$OUT_DIR/xhd_graphics_262144_auto_group.json"

echo "[goal2340] run xhd-graphics 1048576 auto-group"
python3 scripts/goal2126_public_hausdorff_dataset_perf.py \
  --case-suite xhd-graphics \
  --sample-count 1048576 \
  --warmup 1 \
  --commit-label "$COMMIT" \
  --json-out "$OUT_DIR/xhd_graphics_1048576_auto_group.json"

echo "[goal2340] summarize"
python3 - <<'PY'
import json
from pathlib import Path

for path in sorted(Path("docs/reports/goal2340_hausdorff_v2_1_pod").glob("*.json")):
    data = json.loads(path.read_text())
    print(f"[goal2340] artifact={path}")
    for row in data["rows"]:
        ratio = row.get("rtdl_seeded_pruned_vs_cupy_grouped_grid_ratio")
        ok = row.get("matches_cupy_grouped_grid_seeded_pruned")
        group = row.get("target_points_per_group")
        print(f"[goal2340]   {row['case']} group={group} match={ok} ratio={ratio}")
PY

echo "[goal2340] done $(date -Is)"

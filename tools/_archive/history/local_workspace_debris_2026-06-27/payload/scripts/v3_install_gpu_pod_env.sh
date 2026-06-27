#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" != "--accept-experimental-pod-gate" ]]; then
  cat >&2 <<'EOF'
Usage:
  bash scripts/v3_install_gpu_pod_env.sh --accept-experimental-pod-gate

This installs the staged Python GPU package set used by the 2026-06-20 Phoenix
V3 pod evidence runs. It is not a general release installer.
EOF
  exit 2
fi

python3 -m pip install --upgrade pip

# PyTorch cu124 is installed first from the PyTorch wheel index.
python3 -m pip install \
  --index-url https://download.pytorch.org/whl/cu124 \
  "torch==2.6.0+cu124"

# CuPy 14.1.1 needs the newer CUDA 12.9 NVRTC/runtime wheels on the tested pod.
# Installing these after torch may produce resolver warnings because torch pins
# some CUDA wheel versions. The V3 gate is the source of truth after install.
python3 -m pip install \
  "cupy-cuda12x==14.1.1" \
  "numba==0.65.1" \
  "nvidia-cuda-nvcc-cu12==12.4.131" \
  "nvidia-cuda-nvrtc-cu12==12.9.86" \
  "nvidia-cuda-runtime-cu12==12.9.79"

python3 scripts/v3_gpu_python_env_gate.py --pretty

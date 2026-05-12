#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${OUT_DIR:-docs/reports/goal1804_v2_partner_optix_pod}"
OPTIX_PREFIX="${OPTIX_PREFIX:-/root/vendor/optix-dev}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

mkdir -p "${OUT_DIR}"

echo "[goal1804] repo: $(pwd)"
echo "[goal1804] commit: $(git rev-parse HEAD)"
echo "[goal1804] output: ${OUT_DIR}"

{
  echo "commit=$(git rev-parse HEAD)"
  echo "python=$(${PYTHON_BIN} --version 2>&1)"
  echo "optix_prefix=${OPTIX_PREFIX}"
  if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi
  else
    echo "nvidia-smi=missing"
  fi
} | tee "${OUT_DIR}/environment.txt"

if ! ${PYTHON_BIN} - <<'PY' >/dev/null 2>&1
import importlib.util
raise SystemExit(0 if importlib.util.find_spec("torch") and importlib.util.find_spec("cupy") else 1)
PY
then
  echo "[goal1804] installing PyTorch CUDA and CuPy into the active Python environment"
  ${PYTHON_BIN} -m pip install --index-url https://download.pytorch.org/whl/cu121 torch
  ${PYTHON_BIN} -m pip install cupy-cuda12x
fi

echo "[goal1804] probing partner frameworks"
PYTHONPATH=src:. ${PYTHON_BIN} - <<'PY' | tee "${OUT_DIR}/partner_probe.json"
import json
import numpy as np
import torch
import cupy

print(json.dumps({
    "numpy": np.__version__,
    "torch": torch.__version__,
    "torch_cuda_available": bool(torch.cuda.is_available()),
    "torch_cuda": getattr(torch.version, "cuda", None),
    "cupy": cupy.__version__,
    "cupy_device_count": int(cupy.cuda.runtime.getDeviceCount()),
}, indent=2, sort_keys=True))
PY

echo "[goal1804] building OptiX"
make build-optix OPTIX_PREFIX="${OPTIX_PREFIX}" 2>&1 | tee "${OUT_DIR}/build_optix.log"

echo "[goal1804] running focused v2.0 partner OptiX tests"
PYTHONPATH=src:. ${PYTHON_BIN} -m unittest \
  tests.goal1799_partner_anyhit_public_dispatch_test \
  tests.goal1793_mixed_partner_columns_conformance_test \
  tests.goal1791_partner_handoff_phase_timing_test \
  tests.goal1787_optix_partner_anyhit_host_stage_test \
  tests.goal1781_real_framework_partner_availability_test \
  tests.goal1777_v2_0_partner_protocol_baseline_test \
  tests.goal1675_partner_protocol_substrate_test \
  2>&1 | tee "${OUT_DIR}/focused_unittest.log"

echo "[goal1804] running example over OptiX for NumPy, PyTorch CUDA, and CuPy CUDA"
for partner in numpy torch-cuda cupy-cuda; do
  PYTHONPATH=src:. ${PYTHON_BIN} examples/rtdl_partner_anyhit.py \
    --partner "${partner}" \
    --backend optix \
    > "${OUT_DIR}/example_${partner}_optix.json"
  cat "${OUT_DIR}/example_${partner}_optix.json"
done

echo "[goal1804] validating claim flags"
PYTHONPATH=src:. ${PYTHON_BIN} - "${OUT_DIR}" <<'PY'
import json
import pathlib
import sys

out_dir = pathlib.Path(sys.argv[1])
summary = {}
for path in sorted(out_dir.glob("example_*_optix.json")):
    data = json.loads(path.read_text())
    if data["hit_count"] != 1:
        raise SystemExit(f"{path.name}: expected hit_count=1")
    if data["transfer_mode"] != "host_stage":
        raise SystemExit(f"{path.name}: expected host_stage transfer")
    if data["true_zero_copy_authorized"]:
        raise SystemExit(f"{path.name}: zero-copy claim unexpectedly authorized")
    if data["rt_core_speedup_claim_authorized"]:
        raise SystemExit(f"{path.name}: RT-core speedup claim unexpectedly authorized")
    summary[path.stem] = {
        "hit_count": data["hit_count"],
        "source_protocols": data["source_protocols"],
        "source_devices": data["source_devices"],
        "transfer_mode": data["transfer_mode"],
        "true_zero_copy_authorized": data["true_zero_copy_authorized"],
        "rt_core_speedup_claim_authorized": data["rt_core_speedup_claim_authorized"],
    }
summary_path = out_dir / "summary.json"
summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(summary_path)
PY

echo "[goal1804] complete: ${OUT_DIR}"

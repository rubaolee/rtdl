#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${OUT_DIR:-docs/reports/goal1897_road_hazard_prepared_reuse_pod}"
OPTIX_PREFIX="${OPTIX_PREFIX:-/root/vendor/optix-sdk}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
COUNTS="${COUNTS:-512 2048}"
ITERATIONS="${ITERATIONS:-5}"
PARTNERS="${PARTNERS:-cupy,torch}"
THRESHOLD="${THRESHOLD:-2}"
REQUIRE_RTX="${REQUIRE_RTX:-1}"
RTDL_PYTHONPATH="src:."
if [[ -n "${PYTHONPATH:-}" ]]; then
  RTDL_PYTHONPATH="${PYTHONPATH}:${RTDL_PYTHONPATH}"
fi
SOURCE_COMMIT_LABEL="${RTDL_SOURCE_COMMIT_LABEL:-$(git rev-parse HEAD)}"

mkdir -p "${OUT_DIR}"

echo "[goal1897] repo: $(pwd)"
echo "[goal1897] commit: $(git rev-parse HEAD)"
echo "[goal1897] source_commit_label: ${SOURCE_COMMIT_LABEL}"
echo "[goal1897] output: ${OUT_DIR}"
echo "[goal1897] counts: ${COUNTS}"
echo "[goal1897] iterations: ${ITERATIONS}"
echo "[goal1897] partners: ${PARTNERS}"

{
  echo "commit=$(git rev-parse HEAD)"
  echo "source_commit_label=${SOURCE_COMMIT_LABEL}"
  echo "python=$(${PYTHON_BIN} --version 2>&1)"
  echo "optix_prefix=${OPTIX_PREFIX}"
  echo "counts=${COUNTS}"
  echo "iterations=${ITERATIONS}"
  echo "partners=${PARTNERS}"
  echo "require_rtx=${REQUIRE_RTX}"
  if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi
  else
    echo "nvidia-smi=missing"
  fi
} | tee "${OUT_DIR}/environment.txt"

GPU_NAME="$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -n 1 || true)"
echo "[goal1897] gpu: ${GPU_NAME:-unknown}"
if [[ "${REQUIRE_RTX}" == "1" && "${GPU_NAME}" != *"RTX"* ]]; then
  echo "[goal1897] refusing accepted pod run on non-RTX GPU: ${GPU_NAME:-unknown}" >&2
  echo "[goal1897] set REQUIRE_RTX=0 only for local dry-run mechanics" >&2
  exit 2
fi

if ! ${PYTHON_BIN} - <<'PY' >/dev/null 2>&1
import importlib.util
raise SystemExit(0 if importlib.util.find_spec("torch") and importlib.util.find_spec("cupy") else 1)
PY
then
  echo "[goal1897] installing PyTorch CUDA and CuPy into the active Python environment"
  ${PYTHON_BIN} -m pip install --index-url https://download.pytorch.org/whl/cu121 torch
  ${PYTHON_BIN} -m pip install cupy-cuda12x
fi

echo "[goal1897] probing partner frameworks"
PYTHONPATH="${RTDL_PYTHONPATH}" ${PYTHON_BIN} - <<'PY' | tee "${OUT_DIR}/partner_probe.json"
import json
import torch
import cupy

props = cupy.cuda.runtime.getDeviceProperties(0)
name = props.get("name", "cuda:0")
if isinstance(name, bytes):
    name = name.decode("utf-8", errors="replace")
print(json.dumps({
    "torch": torch.__version__,
    "torch_cuda_available": bool(torch.cuda.is_available()),
    "torch_cuda_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "",
    "cupy": cupy.__version__,
    "cupy_device": name,
}, indent=2, sort_keys=True))
PY

echo "[goal1897] building OptiX"
make build-optix OPTIX_PREFIX="${OPTIX_PREFIX}" 2>&1 | tee "${OUT_DIR}/build_optix.log"

export RTDL_OPTIX_LIBRARY="${PWD}/build/librtdl_optix.so"
export RTDL_SOURCE_COMMIT_LABEL="${SOURCE_COMMIT_LABEL}"

echo "[goal1897] running focused tests"
PYTHONPATH="${RTDL_PYTHONPATH}" ${PYTHON_BIN} -m unittest \
  tests.goal1889_road_hazard_prepared_partner_reuse_perf_test \
  tests.goal1869_road_hazard_v2_partner_perf_plan_test \
  tests.goal1886_segment_polygon_prepared_partner_reuse_test \
  2>&1 | tee "${OUT_DIR}/focused_unittest.log"

for count in ${COUNTS}; do
  artifact="docs/reports/goal1889_road_hazard_prepared_reuse_pod_${count}.json"
  echo "[goal1897] running road-hazard prepared reuse count=${count} -> ${artifact}"
  PYTHONPATH="${RTDL_PYTHONPATH}" ${PYTHON_BIN} scripts/goal1869_road_hazard_v2_partner_perf.py \
    --count "${count}" \
    --threshold "${THRESHOLD}" \
    --iterations "${ITERATIONS}" \
    --partners "${PARTNERS}" \
    --output "${artifact}" \
    2>&1 | tee "${OUT_DIR}/road_hazard_${count}.log"
done

echo "[goal1897] validating artifacts"
PYTHONPATH="${RTDL_PYTHONPATH}" ${PYTHON_BIN} - "${SOURCE_COMMIT_LABEL}" ${COUNTS} <<'PY'
import json
import pathlib
import sys

source_commit_label = sys.argv[1]
counts = [int(value) for value in sys.argv[2:]]
summary = {}
for count in counts:
    path = pathlib.Path(f"docs/reports/goal1889_road_hazard_prepared_reuse_pod_{count}.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data["status"] != "pass":
        raise SystemExit(f"{path}: expected pass")
    if data.get("goal_extension") != "Goal1889":
        raise SystemExit(f"{path}: missing Goal1889 extension label")
    if data.get("source_commit_label") != source_commit_label:
        raise SystemExit(f"{path}: source label mismatch")
    if not data["parity"]["strict_priority_flags_match"]:
        raise SystemExit(f"{path}: strict parity failed")
    boundary = data["claim_boundary"]
    if boundary["v2_0_release_authorized"]:
        raise SystemExit(f"{path}: v2.0 release unexpectedly authorized")
    if boundary["whole_app_speedup_claim_authorized"]:
        raise SystemExit(f"{path}: whole-app speedup unexpectedly authorized")
    for partner, result in data["partners"].items():
        prepared = result["goal1889_prepared_reuse"]
        summary[f"{count}_{partner}"] = {
            "unprepared_median_s": result["query_summary"]["median_s"],
            "prepared_median_s": prepared["query_summary"]["median_s"],
            "prepared_ratio_vs_unprepared": prepared["query_median_ratio_vs_goal1869_unprepared_partner"],
            "prepared_ratio_vs_v1_8_prepared": prepared["query_median_ratio_vs_v1_8_prepared_native"],
        }
summary_path = pathlib.Path("docs/reports/goal1897_road_hazard_prepared_reuse_pod_summary.json")
summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(summary_path)
PY

cp docs/reports/goal1897_road_hazard_prepared_reuse_pod_summary.json "${OUT_DIR}/summary.json"
echo "[goal1897] complete: ${OUT_DIR}"

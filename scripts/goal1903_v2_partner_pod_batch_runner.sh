#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${OUT_DIR:-docs/reports/goal1903_v2_partner_pod_batch}"
OPTIX_PREFIX="${OPTIX_PREFIX:-/root/vendor/optix-sdk}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
REQUIRE_RTX="${REQUIRE_RTX:-1}"
RUN_FIXED_RADIUS="${RUN_FIXED_RADIUS:-1}"
RUN_SEGMENT_POLYGON="${RUN_SEGMENT_POLYGON:-1}"
RUN_ROAD_HAZARD="${RUN_ROAD_HAZARD:-1}"
FIXED_RADIUS_SIZES="${FIXED_RADIUS_SIZES:-4096,16384}"
FIXED_RADIUS_REPEAT="${FIXED_RADIUS_REPEAT:-7}"
FIXED_RADIUS_PARTNER="${FIXED_RADIUS_PARTNER:-both}"
SEGMENT_POLYGON_COUNTS="${SEGMENT_POLYGON_COUNTS:-512 2048}"
SEGMENT_POLYGON_ITERATIONS="${SEGMENT_POLYGON_ITERATIONS:-5}"
SEGMENT_POLYGON_PARTNERS="${SEGMENT_POLYGON_PARTNERS:-cupy,torch}"
ROAD_HAZARD_COUNTS="${ROAD_HAZARD_COUNTS:-512 2048}"
ROAD_HAZARD_ITERATIONS="${ROAD_HAZARD_ITERATIONS:-5}"
ROAD_HAZARD_PARTNERS="${ROAD_HAZARD_PARTNERS:-cupy,torch}"
ROAD_HAZARD_THRESHOLD="${ROAD_HAZARD_THRESHOLD:-2}"
SOURCE_COMMIT_LABEL="${RTDL_SOURCE_COMMIT_LABEL:-$(git rev-parse HEAD)}"
FIXED_RADIUS_ARTIFACT="docs/reports/goal1903_fixed_radius_batch_pod.json"
SUMMARY_ARTIFACT="docs/reports/goal1903_v2_partner_pod_batch_summary.json"

RTDL_PYTHONPATH="src:."
if [[ -n "${PYTHONPATH:-}" ]]; then
  RTDL_PYTHONPATH="${PYTHONPATH}:${RTDL_PYTHONPATH}"
fi

mkdir -p "${OUT_DIR}"

echo "[goal1903] clearing this run's target artifacts"
rm -f "${FIXED_RADIUS_ARTIFACT}" "${SUMMARY_ARTIFACT}" docs/reports/goal1897_road_hazard_prepared_reuse_pod_summary.json
for count in ${SEGMENT_POLYGON_COUNTS}; do
  rm -f "docs/reports/goal1903_segment_polygon_batch_pod_${count}.json"
done
for count in ${ROAD_HAZARD_COUNTS}; do
  rm -f "docs/reports/goal1889_road_hazard_prepared_reuse_pod_${count}.json"
done

echo "[goal1903] repo: $(pwd)"
echo "[goal1903] commit: $(git rev-parse HEAD)"
echo "[goal1903] source_commit_label: ${SOURCE_COMMIT_LABEL}"
echo "[goal1903] output: ${OUT_DIR}"

{
  echo "commit=$(git rev-parse HEAD)"
  echo "source_commit_label=${SOURCE_COMMIT_LABEL}"
  echo "python=$(${PYTHON_BIN} --version 2>&1)"
  echo "optix_prefix=${OPTIX_PREFIX}"
  echo "require_rtx=${REQUIRE_RTX}"
  echo "run_fixed_radius=${RUN_FIXED_RADIUS}"
  echo "run_segment_polygon=${RUN_SEGMENT_POLYGON}"
  echo "run_road_hazard=${RUN_ROAD_HAZARD}"
  if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi
  else
    echo "nvidia-smi=missing"
  fi
} | tee "${OUT_DIR}/environment.txt"

GPU_NAME="$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -n 1 || true)"
echo "[goal1903] gpu: ${GPU_NAME:-unknown}"
if [[ "${REQUIRE_RTX}" == "1" && "${GPU_NAME}" != *"RTX"* ]]; then
  echo "[goal1903] refusing accepted pod batch on non-RTX GPU: ${GPU_NAME:-unknown}" >&2
  echo "[goal1903] set REQUIRE_RTX=0 only for local dry-run mechanics" >&2
  exit 2
fi

if ! ${PYTHON_BIN} - <<'PY' >/dev/null 2>&1
import importlib.util
raise SystemExit(0 if importlib.util.find_spec("torch") and importlib.util.find_spec("cupy") else 1)
PY
then
  echo "[goal1903] installing PyTorch CUDA and CuPy into the active Python environment"
  ${PYTHON_BIN} -m pip install --index-url https://download.pytorch.org/whl/cu121 torch
  ${PYTHON_BIN} -m pip install cupy-cuda12x
fi

echo "[goal1903] probing partner frameworks"
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

echo "[goal1903] building OptiX once for the batch"
make build-optix OPTIX_PREFIX="${OPTIX_PREFIX}" 2>&1 | tee "${OUT_DIR}/build_optix.log"
export RTDL_OPTIX_LIBRARY="${PWD}/build/librtdl_optix.so"
export RTDL_SOURCE_COMMIT_LABEL="${SOURCE_COMMIT_LABEL}"

echo "[goal1903] running shared focused tests"
PYTHONPATH="${RTDL_PYTHONPATH}" ${PYTHON_BIN} -m unittest \
  tests.goal1881_prepared_fixed_radius_reusable_outputs_test \
  tests.goal1886_segment_polygon_prepared_partner_reuse_test \
  tests.goal1889_road_hazard_prepared_partner_reuse_perf_test \
  tests.goal1897_road_hazard_prepared_reuse_pod_packet_test \
  2>&1 | tee "${OUT_DIR}/focused_unittest.log"

if [[ "${RUN_FIXED_RADIUS}" == "1" ]]; then
  echo "[goal1903] running fixed-radius batch sizes=${FIXED_RADIUS_SIZES}"
  PYTHONPATH="${RTDL_PYTHONPATH}" ${PYTHON_BIN} scripts/goal1878_fixed_radius_app_adapter_perf.py \
    --sizes "${FIXED_RADIUS_SIZES}" \
    --repeat "${FIXED_RADIUS_REPEAT}" \
    --partner "${FIXED_RADIUS_PARTNER}" \
    --output "${FIXED_RADIUS_ARTIFACT}" \
    2>&1 | tee "${OUT_DIR}/fixed_radius.log"
fi

if [[ "${RUN_SEGMENT_POLYGON}" == "1" ]]; then
  for count in ${SEGMENT_POLYGON_COUNTS}; do
    echo "[goal1903] running segment/polygon count=${count}"
    PYTHONPATH="${RTDL_PYTHONPATH}" ${PYTHON_BIN} scripts/goal1863_segment_polygon_hitcount_v2_partner_perf.py \
      --count "${count}" \
      --iterations "${SEGMENT_POLYGON_ITERATIONS}" \
      --partners "${SEGMENT_POLYGON_PARTNERS}" \
      --output "docs/reports/goal1903_segment_polygon_batch_pod_${count}.json" \
      2>&1 | tee "${OUT_DIR}/segment_polygon_${count}.log"
  done
fi

if [[ "${RUN_ROAD_HAZARD}" == "1" ]]; then
  echo "[goal1903] running road-hazard Goal1897 packet counts=${ROAD_HAZARD_COUNTS}"
  OUT_DIR="${OUT_DIR}/goal1897_road_hazard" \
  OPTIX_PREFIX="${OPTIX_PREFIX}" \
  PYTHON_BIN="${PYTHON_BIN}" \
  COUNTS="${ROAD_HAZARD_COUNTS}" \
  ITERATIONS="${ROAD_HAZARD_ITERATIONS}" \
  PARTNERS="${ROAD_HAZARD_PARTNERS}" \
  THRESHOLD="${ROAD_HAZARD_THRESHOLD}" \
  REQUIRE_RTX="${REQUIRE_RTX}" \
  RTDL_SOURCE_COMMIT_LABEL="${SOURCE_COMMIT_LABEL}" \
  PYTHONPATH="${PYTHONPATH:-}" \
  bash scripts/goal1897_road_hazard_prepared_reuse_pod_runner.sh
fi

echo "[goal1903] writing batch summary"
PYTHONPATH="${RTDL_PYTHONPATH}" \
SEGMENT_POLYGON_COUNTS="${SEGMENT_POLYGON_COUNTS}" \
ROAD_HAZARD_COUNTS="${ROAD_HAZARD_COUNTS}" \
${PYTHON_BIN} - "${SOURCE_COMMIT_LABEL}" "${RUN_FIXED_RADIUS}" "${RUN_SEGMENT_POLYGON}" "${RUN_ROAD_HAZARD}" <<'PY'
import json
import os
import pathlib
import sys

source_commit_label, run_fixed, run_segment, run_road = sys.argv[1:5]
segment_counts = [value for value in os.environ["SEGMENT_POLYGON_COUNTS"].split() if value]
road_counts = [value for value in os.environ["ROAD_HAZARD_COUNTS"].split() if value]
forbid_true_claims = (
    "v2_0_release_authorized",
    "whole_app_speedup_claim_authorized",
    "broad_rt_core_speedup_claim_authorized",
)

def _load_json(path_text):
    path = pathlib.Path(path_text)
    if not path.exists():
        raise SystemExit(f"{path}: expected artifact to exist")
    return json.loads(path.read_text(encoding="utf-8"))

def _check_boundary_false(boundary, path_text):
    for key in forbid_true_claims:
        if boundary.get(key):
            raise SystemExit(f"{path_text}: {key} unexpectedly true")

def _check_provenance(data, path_text):
    if "RTX" not in str(data.get("gpu", "")):
        raise SystemExit(f"{path_text}: expected RTX GPU provenance")
    if not data.get("git_commit") or data.get("git_commit") == "unknown":
        raise SystemExit(f"{path_text}: expected git_commit provenance")
    if data.get("source_commit_label") != source_commit_label:
        raise SystemExit(f"{path_text}: source label mismatch")

if run_fixed == "1":
    fixed_path = "docs/reports/goal1903_fixed_radius_batch_pod.json"
    fixed = _load_json(fixed_path)
    if fixed.get("status") != "measurement":
        raise SystemExit(f"{fixed_path}: expected status=measurement")
    _check_provenance(fixed, fixed_path)
    if not fixed.get("results"):
        raise SystemExit(f"{fixed_path}: expected non-empty results")
    for result in fixed["results"]:
        _check_boundary_false(result.get("claim_boundaries", {}), fixed_path)

if run_segment == "1":
    for value in segment_counts:
        segment_path = f"docs/reports/goal1903_segment_polygon_batch_pod_{value}.json"
        segment = _load_json(segment_path)
        if segment.get("status") != "pass":
            raise SystemExit(f"{segment_path}: expected status=pass")
        _check_provenance(segment, segment_path)
        if not segment.get("parity", {}).get("strict_counts_match"):
            raise SystemExit(f"{segment_path}: strict_counts_match failed")
        _check_boundary_false(segment.get("claim_boundary", {}), segment_path)

summary = {
    "source_commit_label": source_commit_label,
    "fixed_radius": {"requested": run_fixed == "1", "artifact": "docs/reports/goal1903_fixed_radius_batch_pod.json"},
    "segment_polygon": {
        "requested": run_segment == "1",
        "counts": [int(value) for value in segment_counts],
        "artifacts": [
            f"docs/reports/goal1903_segment_polygon_batch_pod_{value}.json"
            for value in segment_counts
        ],
    },
    "road_hazard": {
        "requested": run_road == "1",
        "artifacts": [
            f"docs/reports/goal1889_road_hazard_prepared_reuse_pod_{value}.json"
            for value in road_counts
        ],
    },
    "claim_boundary": {
        "v2_0_release_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_rt_core_speedup_claim_authorized": False,
    },
}
path = pathlib.Path("docs/reports/goal1903_v2_partner_pod_batch_summary.json")
path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(path)
PY
cp "${SUMMARY_ARTIFACT}" "${OUT_DIR}/summary.json"
echo "[goal1903] complete: ${OUT_DIR}"

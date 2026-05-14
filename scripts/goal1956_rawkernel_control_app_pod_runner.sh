#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${OUT_DIR:-docs/reports/goal1956_rawkernel_control_app_pod}"
OPTIX_PREFIX="${OPTIX_PREFIX:-/root/vendor/optix-sdk}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
SOURCE_COMMIT_LABEL="${RTDL_SOURCE_COMMIT_LABEL:-$(git rev-parse HEAD)}"
STEP_TIMEOUT_SECONDS="${STEP_TIMEOUT_SECONDS:-1800}"
DB_COPIES="${DB_COPIES:-100000}"
GRAPH_COPIES="${GRAPH_COPIES:-1000}"
POLYGON_COPIES="${POLYGON_COPIES:-2048}"
REPEATS="${REPEATS:-3}"
WARMUPS="${WARMUPS:-1}"
RUN_POLYGON_WITH_OPTIX="${RUN_POLYGON_WITH_OPTIX:-1}"

mkdir -p "${OUT_DIR}"
export PYTHONPATH="${PYTHONPATH:-src:.}"

run_step() {
  local name="$1"
  shift
  echo "[goal1956] $(date -Iseconds) start ${name}" | tee -a "${OUT_DIR}/progress.log"
  if [[ "${STEP_TIMEOUT_SECONDS}" == "0" ]]; then
    "$@" 2>&1 | tee "${OUT_DIR}/${name}.log"
  else
    timeout --preserve-status "${STEP_TIMEOUT_SECONDS}s" "$@" 2>&1 | tee "${OUT_DIR}/${name}.log"
  fi
  echo "[goal1956] $(date -Iseconds) done ${name}" | tee -a "${OUT_DIR}/progress.log"
}

echo "[goal1956] repo=$(pwd)" | tee "${OUT_DIR}/environment.txt"
echo "[goal1956] source_commit_label=${SOURCE_COMMIT_LABEL}" | tee -a "${OUT_DIR}/environment.txt"
echo "[goal1956] python=$(${PYTHON_BIN} --version 2>&1)" | tee -a "${OUT_DIR}/environment.txt"
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi | tee -a "${OUT_DIR}/environment.txt"
else
  echo "[goal1956] nvidia-smi missing" | tee -a "${OUT_DIR}/environment.txt"
fi

if ! "${PYTHON_BIN}" - <<'PY' >/dev/null 2>&1
import importlib.util
raise SystemExit(0 if importlib.util.find_spec("cupy") else 1)
PY
then
  echo "[goal1956] installing CuPy CUDA package" | tee -a "${OUT_DIR}/progress.log"
  "${PYTHON_BIN}" -m pip install cupy-cuda12x 2>&1 | tee "${OUT_DIR}/install_cupy.log"
fi

echo "[goal1956] probing CuPy" | tee -a "${OUT_DIR}/progress.log"
PYTHONPATH="${PYTHONPATH}" "${PYTHON_BIN}" - <<'PY' | tee "${OUT_DIR}/cupy_probe.json"
import json
import cupy

props = cupy.cuda.runtime.getDeviceProperties(0)
name = props.get("name", "cuda:0")
if isinstance(name, bytes):
    name = name.decode("utf-8", errors="replace")
print(json.dumps({
    "cupy": cupy.__version__,
    "device": name,
}, indent=2, sort_keys=True))
PY

echo "[goal1956] building OptiX once for polygon candidate discovery" | tee -a "${OUT_DIR}/progress.log"
make build-optix OPTIX_PREFIX="${OPTIX_PREFIX}" 2>&1 | tee "${OUT_DIR}/build_optix.log"
export RTDL_OPTIX_LIBRARY="${PWD}/build/librtdl_optix.so"

run_step focused_unittest \
  "${PYTHON_BIN}" -m unittest \
    tests.goal1953_control_apps_cupy_rawkernel_v2_test \
    tests.goal1955_rawkernel_control_app_perf_test

run_step database_analytics \
  "${PYTHON_BIN}" scripts/goal1955_rawkernel_control_app_perf.py \
    --apps database_analytics \
    --copies "${DB_COPIES}" \
    --partner cupy \
    --candidate-backend cpu_all_pairs \
    --repeats "${REPEATS}" \
    --warmups "${WARMUPS}" \
    --source-commit-label "${SOURCE_COMMIT_LABEL}" \
    --output "${OUT_DIR}/database_analytics.json"

run_step graph_analytics \
  "${PYTHON_BIN}" scripts/goal1955_rawkernel_control_app_perf.py \
    --apps graph_analytics \
    --copies "${GRAPH_COPIES}" \
    --partner cupy \
    --candidate-backend cpu_all_pairs \
    --repeats "${REPEATS}" \
    --warmups "${WARMUPS}" \
    --source-commit-label "${SOURCE_COMMIT_LABEL}" \
    --output "${OUT_DIR}/graph_analytics.json"

if [[ "${RUN_POLYGON_WITH_OPTIX}" == "1" ]]; then
  polygon_candidate_backend="optix"
else
  polygon_candidate_backend="cpu_all_pairs"
fi

run_step polygon_pair_overlap_area_rows \
  "${PYTHON_BIN}" scripts/goal1955_rawkernel_control_app_perf.py \
    --apps polygon_pair_overlap_area_rows \
    --copies "${POLYGON_COPIES}" \
    --partner cupy \
    --candidate-backend "${polygon_candidate_backend}" \
    --repeats "${REPEATS}" \
    --warmups "${WARMUPS}" \
    --source-commit-label "${SOURCE_COMMIT_LABEL}" \
    --output "${OUT_DIR}/polygon_pair_overlap_area_rows.json"

run_step polygon_set_jaccard \
  "${PYTHON_BIN}" scripts/goal1955_rawkernel_control_app_perf.py \
    --apps polygon_set_jaccard \
    --copies "${POLYGON_COPIES}" \
    --partner cupy \
    --candidate-backend "${polygon_candidate_backend}" \
    --repeats "${REPEATS}" \
    --warmups "${WARMUPS}" \
    --source-commit-label "${SOURCE_COMMIT_LABEL}" \
    --output "${OUT_DIR}/polygon_set_jaccard.json"

"${PYTHON_BIN}" - "${OUT_DIR}" "${SOURCE_COMMIT_LABEL}" <<'PY' | tee "${OUT_DIR}/summary.json"
import json
import pathlib
import sys

out_dir = pathlib.Path(sys.argv[1])
source_commit_label = sys.argv[2]
artifacts = [
    out_dir / "database_analytics.json",
    out_dir / "graph_analytics.json",
    out_dir / "polygon_pair_overlap_area_rows.json",
    out_dir / "polygon_set_jaccard.json",
]
summary = {
    "goal": "Goal1956",
    "status": "pass",
    "source_commit_label": source_commit_label,
    "artifacts": [str(path) for path in artifacts],
    "results": [],
    "claim_boundary": {
        "v2_0_release_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_rt_core_speedup_claim_authorized": False,
        "local_linux_gtx1070_is_release_perf_evidence": False,
    },
}
for path in artifacts:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("source_commit_label") != source_commit_label:
        raise SystemExit(f"{path}: source_commit_label mismatch")
    if not data.get("all_match_v1_8_python_rtdl_oracle"):
        raise SystemExit(f"{path}: v1.8 oracle mismatch")
    result = data["results"][0]
    summary["results"].append({
        "app": result["app"],
        "copies": result["copies"],
        "candidate_backend": result["candidate_backend"],
        "v1_8_median_s": result["v1_8_python_rtdl_wall"]["median_s"],
        "v2_median_s": result["v2_rawkernel_wall"]["median_s"],
        "v2_vs_v1_8_ratio": result["v2_vs_v1_8_ratio"],
        "matches_v1_8_python_rtdl_oracle": result["matches_v1_8_python_rtdl_oracle"],
    })
print(json.dumps(summary, indent=2, sort_keys=True))
PY

echo "[goal1956] $(date -Iseconds) all steps completed" | tee -a "${OUT_DIR}/progress.log"

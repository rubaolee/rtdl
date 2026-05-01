#!/usr/bin/env bash
set -euo pipefail

# Goal1204 pod-side executor for repaired DB/Jaccard/road-hazard RTX evidence.
# This collects evidence only; it does not authorize public wording, release, or
# speedup claims.

ARCHIVE="${ARCHIVE:-/tmp/goal1204_rtdl_source_2026-05-01.tar.gz}"
EXPECTED_SHA256="${EXPECTED_SHA256:-}"
WORKDIR="${WORKDIR:-/workspace/rtdl_goal1204}"
SOURCE_DIR="${WORKDIR}/rtdl_staged_source"
RESULT_DIR="${RESULT_DIR:-docs/reports/goal1204_repaired_rtx_pod}"
RESULT_TGZ="${RESULT_TGZ:-/tmp/goal1204_repaired_rtx_pod.tgz}"
RESULT_SHA="${RESULT_SHA:-/tmp/goal1204_repaired_rtx_pod.tgz.sha256}"

echo "Goal1204 repaired RTX pod executor"
echo "archive=${ARCHIVE}"
echo "expected_sha256=${EXPECTED_SHA256}"
echo "workdir=${WORKDIR}"
echo "result_dir=${RESULT_DIR}"

if [ -z "${EXPECTED_SHA256}" ]; then
  echo "EXPECTED_SHA256 must be set." >&2
  exit 2
fi
if [ ! -f "${ARCHIVE}" ]; then
  echo "Archive not found: ${ARCHIVE}" >&2
  exit 2
fi

actual_sha256="$(sha256sum "${ARCHIVE}" | awk '{print $1}')"
echo "actual_sha256=${actual_sha256}"
if [ "${actual_sha256}" != "${EXPECTED_SHA256}" ]; then
  echo "Archive SHA256 mismatch." >&2
  exit 2
fi

rm -rf "${WORKDIR}"
mkdir -p "${WORKDIR}"
tar -xzf "${ARCHIVE}" -C "${WORKDIR}"
cd "${SOURCE_DIR}"

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y build-essential git cmake pkg-config libgeos-dev libembree-dev python3-dev python3-pip
apt-get install -y cuda-nvcc-13-0 cuda-nvrtc-dev-13-0 cuda-cudart-dev-13-0 || true

cat > .gitignore <<'EOF'
__pycache__/
*.pyc
*.pyo
*.o
*.a
*.so
*.dylib
build/
dist/
out/
docs/reports/
EOF

git init
git config user.email "pod@example.com"
git config user.name "RTDL Pod"
git add .
git commit -m "Goal1204 staged source archive"

export RTDL_SOURCE_COMMIT="goal1204-archive-${EXPECTED_SHA256}"
export PYTHONPATH="${PYTHONPATH:-src:.}"

mkdir -p "${RESULT_DIR}"
{
  echo "Goal1204 environment"
  date -u
  uname -a
  nvidia-smi || true
  python3 --version || true
  which nvcc || true
  nvcc --version || true
  sha256sum "${ARCHIVE}"
  echo "rtdl_source_commit=${RTDL_SOURCE_COMMIT}"
  git rev-parse HEAD
  git status --short
} | tee "${RESULT_DIR}/goal1204_environment.log"

mkdir -p /root/vendor
if [ ! -d /root/vendor/optix-dev ]; then
  git clone --depth 1 --branch v8.0.0 https://github.com/NVIDIA/optix-dev.git /root/vendor/optix-dev
fi

export OPTIX_PREFIX="${OPTIX_PREFIX:-/root/vendor/optix-dev}"
export CUDA_PREFIX="${CUDA_PREFIX:-/usr/local/cuda}"
export NVCC="${NVCC:-${CUDA_PREFIX}/bin/nvcc}"
export RTDL_OPTIX_PTX_COMPILER="${RTDL_OPTIX_PTX_COMPILER:-nvcc}"

package_results() {
  tar -czf "${RESULT_TGZ}" "${RESULT_DIR}"
  sha256sum "${RESULT_TGZ}" | tee "${RESULT_SHA}"
  echo "result_tgz=${RESULT_TGZ}"
  echo "result_sha=${RESULT_SHA}"
}

set +e
make build-optix OPTIX_PREFIX="${OPTIX_PREFIX}" CUDA_PREFIX="${CUDA_PREFIX}" NVCC="${NVCC}" \
  2>&1 | tee "${RESULT_DIR}/make_build_optix.log"
build_rc=${PIPESTATUS[0]}
set -e
python3 - "$build_rc" "${RESULT_DIR}/make_build_optix.log" "${RESULT_DIR}/make_build_optix.status.json" <<'PY'
import json
import sys
rc = int(sys.argv[1])
payload = {
    "label": "make_build_optix",
    "exit_code": rc,
    "log": sys.argv[2],
    "status": "ok" if rc == 0 else "failed",
}
open(sys.argv[3], "w", encoding="utf-8").write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
PY
if [ "${build_rc}" -ne 0 ]; then
  python3 - <<'PY' | tee "docs/reports/goal1204_repaired_rtx_pod/goal1204_status_summary.json"
import json
payload = {
    "goal": "Goal1204 repaired RTX pod execution",
    "status_count": 1,
    "failed_count": 1,
    "failed_labels": ["make_build_optix"],
    "boundary": "Build failed before benchmark execution; partial artifact package is preserved for copy-back. No public claims are authorized.",
}
print(json.dumps(payload, indent=2, sort_keys=True))
PY
  package_results
  exit "${build_rc}"
fi

run_step() {
  local label="$1"
  local command="$2"
  local log="${RESULT_DIR}/${label}.log"
  local status="${RESULT_DIR}/${label}.status.json"
  echo "BEGIN ${label}" | tee "${log}"
  echo "${command}" | tee -a "${log}"
  set +e
  bash -lc "${command}" >> "${log}" 2>&1
  local rc=$?
  set -e
  python3 - "$label" "$rc" "$command" "$log" "$status" <<'PY'
import json
import sys
label, rc, command, log_path, status_path = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5]
payload = {
    "label": label,
    "exit_code": rc,
    "command": command,
    "log": log_path,
    "status": "ok" if rc == 0 else "failed",
}
open(status_path, "w", encoding="utf-8").write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
PY
  echo "END ${label} rc=${rc}" | tee -a "${log}"
}

run_step "db_embree_100000_chunked_repair" \
  "python3 scripts/goal756_db_prepared_session_perf.py --backend embree --scenario sales_risk --copies 100000 --iterations 3 --output-mode compact_summary --strict --output-json ${RESULT_DIR}/db_embree_100000_chunked_repair.json"
run_step "db_optix_100000_chunked_repair" \
  "python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario sales_risk --copies 100000 --iterations 3 --output-mode compact_summary --strict --output-json ${RESULT_DIR}/db_optix_100000_chunked_repair.json"
run_step "db_embree_300000_chunked_repair" \
  "python3 scripts/goal756_db_prepared_session_perf.py --backend embree --scenario sales_risk --copies 300000 --iterations 2 --output-mode compact_summary --strict --output-json ${RESULT_DIR}/db_embree_300000_chunked_repair.json"
run_step "db_optix_300000_chunked_repair" \
  "python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario sales_risk --copies 300000 --iterations 2 --output-mode compact_summary --strict --output-json ${RESULT_DIR}/db_optix_300000_chunked_repair.json"

run_step "jaccard_optix_8192_public_safe_chunk_512" \
  "python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app jaccard --mode optix --copies 8192 --output-mode summary --validation-mode analytic_summary --chunk-copies 512 --output-json ${RESULT_DIR}/jaccard_optix_8192_public_safe_chunk_512.json"
run_step "jaccard_optix_8192_diagnostic_chunk_64" \
  "python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app jaccard --mode optix --copies 8192 --output-mode summary --validation-mode analytic_summary --chunk-copies 64 --output-json ${RESULT_DIR}/jaccard_optix_8192_diagnostic_chunk_64.json"

run_step "road_hazard_embree_control_40000" \
  "python3 examples/rtdl_road_hazard_screening.py --backend embree --copies 40000 --output-mode summary > ${RESULT_DIR}/road_hazard_embree_control_40000.json"
run_step "road_hazard_optix_control_40000" \
  "python3 scripts/goal933_prepared_segment_polygon_optix_profiler.py --scenario road_hazard_prepared_summary --copies 40000 --iterations 5 --mode run --output-json ${RESULT_DIR}/road_hazard_optix_control_40000.json"

python3 - <<'PY' | tee "docs/reports/goal1204_repaired_rtx_pod/goal1204_status_summary.json"
import json
from pathlib import Path
result = Path("docs/reports/goal1204_repaired_rtx_pod")
statuses = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(result.glob("*.status.json"))]
payload = {
    "goal": "Goal1204 repaired RTX pod execution",
    "status_count": len(statuses),
    "failed_count": sum(1 for row in statuses if row["exit_code"] != 0),
    "failed_labels": [row["label"] for row in statuses if row["exit_code"] != 0],
    "statuses": statuses,
    "boundary": "Execution summary only; no public wording, release, or speedup claims are authorized.",
}
print(json.dumps(payload, indent=2, sort_keys=True))
PY

package_results
echo "Goal1204 complete"

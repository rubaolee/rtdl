#!/usr/bin/env bash
set -euo pipefail

# Goal1200 pod-side executor for the reviewed Goal1197/Goal1199 OptiX-slower
# investigation plan. This collects evidence only; it does not authorize public
# wording, release, or speedup claims.

ARCHIVE="${ARCHIVE:-/tmp/goal1200_rtdl_source_2026-04-30.tar.gz}"
EXPECTED_SHA256="${EXPECTED_SHA256:-}"
WORKDIR="${WORKDIR:-/workspace/rtdl_goal1200}"
SOURCE_DIR="${WORKDIR}/rtdl_staged_source"
RESULT_DIR="${RESULT_DIR:-docs/reports/goal1200_optix_slower_app_investigation}"
RESULT_TGZ="${RESULT_TGZ:-/tmp/goal1200_optix_slower_app_investigation.tgz}"
RESULT_SHA="${RESULT_SHA:-/tmp/goal1200_optix_slower_app_investigation.tgz.sha256}"

echo "Goal1200 OptiX slower-app investigation pod executor"
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
git commit -m "Goal1200 staged source archive"

export RTDL_SOURCE_COMMIT="goal1200-archive-${EXPECTED_SHA256}"
export PYTHONPATH="${PYTHONPATH:-src:.}"

mkdir -p "${RESULT_DIR}"
{
  echo "Goal1200 environment"
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
} | tee "${RESULT_DIR}/goal1200_environment.log"

mkdir -p /root/vendor
if [ ! -d /root/vendor/optix-dev ]; then
  git clone --depth 1 --branch v8.0.0 https://github.com/NVIDIA/optix-dev.git /root/vendor/optix-dev
fi

export OPTIX_PREFIX="${OPTIX_PREFIX:-/root/vendor/optix-dev}"
export CUDA_PREFIX="${CUDA_PREFIX:-/usr/local/cuda}"
export NVCC="${NVCC:-${CUDA_PREFIX}/bin/nvcc}"
export RTDL_OPTIX_PTX_COMPILER="${RTDL_OPTIX_PTX_COMPILER:-nvcc}"

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
  python3 - <<'PY' | tee "docs/reports/goal1200_optix_slower_app_investigation/goal1200_status_summary.json"
import json
payload = {
    "goal": "Goal1200 OptiX slower-app investigation pod execution",
    "status_count": 1,
    "failed_count": 1,
    "failed_labels": ["make_build_optix"],
    "boundary": "Build failed before benchmark execution; partial artifact package is preserved for copy-back. No public wording, release, or speedup claims are authorized.",
}
print(json.dumps(payload, indent=2, sort_keys=True))
PY
  tar -czf "${RESULT_TGZ}" "${RESULT_DIR}"
  sha256sum "${RESULT_TGZ}" | tee "${RESULT_SHA}"
  echo "Goal1200 build failed; partial result package created."
  echo "result_tgz=${RESULT_TGZ}"
  echo "result_sha=${RESULT_SHA}"
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

db_iterations() {
  case "$1" in
    300000) echo 5 ;;
    *) echo 10 ;;
  esac
}

for copies in 30000 100000 300000; do
  iterations="$(db_iterations "${copies}")"
  run_step "db_embree_${copies}" \
    "python3 scripts/goal756_db_prepared_session_perf.py --backend embree --scenario sales_risk --copies ${copies} --iterations ${iterations} --output-mode compact_summary --strict --output-json ${RESULT_DIR}/db_embree_${copies}.json"
  run_step "db_optix_${copies}" \
    "python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario sales_risk --copies ${copies} --iterations ${iterations} --output-mode compact_summary --strict --output-json ${RESULT_DIR}/db_optix_${copies}.json"
done

for copies in 30000 60000 120000; do
  run_step "graph_embree_visibility_${copies}" \
    "python3 examples/rtdl_graph_analytics_app.py --backend embree --scenario visibility_edges --copies ${copies} --output-mode summary > ${RESULT_DIR}/graph_embree_visibility_${copies}.json"
  run_step "graph_optix_visibility_${copies}" \
    "python3 scripts/goal889_graph_visibility_optix_gate.py --copies ${copies} --output-mode summary --validation-mode analytic_summary --chunk-copies 0 --strict --output-json ${RESULT_DIR}/graph_optix_visibility_${copies}.json"
done

for copies in 10000 20000 40000; do
  run_step "polygon_pair_embree_${copies}" \
    "python3 examples/rtdl_polygon_pair_overlap_area_rows.py --backend embree --copies ${copies} --output-mode summary > ${RESULT_DIR}/polygon_pair_embree_${copies}.json"
  run_step "polygon_pair_optix_${copies}" \
    "python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app pair_overlap --mode optix --copies ${copies} --output-mode summary --validation-mode analytic_summary --chunk-copies 100 --output-json ${RESULT_DIR}/polygon_pair_optix_${copies}.json"
done

run_step "polygon_jaccard_embree_8192" \
  "python3 examples/rtdl_polygon_set_jaccard.py --backend embree --copies 8192 --output-mode summary > ${RESULT_DIR}/polygon_jaccard_embree_8192.json"
for chunk in 1 8 64 512; do
  run_step "polygon_jaccard_optix_8192_chunk_${chunk}" \
    "python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app jaccard --mode optix --copies 8192 --output-mode summary --validation-mode analytic_summary --chunk-copies ${chunk} --output-json ${RESULT_DIR}/polygon_jaccard_optix_8192_chunk_${chunk}.json"
done

run_step "road_hazard_embree_control_20000" \
  "python3 examples/rtdl_road_hazard_screening.py --backend embree --copies 20000 --output-mode summary > ${RESULT_DIR}/road_hazard_embree_control_20000.json"
run_step "road_hazard_optix_control_20000" \
  "python3 scripts/goal933_prepared_segment_polygon_optix_profiler.py --scenario road_hazard_prepared_summary --copies 20000 --iterations 5 --mode run --output-json ${RESULT_DIR}/road_hazard_optix_control_20000.json"

for copies in 2000 10000 20000; do
  run_step "hausdorff_embree_repair_${copies}" \
    "timeout 600s python3 examples/rtdl_hausdorff_distance_app.py --backend embree --copies ${copies} --embree-result-mode directed_summary --hausdorff-threshold 0.4 > ${RESULT_DIR}/hausdorff_embree_repair_${copies}.json"
done
for copies in 200000 1200000; do
  run_step "hausdorff_optix_repair_${copies}" \
    "timeout 600s python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario hausdorff_threshold --mode optix --copies ${copies} --iterations 3 --radius 0.4 --output-json ${RESULT_DIR}/hausdorff_optix_repair_${copies}.json"
done

python3 - <<'PY' | tee "docs/reports/goal1200_optix_slower_app_investigation/goal1200_status_summary.json"
import json
from pathlib import Path
result = Path("docs/reports/goal1200_optix_slower_app_investigation")
statuses = []
for path in sorted(result.glob("*.status.json")):
    statuses.append(json.loads(path.read_text(encoding="utf-8")))
payload = {
    "goal": "Goal1200 OptiX slower-app investigation pod execution",
    "status_count": len(statuses),
    "failed_count": sum(1 for row in statuses if row["exit_code"] != 0),
    "failed_labels": [row["label"] for row in statuses if row["exit_code"] != 0],
    "statuses": statuses,
    "boundary": "Execution summary only; no public wording, release, or speedup claims are authorized.",
}
print(json.dumps(payload, indent=2, sort_keys=True))
PY

tar -czf "${RESULT_TGZ}" "${RESULT_DIR}"
sha256sum "${RESULT_TGZ}" | tee "${RESULT_SHA}"

echo "Goal1200 complete"
echo "result_tgz=${RESULT_TGZ}"
echo "result_sha=${RESULT_SHA}"

#!/usr/bin/env bash
set -euo pipefail

ARCHIVE="${ARCHIVE:-/tmp/goal1267_rtdl_source_2026-05-05.tar.gz}"
EXPECTED_SHA256="${EXPECTED_SHA256:-}"
WORKDIR="${WORKDIR:-/workspace/rtdl_goal1267}"
SOURCE_DIR="${WORKDIR}/rtdl_staged_source"
RESULT_DIR="${RESULT_DIR:-docs/reports/goal1267_v1_2_optix_targeted_pod_results}"
RESULT_TGZ="${RESULT_TGZ:-/tmp/goal1267_v1_2_optix_targeted_pod_results.tgz}"
RESULT_SHA="${RESULT_SHA:-/tmp/goal1267_v1_2_optix_targeted_pod_results.tgz.sha256}"

echo "Goal1267 v1.2 targeted OptiX pod executor"
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
git commit -m "Goal1267 staged source archive"

export RTDL_SOURCE_COMMIT="goal1267-archive-${EXPECTED_SHA256}"
export PYTHONPATH="${PYTHONPATH:-src:.}"

mkdir -p "${RESULT_DIR}"
{
  echo "Goal1267 environment"
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
} | tee "${RESULT_DIR}/goal1267_environment.log"

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

if [ "${build_rc}" -eq 0 ]; then
  for copies in 30000 60000; do
    run_step "graph_embree_visibility_${copies}" \
      "python3 examples/rtdl_graph_analytics_app.py --backend embree --scenario visibility_edges --copies ${copies} --output-mode summary > ${RESULT_DIR}/graph_embree_visibility_${copies}.json"
    run_step "graph_optix_visibility_${copies}" \
      "python3 scripts/goal889_graph_visibility_optix_gate.py --copies ${copies} --output-mode summary --validation-mode analytic_summary --chunk-copies 0 --strict --output-json ${RESULT_DIR}/graph_optix_visibility_${copies}.json"
  done

  for copies in 40000 80000 160000; do
    run_step "polygon_pair_embree_${copies}" \
      "python3 examples/rtdl_polygon_pair_overlap_area_rows.py --backend embree --copies ${copies} --output-mode summary > ${RESULT_DIR}/polygon_pair_embree_${copies}.json"
    run_step "polygon_pair_optix_${copies}" \
      "python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app pair_overlap --mode optix --copies ${copies} --output-mode summary --validation-mode analytic_summary --chunk-copies 512 --output-json ${RESULT_DIR}/polygon_pair_optix_${copies}.json"
  done

  for copies in 100000 300000; do
    run_step "db_embree_sales_risk_${copies}" \
      "python3 scripts/goal756_db_prepared_session_perf.py --backend embree --scenario sales_risk --copies ${copies} --iterations 5 --output-mode compact_summary --strict --output-json ${RESULT_DIR}/db_embree_sales_risk_${copies}.json"
    run_step "db_optix_sales_risk_${copies}" \
      "python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario sales_risk --copies ${copies} --iterations 5 --output-mode compact_summary --strict --output-json ${RESULT_DIR}/db_optix_sales_risk_${copies}.json"
  done

  for copies in 4096 8192; do
    run_step "polygon_jaccard_embree_${copies}" \
      "python3 examples/rtdl_polygon_set_jaccard.py --backend embree --copies ${copies} --output-mode summary > ${RESULT_DIR}/polygon_jaccard_embree_${copies}.json"
    run_step "polygon_jaccard_optix_${copies}_chunk_1024" \
      "python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app jaccard --mode optix --copies ${copies} --output-mode summary --validation-mode analytic_summary --chunk-copies 1024 --output-json ${RESULT_DIR}/polygon_jaccard_optix_${copies}_chunk_1024.json"
  done
fi

python3 - "${RESULT_DIR}" <<'PY' | tee "${RESULT_DIR}/goal1267_graph_ray_pack_metadata.json"
import json
import sys
from pathlib import Path

result = Path(sys.argv[1])
rows = []
for path in sorted(result.glob("graph_optix_visibility_*.json")):
    payload = json.loads(path.read_text(encoding="utf-8"))
    for record in payload.get("records", []):
        if record.get("label") != "optix_visibility_anyhit":
            continue
        section_phases = record.get("section_run_phases", {})
        rows.append({
            "artifact": str(path),
            "copies": payload.get("copies"),
            "ray_pack_mode": record.get("ray_pack_mode"),
            "blocker_pack_mode": record.get("blocker_pack_mode"),
            "has_ray_pack_mode": "ray_pack_mode" in record,
            "has_blocker_pack_mode": "blocker_pack_mode" in record,
            "ray_pack_sec": section_phases.get("ray_pack_sec"),
            "scene_prepare_sec": section_phases.get("scene_prepare_sec"),
            "ray_prepare_sec": section_phases.get("ray_prepare_sec"),
            "query_anyhit_count_sec": section_phases.get("query_anyhit_count_sec"),
        })
summary = {
    "goal": "Goal1267 graph ray-pack metadata check",
    "artifact_count": len(rows),
    "all_numpy_packed_rays": bool(rows) and all(row["ray_pack_mode"] == "numpy_packed_rays" for row in rows),
    "all_numpy_packed_triangles": (
        bool(rows) and all(row["blocker_pack_mode"] == "numpy_packed_triangles" for row in rows)
    ),
    "rows": rows,
    "boundary": "Diagnostic metadata only; no public speedup claim is authorized.",
}
print(json.dumps(summary, indent=2, sort_keys=True))
PY

python3 - "${RESULT_DIR}" <<'PY' | tee "${RESULT_DIR}/goal1267_status_summary.json"
import json
import sys
from pathlib import Path

result = Path(sys.argv[1])
statuses = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(result.glob("*.status.json"))]
payload = {
    "goal": "Goal1267 v1.2 targeted OptiX pod execution",
    "status_count": len(statuses),
    "failed_count": sum(1 for row in statuses if row["exit_code"] != 0),
    "failed_labels": [row["label"] for row in statuses if row["exit_code"] != 0],
    "statuses": statuses,
    "boundary": "Execution summary only; no public wording, release, or speedup claims are authorized.",
    "allowed_exit": "optix_improved or optix_still_slower_with_reason after separate intake.",
    "metadata_checks": ["goal1267_graph_ray_pack_metadata.json"],
}
print(json.dumps(payload, indent=2, sort_keys=True))
PY

tar -czf "${RESULT_TGZ}" "${RESULT_DIR}"
sha256sum "${RESULT_TGZ}" | tee "${RESULT_SHA}"

echo "Goal1267 complete"
echo "result_tgz=${RESULT_TGZ}"
echo "result_sha=${RESULT_SHA}"

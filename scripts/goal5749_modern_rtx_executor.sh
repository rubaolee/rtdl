#!/usr/bin/env bash
set -euo pipefail

# Goal5749 functional-only RTX executor.  It consumes a self-contained bundle,
# writes into one create-only output root and performs no performance timing.

if [[ $# -ne 1 ]]; then
  echo "usage: $0 ABSOLUTE_CREATE_ONLY_OUTPUT_ROOT" >&2
  exit 2
fi

BUNDLE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PAYLOAD_ROOT="${BUNDLE_ROOT}/payload"
OUTPUT_ROOT="$1"
if [[ "${OUTPUT_ROOT}" != /* || -e "${OUTPUT_ROOT}" ]]; then
  echo "output root must be absolute and not already exist: ${OUTPUT_ROOT}" >&2
  exit 2
fi

for command_name in sha256sum tar dpkg-deb make nvidia-smi /usr/bin/python3.12; do
  command -v "${command_name}" >/dev/null 2>&1 || {
    echo "missing required command before functional execution: ${command_name}" >&2
    exit 3
  }
done

cd "${BUNDLE_ROOT}"
sha256sum -c BUNDLE_PAYLOADS.sha256

GPU_ROWS="$(nvidia-smi --query-gpu=name,driver_version,uuid,compute_cap --format=csv,noheader)"
if [[ "$(printf '%s\n' "${GPU_ROWS}" | sed '/^[[:space:]]*$/d' | wc -l)" -ne 1 ]]; then
  echo "Goal5749 requires exactly one visible GPU" >&2
  exit 4
fi
IFS=',' read -r GPU_NAME GPU_DRIVER GPU_UUID GPU_CC <<<"${GPU_ROWS}"
trim() { local value="$1"; value="${value#"${value%%[![:space:]]*}"}"; value="${value%"${value##*[![:space:]]}"}"; printf '%s' "${value}"; }
GPU_NAME="$(trim "${GPU_NAME}")"; GPU_DRIVER="$(trim "${GPU_DRIVER}")"
GPU_UUID="$(trim "${GPU_UUID}")"; GPU_CC="$(trim "${GPU_CC}")"
if [[ "${GPU_NAME}" != "NVIDIA RTX 4000 Ada Generation" || "${GPU_CC}" != "8.9" ]]; then
  echo "target mismatch: ${GPU_NAME} CC${GPU_CC}; expected NVIDIA RTX 4000 Ada Generation CC8.9" >&2
  exit 4
fi

mkdir "${OUTPUT_ROOT}"
WORK_ROOT="${OUTPUT_ROOT}/work"
mkdir "${WORK_ROOT}" "${WORK_ROOT}/toolchain" "${WORK_ROOT}/optix" \
      "${WORK_ROOT}/python_site" "${OUTPUT_ROOT}/preserved_before_worker_zero"

for package in "${PAYLOAD_ROOT}"/cuda_debs/*.deb; do
  dpkg-deb -x "${package}" "${WORK_ROOT}/toolchain"
done
CUDA_ROOT="${WORK_ROOT}/toolchain/usr/local/cuda-12.8"
test -x "${CUDA_ROOT}/bin/nvcc"
"${CUDA_ROOT}/bin/nvcc" --version | grep -F 'V12.8.93'

tar -xzf "${PAYLOAD_ROOT}/optix9_include.tar.gz" -C "${WORK_ROOT}/optix"
OPTIX_ROOT="${WORK_ROOT}/optix"
grep -Eq '^#define[[:space:]]+OPTIX_VERSION[[:space:]]+90000[[:space:]]*$' \
  "${OPTIX_ROOT}/include/optix.h"

/usr/bin/python3.12 -m pip install --no-index --no-deps \
  --target "${WORK_ROOT}/python_site" "${PAYLOAD_ROOT}"/wheelhouse/*.whl \
  >"${OUTPUT_ROOT}/pip_install.log" 2>&1
env PYTHONPATH="${WORK_ROOT}/python_site" /usr/bin/python3.12 - <<'PY'
import numba, numpy, platform
assert platform.python_version() == "3.12.3", platform.python_version()
assert numba.__version__ == "0.65.1", numba.__version__
assert numpy.__version__ == "2.2.6", numpy.__version__
PY

tar -xzf "${PAYLOAD_ROOT}/source.tar.gz" -C "${WORK_ROOT}"
SOURCE_ROOT="${WORK_ROOT}/source"
test -f "${SOURCE_ROOT}/scripts/goal5749_v4_callback_poc_driver.py"

PATH="${CUDA_ROOT}/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" \
  make -C "${SOURCE_ROOT}" build-optix OPTIX_PREFIX="${OPTIX_ROOT}" \
    CUDA_PREFIX="${CUDA_ROOT}" >"${OUTPUT_ROOT}/native_build.log" 2>&1
NATIVE="${SOURCE_ROOT}/build/librtdl_optix.so"
test -f "${NATIVE}"

# Preserve the exact scientific source and native before the first functional
# GPU worker.  The driver performs the only bounded functional cohort below.
cp "${PAYLOAD_ROOT}/source.tar.gz" "${OUTPUT_ROOT}/preserved_before_worker_zero/EXECUTION_SOURCE.tar.gz"
cp "${NATIVE}" "${OUTPUT_ROOT}/preserved_before_worker_zero/librtdl_optix.so"
sha256sum "${OUTPUT_ROOT}/preserved_before_worker_zero/EXECUTION_SOURCE.tar.gz" \
  "${OUTPUT_ROOT}/preserved_before_worker_zero/librtdl_optix.so" \
  >"${OUTPUT_ROOT}/preserved_before_worker_zero/SHA256SUMS"

COMMON_ENV=(
  "PYTHONPATH=${SOURCE_ROOT}/src:${WORK_ROOT}/python_site"
  "LD_LIBRARY_PATH=${CUDA_ROOT}/nvvm/lib64:${CUDA_ROOT}/targets/x86_64-linux/lib:/usr/lib/x86_64-linux-gnu"
  "NUMBA_CUDA_NVVM=${CUDA_ROOT}/nvvm/lib64/libnvvm.so"
  "NUMBA_CUDA_LIBDEVICE=${CUDA_ROOT}/nvvm/libdevice/libdevice.10.bc"
  "RTDL_OPTIX_LIB=${NATIVE}"
  "RTDL_V4_CUDA_PREFIX=${CUDA_ROOT}"
  "RTDL_V4_OPTIX_PREFIX=${OPTIX_ROOT}"
  "RTDL_V4_SOURCE_ARCHIVE_SHA256=@SOURCE_ARCHIVE_SHA256@"
  "RTDL_V4_SOURCE_COMMIT=@SOURCE_COMMIT@"
)

env "PYTHONPATH=${SOURCE_ROOT}/src:${WORK_ROOT}/python_site" \
  /usr/bin/python3.12 \
  "${SOURCE_ROOT}/tests/goal5749_v4_callback_poc_test.py" -v \
  >"${OUTPUT_ROOT}/focused_tests.log" 2>&1

env -u RTDL_OPTIX_PTX_ARCH "${COMMON_ENV[@]}" /usr/bin/python3.12 \
  "${SOURCE_ROOT}/scripts/goal5749_v4_callback_poc_driver.py" \
  --lane modern_rtx_portability_confirmation \
  --output "${OUTPUT_ROOT}/functional" --run-native \
  >"${OUTPUT_ROOT}/functional_driver.log" 2>&1

env PYTHONPATH="${SOURCE_ROOT}/src:${WORK_ROOT}/python_site" \
  /usr/bin/python3.12 - "${OUTPUT_ROOT}" "${GPU_NAME}" "${GPU_DRIVER}" \
  "${GPU_UUID}" "${GPU_CC}" <<'PY'
import hashlib, json, pathlib, sys
root = pathlib.Path(sys.argv[1])
result = json.loads((root / "functional/RESULT.json").read_text())
runs = result["functional_runs"]
diagnostics = result["diagnostic_runs"]
assert len(runs) == 8
assert {row["route"] for row in runs} == {"ordinary_composed", "direct_callable"}
assert all(all(value > 0 for value in row["callback_counters"]) for row in runs)
assert all(all(item["status"] == 0 for item in row["launch_status"]) for row in runs)
assert any(row["kind"] == "ab_semantic_mutation" and row["output_changed"] for row in diagnostics)
for kind in ("invalid_nonfinite_hit", "invalid_u32_overflow"):
    row = next(item for item in diagnostics if item["kind"] == kind)
    assert row["output_accepted"] is False
receipt = {
    "schema": "rtdl.goal5749.modern_rtx_transaction.v1",
    "goal": 5749,
    "gpu_name": sys.argv[2], "driver": sys.argv[3],
    "gpu_uuid": sys.argv[4], "compute_capability": sys.argv[5],
    "source_archive_sha256": "@SOURCE_ARCHIVE_SHA256@",
    "source_commit": "@SOURCE_COMMIT@",
    "native_sha256": hashlib.sha256((root / "preserved_before_worker_zero/librtdl_optix.so").read_bytes()).hexdigest(),
    "functional_result_sha256": hashlib.sha256((root / "functional/RESULT.json").read_bytes()).hexdigest(),
    "functional_run_count": 8,
    "diagnostic_run_count": len(diagnostics),
    "all_exact_and_behaviorally_true_optix": True,
    "registered_performance_timing_count": 0,
    "performance_claimed": False,
}
(root / "TRANSACTION_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
rows = []
for path in sorted(p for p in root.rglob("*") if p.is_file() and "work" not in p.parts and p.name != "EVIDENCE_MANIFEST.json"):
    rel = path.relative_to(root).as_posix()
    rows.append({"path": rel, "size": path.stat().st_size,
                 "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
(root / "EVIDENCE_MANIFEST.json").write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n")
print(json.dumps(receipt, sort_keys=True))
PY

echo "Goal5749 modern RTX functional transaction complete: ${OUTPUT_ROOT}"

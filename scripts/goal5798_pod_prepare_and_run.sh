#!/usr/bin/env bash
set -euo pipefail

bundle_root="$(cd "$(dirname "$0")" && pwd)"
run_root="${1:-/root/goal5798_run}"

test ! -e "$run_root"
(cd "$bundle_root" && sha256sum -c SHA256SUMS)
mkdir -p "$run_root"
cp -a "$bundle_root/source" "$run_root/source"
source_root="$run_root/source"
upstream="$run_root/upstream"
artifacts="$run_root/artifacts"
mkdir -p "$upstream" "$artifacts"

for command in git g++ make nvidia-smi sha256sum python3.12; do
  command -v "$command" >/dev/null || { echo "missing command: $command" >&2; exit 20; }
done
cuda_root="${CUDA_ROOT:-/usr/local/cuda}"
test -x "$cuda_root/bin/nvcc"
test -f "$cuda_root/include/cuda.h"

gpu_line="$(nvidia-smi --query-gpu=name,driver_version,compute_cap --format=csv,noheader | head -n 1)"
driver_version="$(printf '%s' "$gpu_line" | cut -d, -f2 | xargs)"
driver_branch="${driver_version%%.*}"
test "$driver_branch" -ge 590 || { echo "R590+ required: $gpu_line" >&2; exit 21; }
case "$gpu_line" in
  "NVIDIA RTX 4000 Ada Generation,"*) ;;
  *) echo "exact RTX 4000 Ada Generation required: $gpu_line" >&2; exit 22 ;;
esac

git init -q "$upstream/otk-pyoptix"
git -C "$upstream/otk-pyoptix" remote add origin https://github.com/NVIDIA/otk-pyoptix.git
git -C "$upstream/otk-pyoptix" fetch -q --depth 1 origin 3144f224c0fd18733925faf3d8fb82c7376b8dcf
git -C "$upstream/otk-pyoptix" checkout -q --detach FETCH_HEAD
test "$(git -C "$upstream/otk-pyoptix" rev-parse HEAD)" = 3144f224c0fd18733925faf3d8fb82c7376b8dcf

git init -q "$upstream/optix-dev"
git -C "$upstream/optix-dev" remote add origin https://github.com/NVIDIA/optix-dev.git
git -C "$upstream/optix-dev" fetch -q --depth 1 origin f1f6dd803f3159992d248178f6e09421c6eb8b6d
git -C "$upstream/optix-dev" checkout -q --detach FETCH_HEAD
test "$(git -C "$upstream/optix-dev" rev-parse HEAD)" = f1f6dd803f3159992d248178f6e09421c6eb8b6d

python3.12 -m venv --copies "$run_root/venv"
. "$run_root/venv/bin/activate"
python -m pip install --upgrade pip
python -m pip install \
  scikit-build-core==1.0.3 pybind11==3.1.0 ninja==1.13.0 \
  numpy==2.4.4 Pillow==10.2.0 numba==0.65.1 \
  cuda-pathfinder==1.6.1 cuda-bindings==12.9.7 cuda-python==12.9.7 \
  cupy-cuda12x==14.0.1 nvidia-ml-py==13.580.82
export PYOPTIX_CMAKE_ARGS="-DFETCHCONTENT_SOURCE_DIR_OPTIX_HEADERS=$upstream/optix-dev"
python -m pip install --no-build-isolation --no-deps "$upstream/otk-pyoptix"
python -c 'import importlib.metadata, optix; assert optix.version() == (9,1,0); assert importlib.metadata.version("pyoptix") == "9.1.0"'

make -C "$source_root" build-optix \
  OPTIX_PREFIX="$upstream/optix-dev" CUDA_PREFIX="$cuda_root" OPTIX_CUDA_ARCH=sm_89
native="$source_root/build/librtdl_optix.so"
test -s "$native"
direct="$artifacts/goal5798_direct_measurement"
bash "$source_root/experiments/goal5798_premeasurement/build_direct_measurement.sh" \
  "$upstream/optix-dev/include" "$cuda_root/include" "$direct"
test -x "$direct"

export PYTHONPATH="$source_root/src:$source_root"
export LD_LIBRARY_PATH="$cuda_root/lib64:${LD_LIBRARY_PATH:-}"
runtime_manifest="$source_root/experiments/goal5798_premeasurement/runtime_manifest_v5.json"
freeze="$source_root/history/internal_docs/goal5798_s0_premeasurement_design_freeze_v4_20260823.json"
python "$source_root/scripts/goal5798_bind_host.py" \
  --freeze "$freeze" --optix-header-repo "$upstream/optix-dev" \
  --pyoptix-repo "$upstream/otk-pyoptix" --output "$artifacts/host_binding.json"

python -m unittest \
  tests.goal5798_premeasurement_freeze_test \
  tests.goal5798_formal_harness_test -v \
  > "$artifacts/local_static_tests.stdout" 2> "$artifacts/local_static_tests.stderr"

python - "$native" "$direct" "$artifacts/prepare_result.json" <<'PY'
import hashlib, json, pathlib, platform, subprocess, sys
native, direct, output = map(pathlib.Path, sys.argv[1:])
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
value = {
  "schema": "rtdl.goal5798.pod_prepare_result.v1", "status": "PASS",
  "hostname": platform.node(),
  "gpu": subprocess.run(["nvidia-smi", "--query-gpu=name,driver_version,uuid,compute_cap,memory.total", "--format=csv,noheader"], check=True, text=True, capture_output=True).stdout.strip(),
  "rtdl_native_sha256": sha(native), "direct_binary_sha256": sha(direct),
  "formal_worker_count_executed": 0,
}
output.write_text(json.dumps(value, indent=2, sort_keys=True)+"\n")
print(json.dumps(value, sort_keys=True))
PY

if [ "${OWNER_AUTHORIZED_EXACT_GOAL5798:-NO}" != YES ]; then
  echo "PREPARE_COMPLETE__FORMAL_EXECUTION_NOT_AUTHORIZED"
  exit 0
fi

authority="$artifacts/execution_authority.json"
python "$source_root/scripts/goal5798_build_execution_authority.py" \
  --freeze "$freeze" --runtime-manifest "$runtime_manifest" \
  --host-binding "$artifacts/host_binding.json" \
  --direct-binary "$direct" --rtdl-native "$native" \
  --output "$authority" --owner-authorized-exact-goal5798

python "$source_root/experiments/goal5798_premeasurement/controller.py" \
  --freeze "$freeze" --runtime-manifest "$runtime_manifest" \
  --execution-authority "$authority" --output-root "$run_root/formal_result" \
  --python "$run_root/venv/bin/python" --direct-binary "$direct" \
  --device-source "$source_root/experiments/goal5796_matched/matched_device.cu" \
  --optix-include "$upstream/optix-dev/include" --cuda-include "$cuda_root/include" \
  --native "$native" --proof "$source_root/experiments/goal5796_matched/independent_oracle.py" \
  --optix-sdk 9.1.0

python "$source_root/scripts/goal5798_independent_recount.py" \
  --freeze "$freeze" --result-root "$run_root/formal_result" \
  --output "$artifacts/independent_recount.json"

tar --sort=name --mtime='@0' --owner=0 --group=0 --numeric-owner \
  -czf "$run_root/GOAL5798_EVIDENCE.tar.gz" \
  -C "$run_root" artifacts formal_result
sha256sum "$run_root/GOAL5798_EVIDENCE.tar.gz" | tee "$run_root/GOAL5798_EVIDENCE.tar.gz.sha256"


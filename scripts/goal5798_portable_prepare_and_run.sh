#!/usr/bin/env bash
set -euo pipefail

bundle_root="$(cd "$(dirname "$0")" && pwd)"
run_root="${1:-/root/goal5798_portable_run}"

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
if [ -n "${CUDA_ROOT:-}" ]; then
  cuda_root="$CUDA_ROOT"
else
  cuda_root="$(cd "$(dirname "$(command -v nvcc)")/.." && pwd)"
fi
test -x "$cuda_root/bin/nvcc"
test -f "$cuda_root/include/cuda.h"
# CUDA_ROOT is an explicit portable override.  Every later subprocess,
# including the host-binding recorder, must observe the same selected toolkit.
export PATH="$cuda_root/bin:$PATH"

# Ordinal zero is selected before any task or timing.  No model, capability,
# VRAM, correctness, or performance value participates in this choice.
export CUDA_VISIBLE_DEVICES=0
gpu_line="$(nvidia-smi --query-gpu=name,driver_version,compute_cap,memory.total --format=csv,noheader,nounits | head -n 1)"
driver_version="$(printf '%s' "$gpu_line" | cut -d, -f2 | xargs)"
compute_capability="$(printf '%s' "$gpu_line" | cut -d, -f3 | xargs)"
selector="$source_root/experiments/goal5798_premeasurement/compatibility.py"
optix_api="$(python3.12 "$selector" --driver "$driver_version" --field optix_api_version)"
optix_commit="$(python3.12 "$selector" --driver "$driver_version" --field optix_header_commit)"
stack_id="$(python3.12 "$selector" --driver "$driver_version" --field stack_id)"
printf '%s\n' "$gpu_line" > "$artifacts/observed_gpu_before_task.txt"
python3.12 "$selector" --driver "$driver_version" > "$artifacts/selected_stack_before_task.json"

pyoptix_commit=3144f224c0fd18733925faf3d8fb82c7376b8dcf
git init -q "$upstream/otk-pyoptix"
git -C "$upstream/otk-pyoptix" remote add origin https://github.com/NVIDIA/otk-pyoptix.git
git -C "$upstream/otk-pyoptix" fetch -q --depth 1 origin "$pyoptix_commit"
git -C "$upstream/otk-pyoptix" checkout -q --detach FETCH_HEAD
test "$(git -C "$upstream/otk-pyoptix" rev-parse HEAD)" = "$pyoptix_commit"

git init -q "$upstream/optix-dev"
git -C "$upstream/optix-dev" remote add origin https://github.com/NVIDIA/optix-dev.git
git -C "$upstream/optix-dev" fetch -q --depth 1 origin "$optix_commit"
git -C "$upstream/optix-dev" checkout -q --detach FETCH_HEAD
test "$(git -C "$upstream/optix-dev" rev-parse HEAD)" = "$optix_commit"

if python3.12 -c 'import ensurepip' >/dev/null 2>&1; then
  python3.12 -m venv --copies "$run_root/venv"
elif python3.12 -m virtualenv --version >/dev/null 2>&1; then
  python3.12 -m virtualenv --copies "$run_root/venv"
else
  python3.12 -m venv --without-pip --copies "$run_root/venv"
  python3.12 -m pip --python "$run_root/venv/bin/python" install pip
fi
. "$run_root/venv/bin/activate"
python -m pip install --upgrade pip
python -m pip install \
  scikit-build-core==1.0.3 pybind11==3.1.0 ninja==1.13.0 \
  numpy==2.4.4 Pillow==10.2.0 numba==0.65.1 \
  cuda-pathfinder==1.6.1 cuda-bindings==12.9.7 cuda-python==12.9.7 \
  cupy-cuda12x==14.0.1 nvidia-ml-py==13.580.82
export CMAKE_ARGS="-DFETCHCONTENT_SOURCE_DIR_OPTIX_HEADERS=$upstream/optix-dev"
export PYOPTIX_CMAKE_ARGS="$CMAKE_ARGS"
python -m pip install --no-build-isolation --no-deps "$upstream/otk-pyoptix"
python - "$optix_api" <<'PY'
import importlib.metadata, optix, sys
expected = tuple(int(value) for value in sys.argv[1].split('.'))
assert tuple(optix.version()) == expected, (optix.version(), expected)
assert importlib.metadata.version('pyoptix') == '9.1.0'
PY

cuda_arch="sm_$(printf '%s' "$compute_capability" | tr -d '.')"
make -C "$source_root" build-optix \
  OPTIX_PREFIX="$upstream/optix-dev" CUDA_PREFIX="$cuda_root" OPTIX_CUDA_ARCH="$cuda_arch"
native="$source_root/build/librtdl_optix.so"
test -s "$native"
direct="$artifacts/goal5798_direct_measurement"
bash "$source_root/experiments/goal5798_premeasurement/build_direct_measurement.sh" \
  "$upstream/optix-dev/include" "$cuda_root/include" "$direct"
test -x "$direct"

export PYTHONPATH="$source_root/src:$source_root"
export LD_LIBRARY_PATH="$cuda_root/lib64:${LD_LIBRARY_PATH:-}"
runtime_manifest="$source_root/experiments/goal5798_premeasurement/runtime_manifest_v13.json"
freeze="$source_root/history/internal_docs/goal5798_a2_optix76_compatible_premeasurement_freeze_v6_20260823.json"
python "$source_root/scripts/goal5798_bind_host.py" \
  --freeze "$freeze" --optix-header-repo "$upstream/optix-dev" \
  --pyoptix-repo "$upstream/otk-pyoptix" --output "$artifacts/host_binding.json"

python -m unittest \
  tests.goal5798_portable_environment_test \
  tests.goal5798_immutable_input_reuse_test -v \
  > "$artifacts/local_static_tests.stdout" 2> "$artifacts/local_static_tests.stderr"

python - "$native" "$direct" "$artifacts/prepare_result.json" "$stack_id" "$optix_api" <<'PY'
import hashlib, json, pathlib, platform, subprocess, sys
native, direct, output = map(pathlib.Path, sys.argv[1:4])
stack_id, optix_api = sys.argv[4:6]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
value = {
  "schema": "rtdl.goal5798.portable_prepare_result.v1", "status": "PASS",
  "hostname": platform.node(),
  "gpu": subprocess.run(["nvidia-smi", "--query-gpu=name,driver_version,uuid,compute_cap,memory.total", "--format=csv,noheader"], check=True, text=True, capture_output=True).stdout.strip().splitlines()[0],
  "selected_stack_id": stack_id, "selected_optix_api_version": optix_api,
  "gpu_model_filter_used": False, "preferred_driver_filter_used": False,
  "rtdl_native_sha256": sha(native), "direct_binary_sha256": sha(direct),
  "formal_worker_count_executed": 0,
}
output.write_text(json.dumps(value, indent=2, sort_keys=True)+"\n")
print(json.dumps(value, sort_keys=True))
PY

if [ "${OWNER_AUTHORIZED_GOAL5798_PORTABLE:-NO}" != YES ]; then
  echo "PORTABLE_PREPARE_COMPLETE__FORMAL_EXECUTION_NOT_AUTHORIZED"
  exit 0
fi

# Owner authority is necessary but no longer sufficient.  The v11 external
# review found that the prior formal run skipped its external premeasurement
# gate.  A returned review must now bind these exact candidate/runtime bytes.
external_gate="${GOAL5798_V12_EXTERNAL_PREEXECUTION_GATE:-}"
test -n "$external_gate"
python "$source_root/scripts/goal5798_verify_v12_external_gate.py" \
  --gate "$external_gate" --candidate-manifest "$bundle_root/MANIFEST.json" \
  --runtime-manifest "$runtime_manifest" \
  > "$artifacts/external_preexecution_gate.stdout"

authority="$artifacts/execution_authority.json"
python "$source_root/scripts/goal5798_build_execution_authority.py" \
  --freeze "$freeze" --runtime-manifest "$runtime_manifest" \
  --host-binding "$artifacts/host_binding.json" \
  --direct-binary "$direct" --rtdl-native "$native" \
  --output "$authority" --owner-authorized-goal5798-portable

python "$source_root/experiments/goal5798_premeasurement/controller.py" \
  --freeze "$freeze" --runtime-manifest "$runtime_manifest" \
  --execution-authority "$authority" --output-root "$run_root/formal_result" \
  --python "$run_root/venv/bin/python" --direct-binary "$direct" \
  --device-source "$source_root/experiments/goal5796_matched/matched_device.cu" \
  --optix-include "$upstream/optix-dev/include" --cuda-include "$cuda_root/include" \
  --native "$native" --proof "$source_root/experiments/goal5796_matched/independent_oracle.py"

python "$source_root/scripts/goal5798_independent_recount.py" \
  --freeze "$freeze" --result-root "$run_root/formal_result" \
  --output "$artifacts/independent_recount.json"

tar --sort=name --mtime='@0' --owner=0 --group=0 --numeric-owner \
  -czf "$run_root/GOAL5798_PORTABLE_EVIDENCE.tar.gz" \
  -C "$run_root" artifacts formal_result
sha256sum "$run_root/GOAL5798_PORTABLE_EVIDENCE.tar.gz" | tee \
  "$run_root/GOAL5798_PORTABLE_EVIDENCE.tar.gz.sha256"

#!/usr/bin/env bash
set +e

base="${BASE:-/root/rtdl_v3_rebuild_20260620}"
python_bin="${PYTHON_BIN:-$base/.venv/bin/python}"
required_gpu_name="${RTDL_REQUIRED_GPU_NAME:-NVIDIA RTX 4000 Ada Generation}"
required_driver_version="${RTDL_REQUIRED_DRIVER_VERSION:-550.127.05}"
required_compute_capability="${RTDL_REQUIRED_COMPUTE_CAPABILITY:-8.9}"
run_id="${RUN_ID:-phoenix_v3_serious_v2x_paired_$(date -u +%Y%m%d_%H%M%S)}"
run_dir="${ARTIFACT_DIR:-$base/artifacts/$run_id}"
log="$run_dir/main.log"
status="$run_dir/status.tsv"

mkdir -p "$run_dir"
: > "$status"

if [ "${PHOENIX_V3_ALLOW_ALL_APP_RUN:-0}" != "1" ] || [ "${PHOENIX_V3_RUNTIME_TRUNK_EXECUTED:-0}" != "1" ]; then
  {
    echo "===PHOENIX_V3_SERIOUS_V2X_PAIRED_BLOCKED $(date -Is)==="
    echo "reason=Phoenix V3 redesign Step 0 pauses all-app paired runs until the runtime trunk executes."
    echo "required=PHOENIX_V3_ALLOW_ALL_APP_RUN=1 and PHOENIX_V3_RUNTIME_TRUNK_EXECUTED=1"
    echo "controlling_doc=docs/rebuild/v3/phoenix_v3_redesign_step0_freeze_2026-06-22.md"
  } >> "$log" 2>&1
  printf "%s\t%s\t%s\t%s\t%s\n" "current" "phoenix_v3_serious_v2x_paired" "64" "$(date -Is)" "$(date -Is)" >> "$status"
  exit 64
fi

if [ ! -x "$python_bin" ]; then
  {
    echo "===PHOENIX_V3_SERIOUS_V2X_PAIRED_BLOCKED $(date -Is)==="
    echo "reason=Project venv interpreter is missing or not executable."
    echo "required=$python_bin"
  } >> "$log" 2>&1
  printf "%s\t%s\t%s\t%s\t%s\n" "current" "phoenix_v3_serious_v2x_paired" "65" "$(date -Is)" "$(date -Is)" >> "$status"
  exit 65
fi

export PATH="$(dirname "$python_bin"):$PATH"
export NUMBA_CUDA_PREFIX="${NUMBA_CUDA_PREFIX:-$base/.venv/lib/python3.12/site-packages/nvidia/cuda_nvcc}"
export CUDA_HOME="$NUMBA_CUDA_PREFIX"
export CUDA_PATH="$NUMBA_CUDA_PREFIX"
export PYTHONPATH="src:."

"$python_bin" - "$python_bin" <<'PY' >> "$log" 2>&1
import os
import sys

expected = sys.argv[1]
actual = sys.executable
print(f"python_preflight_expected={expected}")
print(f"python_preflight_actual={actual}")
if os.path.realpath(actual) != os.path.realpath(expected):
    raise SystemExit("sys.executable does not match the project venv interpreter")
PY
python_preflight_rc=$?
if [ "$python_preflight_rc" != "0" ]; then
  {
    echo "===PHOENIX_V3_SERIOUS_V2X_PAIRED_BLOCKED $(date -Is)==="
    echo "reason=Project venv sys.executable preflight failed."
    echo "rc=$python_preflight_rc"
  } >> "$log" 2>&1
  printf "%s\t%s\t%s\t%s\t%s\n" "current" "phoenix_v3_serious_v2x_paired" "66" "$(date -Is)" "$(date -Is)" >> "$status"
  exit 66
fi

gpu_csv=$(nvidia-smi --query-gpu=name,driver_version,compute_cap --format=csv,noheader 2>> "$log" | head -n 1)
gpu_query_rc=$?
gpu_name=$(printf "%s" "$gpu_csv" | cut -d, -f1 | sed 's/^ *//;s/ *$//')
gpu_driver_version=$(printf "%s" "$gpu_csv" | cut -d, -f2 | sed 's/^ *//;s/ *$//')
gpu_compute_capability=$(printf "%s" "$gpu_csv" | cut -d, -f3 | sed 's/^ *//;s/ *$//')
{
  echo "gpu_preflight_name=$gpu_name"
  echo "gpu_preflight_driver=$gpu_driver_version"
  echo "gpu_preflight_compute_capability=$gpu_compute_capability"
} >> "$log" 2>&1
if [ "$gpu_query_rc" != "0" ] \
  || [ "$gpu_name" != "$required_gpu_name" ] \
  || [ "$gpu_driver_version" != "$required_driver_version" ] \
  || [ "$gpu_compute_capability" != "$required_compute_capability" ]; then
  {
    echo "===PHOENIX_V3_SERIOUS_V2X_PAIRED_BLOCKED $(date -Is)==="
    echo "reason=Required GPU identity preflight failed."
    echo "required_gpu_name=$required_gpu_name"
    echo "required_driver_version=$required_driver_version"
    echo "required_compute_capability=$required_compute_capability"
    echo "actual_gpu_name=$gpu_name"
    echo "actual_driver_version=$gpu_driver_version"
    echo "actual_compute_capability=$gpu_compute_capability"
    echo "rc=$gpu_query_rc"
  } >> "$log" 2>&1
  printf "%s\t%s\t%s\t%s\t%s\n" "current" "phoenix_v3_serious_v2x_paired" "67" "$(date -Is)" "$(date -Is)" >> "$status"
  exit 67
fi

"$python_bin" - <<'PY' >> "$log" 2>&1
import importlib

for name in ("cupy", "numba"):
    module = importlib.import_module(name)
    print(f"required_import_preflight_{name}={getattr(module, '__version__', '?')}")
PY
required_import_rc=$?
if [ "$required_import_rc" != "0" ]; then
  {
    echo "===PHOENIX_V3_SERIOUS_V2X_PAIRED_BLOCKED $(date -Is)==="
    echo "reason=Required project venv import preflight failed."
    echo "required_imports=cupy,numba"
    echo "rc=$required_import_rc"
  } >> "$log" 2>&1
  printf "%s\t%s\t%s\t%s\t%s\n" "current" "phoenix_v3_serious_v2x_paired" "68" "$(date -Is)" "$(date -Is)" >> "$status"
  exit 68
fi

for tree in current v2_14; do
  (
    cd "$base/$tree" || exit 97
    PYTHON_BIN="$python_bin" "$python_bin" - "$python_bin" "$tree" <<'PY'
import os
import subprocess
import sys

expected = sys.argv[1]
tree = sys.argv[2]
sys.path.insert(0, "scripts")
import goal2626_benchmark_embree_optix_baseline as goal2626
import goal3828_current_benchmark_scale_profile_runner as goal3828

goal2626_cmd = goal2626._py("-c", "import sys; print(sys.executable)")
goal2626_child = subprocess.check_output(goal2626_cmd, text=True).strip()
goal3828_cmd = goal3828._row_command(
    {"command": ["python", "-c", "import sys; print(sys.executable)"]},
    use_current_python=True,
)
goal3828_child = subprocess.check_output(goal3828_cmd, text=True).strip()
print(f"child_interpreter_preflight_{tree}_goal2626_cmd0={goal2626_cmd[0]}")
print(f"child_interpreter_preflight_{tree}_goal2626_child={goal2626_child}")
print(f"child_interpreter_preflight_{tree}_goal3828_cmd0={goal3828_cmd[0]}")
print(f"child_interpreter_preflight_{tree}_goal3828_child={goal3828_child}")
for label, value in (
    ("goal2626_cmd0", goal2626_cmd[0]),
    ("goal2626_child", goal2626_child),
    ("goal3828_cmd0", goal3828_cmd[0]),
    ("goal3828_child", goal3828_child),
):
    if os.path.realpath(value) != os.path.realpath(expected):
        raise SystemExit(f"{tree} {label} does not match project venv interpreter")
PY
  ) >> "$log" 2>&1
  child_interpreter_rc=$?
  if [ "$child_interpreter_rc" != "0" ]; then
    {
      echo "===PHOENIX_V3_SERIOUS_V2X_PAIRED_BLOCKED $(date -Is)==="
      echo "reason=Benchmark child interpreter preflight failed."
      echo "tree=$tree"
      echo "required_child_interpreter=$python_bin"
      echo "rc=$child_interpreter_rc"
    } >> "$log" 2>&1
    printf "%s\t%s\t%s\t%s\t%s\n" "$tree" "phoenix_v3_serious_v2x_paired" "69" "$(date -Is)" "$(date -Is)" >> "$status"
    exit 69
  fi
done

{
  echo "===PHOENIX_V3_SERIOUS_V2X_PAIRED_START $(date -Is)==="
  echo "base=$base"
  echo "run_dir=$run_dir"
  echo "python_bin=$python_bin"
  nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader || true
  "$python_bin" --version
  "$python_bin" - <<'PY' || true
import importlib
for name in ["numpy", "cupy", "torch", "numba", "numba_cuda", "cuda"]:
    try:
        m = importlib.import_module(name)
        print(name, getattr(m, "__version__", "?"), getattr(m, "__file__", "?"))
    except Exception as exc:
        print(name, "IMPORT_FAIL", repr(exc))
PY
} >> "$log" 2>&1

if [ -d "$base/current/data/rayjoin_public_cdb" ]; then
  mkdir -p "$base/v2_14/data"
  ln -sfn "$base/current/data/rayjoin_public_cdb" "$base/v2_14/data/rayjoin_public_cdb"
  {
    echo "v2_14_public_cdb_symlink=$base/v2_14/data/rayjoin_public_cdb"
    ls -ld "$base/v2_14/data/rayjoin_public_cdb"
  } >> "$log" 2>&1
fi

run_cmd() {
  local tree="$1"; shift
  local suite="$1"; shift
  local cwd="$base/$tree"
  local started ended rc
  started=$(date -Is)
  {
    echo "===BEGIN $tree:$suite $started==="
    echo "cwd=$cwd"
    cd "$cwd" || rc=97
    if [ -z "${rc+x}" ]; then
      export PYTHONPATH="src:."
      export RTDL_OPTIX_LIBRARY="$cwd/build/librtdl_optix.so"
      export RTDL_EMBREE_LIBRARY="$cwd/build/librtdl_embree.so"
      git rev-parse HEAD 2>/dev/null || true
      git describe --tags --always 2>/dev/null || true
      echo "CMD: $*"
      "$@"
      rc=$?
    fi
    ended=$(date -Is)
    echo "===END $tree:$suite rc=$rc $ended==="
    printf "%s\t%s\t%s\t%s\t%s\n" "$tree" "$suite" "$rc" "$started" "$ended" >> "$status"
  } >> "$log" 2>&1
  unset rc
  return 0
}

for tree in v2_14 current; do
  mkdir -p \
    "$run_dir/${tree}_goal2626_large" \
    "$run_dir/${tree}_goal2636_stress" \
    "$run_dir/${tree}_goal3828_full"

  run_cmd "$tree" goal2626_large \
    "$python_bin" scripts/goal2626_benchmark_embree_optix_baseline.py \
      --scale large \
      --artifact-dir "$run_dir/${tree}_goal2626_large" \
      --case-repeat 3 \
      --timeout-sec 2400

  run_cmd "$tree" goal2636_stress \
    "$python_bin" scripts/goal2636_strengthen_benchmark_rows.py \
      --tier stress \
      --artifact-dir "$run_dir/${tree}_goal2636_stress" \
      --case-repeat 3 \
      --timeout-sec 3600

  run_cmd "$tree" goal3828_full \
    "$python_bin" scripts/goal3828_current_benchmark_scale_profile_runner.py \
      --output-json "$run_dir/${tree}_goal3828_full.json" \
      --output-dir "$run_dir/${tree}_goal3828_full" \
      --heartbeat-sec 20 \
      --timeout-scale 3 \
      --materialize-rayjoin-public-cdb
done

{
  echo "===PHOENIX_V3_SERIOUS_V2X_PAIRED_END $(date -Is)==="
  echo "status.tsv:"
  cat "$status"
} >> "$log" 2>&1

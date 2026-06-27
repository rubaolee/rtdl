#!/usr/bin/env bash
set +e
base=/root/rtdl_v3_rebuild_20260620
run_dir=$(cd "$(dirname "$0")" && pwd)
log="$run_dir/main.log"
status="$run_dir/status.tsv"
: > "$status"
export PATH="$base/.venv/bin:$PATH"
export NUMBA_CUDA_PREFIX="$base/.venv/lib/python3.12/site-packages/nvidia/cuda_nvcc"
export CUDA_HOME="$NUMBA_CUDA_PREFIX"
export CUDA_PATH="$NUMBA_CUDA_PREFIX"
{
  echo "===PAIRED_V2_14_V3_START $(date -Is)==="
  echo "run_dir=$run_dir"
  nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader || true
  python3 --version
  python3 - <<'PY' || true
import importlib
for name in ['numpy','cupy','torch','numba','numba_cuda','cuda']:
    try:
        m=importlib.import_module(name)
        print(name, getattr(m,'__version__','?'), getattr(m,'__file__','?'))
    except Exception as e:
        print(name, 'IMPORT_FAIL', repr(e))
PY
} >> "$log" 2>&1
run_cmd() {
  local tree="$1"; shift
  local suite="$1"; shift
  local cwd="$base/$tree"
  local started ended rc
  started=$(date -Is)
  {
    echo "===BEGIN $tree:$suite $started==="
    echo "cwd=$cwd"
    cd "$cwd" || exit 97
    export PYTHONPATH="src:."
    export RTDL_OPTIX_LIBRARY="$cwd/build/librtdl_optix.so"
    export RTDL_EMBREE_LIBRARY="$cwd/build/librtdl_embree.so"
    git rev-parse HEAD 2>/dev/null || true
    git describe --tags --always 2>/dev/null || true
    echo "CMD: $*"
    "$@"
    rc=$?
    ended=$(date -Is)
    echo "===END $tree:$suite rc=$rc $ended==="
    printf "%s\t%s\t%s\t%s\t%s\n" "$tree" "$suite" "$rc" "$started" "$ended" >> "$status"
    exit $rc
  } >> "$log" 2>&1
  return $?
}
for tree in v2_14 current; do
  mkdir -p "$run_dir/${tree}_goal2626_standard" "$run_dir/${tree}_goal2636_standard" "$run_dir/${tree}_goal3828_full"
  run_cmd "$tree" goal2626_standard python3 scripts/goal2626_benchmark_embree_optix_baseline.py --scale standard --artifact-dir "$run_dir/${tree}_goal2626_standard" --case-repeat 1 --timeout-sec 1200
  run_cmd "$tree" goal2636_standard python3 scripts/goal2636_strengthen_benchmark_rows.py --tier standard --artifact-dir "$run_dir/${tree}_goal2636_standard" --case-repeat 1 --timeout-sec 1800
  run_cmd "$tree" goal3828_full python3 scripts/goal3828_current_benchmark_scale_profile_runner.py --output-json "$run_dir/${tree}_goal3828_full.json" --output-dir "$run_dir/${tree}_goal3828_full" --heartbeat-sec 20 --timeout-scale 2
 done
{
  echo "===PAIRED_V2_14_V3_END $(date -Is)==="
  echo "status.tsv:"
  cat "$status"
} >> "$log" 2>&1

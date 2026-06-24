#!/usr/bin/env bash
set +e
base=/root/rtdl_v3_rebuild_20260620
run_dir=/root/rtdl_v3_rebuild_20260620/artifacts/v2_14_vs_v3_same_rt_hardware_paired_20260620_140120
log="$run_dir/main.log"
status="$run_dir/status.tsv"
export PATH="$base/.venv/bin:$PATH"
export NUMBA_CUDA_PREFIX="$base/.venv/lib/python3.12/site-packages/nvidia/cuda_nvcc"
export CUDA_HOME="$NUMBA_CUDA_PREFIX"
export CUDA_PATH="$NUMBA_CUDA_PREFIX"
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
{
  echo "===PAIRED_CONTINUE_START $(date -Is)==="
} >> "$log" 2>&1
mkdir -p "$run_dir/v2_14_goal2636_standard" "$run_dir/v2_14_goal3828_full" "$run_dir/current_goal2626_standard" "$run_dir/current_goal2636_standard" "$run_dir/current_goal3828_full"
run_cmd v2_14 goal2636_standard python3 scripts/goal2636_strengthen_benchmark_rows.py --tier standard --artifact-dir "$run_dir/v2_14_goal2636_standard" --case-repeat 1 --timeout-sec 1800
run_cmd v2_14 goal3828_full python3 scripts/goal3828_current_benchmark_scale_profile_runner.py --output-json "$run_dir/v2_14_goal3828_full.json" --output-dir "$run_dir/v2_14_goal3828_full" --heartbeat-sec 20 --timeout-scale 2
run_cmd current goal2626_standard python3 scripts/goal2626_benchmark_embree_optix_baseline.py --scale standard --artifact-dir "$run_dir/current_goal2626_standard" --case-repeat 1 --timeout-sec 1200
run_cmd current goal2636_standard python3 scripts/goal2636_strengthen_benchmark_rows.py --tier standard --artifact-dir "$run_dir/current_goal2636_standard" --case-repeat 1 --timeout-sec 1800
run_cmd current goal3828_full python3 scripts/goal3828_current_benchmark_scale_profile_runner.py --output-json "$run_dir/current_goal3828_full.json" --output-dir "$run_dir/current_goal3828_full" --heartbeat-sec 20 --timeout-scale 2
{
  echo "===PAIRED_V2_14_V3_END $(date -Is)==="
  echo "status.tsv:"
  cat "$status"
} >> "$log" 2>&1

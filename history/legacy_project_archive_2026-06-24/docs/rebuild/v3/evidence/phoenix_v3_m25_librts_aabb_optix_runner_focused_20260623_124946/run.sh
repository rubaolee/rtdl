set -eu
BASE=/root/rtdl_v3_rebuild_20260620
ART="$1"
PY=$BASE/.venv/bin/python
APP=examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py
log(){ printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" | tee -a "$ART/progress.log"; }
run_case(){
  tree="$1"; backend="$2"; label="$3"; boxes="$4"; queries="$5"; repeat="$6"; warmup="$7"; skip="$8"
  mode=${backend}_aabb_index
  out="$ART/${tree}_${backend}_${label}.json"
  err="$ART/${tree}_${backend}_${label}.stderr.txt"
  log "START tree=$tree backend=$backend label=$label boxes=$boxes queries=$queries repeat=$repeat warmup=$warmup skip=$skip"
  cd "$BASE/$tree"
  export PYTHONPATH=src:.
  export RTDL_OPTIX_LIBRARY="$PWD/build/librtdl_optix.so"
  args=("$APP" --mode "$mode" --dataset uniform --operation all --box-count "$boxes" --query-count "$queries" --seed 2025 --repeat "$repeat" --warmup "$warmup")
  if [ "$skip" = yes ]; then args+=(--skip-counts); fi
  "$PY" "${args[@]}" > "$out" 2> "$err"
  log "DONE tree=$tree backend=$backend label=$label"
}
{
  echo "artifact=$ART"
  nvidia-smi --query-gpu=name,driver_version --format=csv,noheader
  echo "current_sha256_prepared_execution=$(sha256sum $BASE/current/src/rtdsl/prepared_execution.py | awk '{print $1}')"
  echo "current_sha256_librts_app=$(sha256sum $BASE/current/examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py | awk '{print $1}')"
  echo "v2_14_sha256_librts_app=$(sha256sum $BASE/v2_14/examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py | awk '{print $1}')"
} > "$ART/environment.txt"
log "ARTIFACT $ART"
for tree in v2_14 current; do
  for backend in embree optix; do
    run_case "$tree" "$backend" m22_exact_2048x1024_r1w0 2048 1024 1 0 no
    run_case "$tree" "$backend" repeat50_2048x1024_r50w5 2048 1024 50 5 no
    run_case "$tree" "$backend" stress_32768x1024_r20w5 32768 1024 20 5 yes
  done
done
log "ALL_DONE"

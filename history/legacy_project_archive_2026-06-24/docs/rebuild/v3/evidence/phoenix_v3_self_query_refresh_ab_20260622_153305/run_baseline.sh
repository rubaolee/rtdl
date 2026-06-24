#!/usr/bin/env bash
set -u
cd /root/rtdl_v3_rebuild_20260620/current
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=/root/rtdl_v3_rebuild_20260620/current/build/librtdl_optix.so
export RTDL_EMBREE_LIBRARY=/root/rtdl_v3_rebuild_20260620/current/build/librtdl_embree.so
out="$1"
{
  date -u +%FT%TZ
  nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader || true
  sha256sum src/rtdsl/partner_adapters.py src/rtdsl/optix_runtime.py src/rtdsl/embree_runtime.py || true
} > "$out/environment.txt" 2>&1
: > "$out/status.tsv"
run_case() {
  name="$1"; shift
  echo "START	$name	$(date -u +%FT%TZ)" >> "$out/status.tsv"
  timeout 900s python3 examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py "$@" > "$out/${name}.json" 2> "$out/${name}.stderr"
  rc=$?
  echo "END	$name	$(date -u +%FT%TZ)	$rc" >> "$out/status.tsv"
  return 0
}
run_case blocked_cupy_16384 --mode optix_rt_core_grouped_stream_blocked_cupy_column_signature_3d --dataset clustered3d --point-count 16384 --partner cupy --grouped-union-query-block-size 4096 --warmup 1 --repeat 4 --no-validation
run_case blocked_cupy_65536 --mode optix_rt_core_grouped_stream_blocked_cupy_column_signature_3d --dataset clustered3d --point-count 65536 --partner cupy --grouped-union-query-block-size 4096 --warmup 1 --repeat 4 --no-validation
run_case unblocked_cupy_16384 --mode optix_rt_core_grouped_stream_cupy_column_signature_3d --dataset clustered3d --point-count 16384 --partner cupy --warmup 1 --repeat 4 --no-validation
run_case blocked_numba_16384 --mode optix_rt_core_grouped_stream_blocked_numba_column_signature_3d --dataset clustered3d --point-count 16384 --partner numba --grouped-union-query-block-size 4096 --warmup 1 --repeat 4 --no-validation
sha256sum "$out"/* > "$out/sha256sums.txt" 2>/dev/null || true
date -u +%FT%TZ > "$out/DONE"

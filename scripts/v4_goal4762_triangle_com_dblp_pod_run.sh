#!/usr/bin/env bash
set -u

OUT="${OUT:-/root/v4_goal4762_triangle_com_dblp_paper_20260626}"
DATA="${DATA:-/root/rtgraph_paper_datasets/com-dblp/com-dblp.ungraph.rtdl_i32.edgebin}"
PY="${PY:-/root/rtdl_v4_venv/bin/python}"
CUDA="${CUDA:-/root/rtdl_v4_venv/lib/python3.12/site-packages/nvidia/cuda_nvcc}"
WARMUP="${WARMUP:-1}"
REPEAT="${REPEAT:-3}"

mkdir -p "$OUT/raw"
cp /root/rtdl_v4_candidate_pod/build/librtdl_optix.so /root/rtdl_v2_14_tag/build/librtdl_optix.v4compat.so
cp /root/rtdl_v4_candidate_pod/build/librtdl_optix.so /root/rtdl_v3_0_2_tag/build/librtdl_optix.v4compat.so

run_one() {
  local label="$1"
  local root="$2"
  local mode="$3"
  local optix="$4"
  shift 4

  echo "[triangle-com-dblp] BEGIN ${label} $(date -Is)" | tee -a "$OUT/run.log"
  (
    cd "$root" &&
    export PYTHONPATH="$root/src:$root" &&
    export CUDA_HOME="$CUDA" CUDA_PATH="$CUDA" NUMBA_CUDA_PREFIX="$CUDA" &&
    export NUMBA_CUDA_NVVM="$CUDA/nvvm/lib64/libnvvm.so" &&
    export LD_LIBRARY_PATH="$CUDA/nvvm/lib64:${LD_LIBRARY_PATH:-}" &&
    export RTDL_OPTIX_LIBRARY="$optix" RTDL_OPTIX_LIB="$optix" &&
    timeout 2400 "$PY" examples/benchmark_apps/triangle_counting/rtdl_triangle_counting_benchmark_app.py \
      --mode "$mode" \
      --edge-file "$DATA" \
      --edge-format binary \
      --backend optix \
      --detail summary \
      --partner cupy \
      --warmup "$WARMUP" \
      --repeat "$REPEAT" \
      "$@"
  ) > "$OUT/raw/${label}.json" 2> "$OUT/raw/${label}.stderr.txt"
  local rc=$?
  echo "[triangle-com-dblp] END ${label} rc=${rc} $(date -Is)" | tee -a "$OUT/run.log"
  return "$rc"
}

run_one v4_0 /root/rtdl_v4_candidate_pod rt_graph_2a1_segmented_generic_rt \
  /root/rtdl_v4_candidate_pod/build/librtdl_optix.so \
  --segment-ray-representation unique_weighted \
  --segment-query-schedule prepared_segment_replay

run_one v3_0_2 /root/rtdl_v3_0_2_tag rt_graph_2a1_segmented_generic_rt \
  /root/rtdl_v3_0_2_tag/build/librtdl_optix.v4compat.so \
  --segment-ray-representation unique_weighted \
  --segment-query-schedule prepared_segment_replay

run_one v2_14 /root/rtdl_v2_14_tag rt_graph_2a1_generic_rt \
  /root/rtdl_v2_14_tag/build/librtdl_optix.v4compat.so

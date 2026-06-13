# Goal4346: CPU-Only Pod Comparison Launch

Date: 2026-06-11

Status: CPU-only OptiX-vs-Embree launch packet; not release or public speedup authorization.

## Verdict

Proceed with NVIDIA RT-core OptiX versus Embree CPU only. No Intel-GPU lane is included.

Run OptiX on an RTX-class pod. Do not use Pascal/GTX hardware for RT-core timing.

## Preflight

`export PYTHONPATH=src:.`
`export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so`
`export RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so`
`export RTDL_EMBREE_LIBRARY=$PWD/build/librtdl_embree.so`
`export RTDL_CUDA_PREFIX=${RTDL_CUDA_PREFIX:-/usr/local/cuda-12.8}`
`export NUMBA_CUDA_PREFIX=${NUMBA_CUDA_PREFIX:-/usr/local/lib/python3.12/dist-packages/nvidia/cuda_nvcc}`
`export CUDA_HOME=$NUMBA_CUDA_PREFIX`
`export CUDA_PATH=$NUMBA_CUDA_PREFIX`
`export PATH=$RTDL_CUDA_PREFIX/bin:$NUMBA_CUDA_PREFIX/bin:$PATH`
`export LD_LIBRARY_PATH=$NUMBA_CUDA_PREFIX/nvvm/lib64:$RTDL_CUDA_PREFIX/targets/x86_64-linux/lib:$RTDL_CUDA_PREFIX/lib64:${LD_LIBRARY_PATH:-}`
`export OMP_NUM_THREADS=${OMP_NUM_THREADS:-8}`
`export TBB_NUM_THREADS=${TBB_NUM_THREADS:-8}`
`export MKL_NUM_THREADS=${MKL_NUM_THREADS:-8}`
`export OPENBLAS_NUM_THREADS=${OPENBLAS_NUM_THREADS:-8}`
`export NUMEXPR_NUM_THREADS=${NUMEXPR_NUM_THREADS:-8}`
`export RTDL_EMBREE_THREADS=${RTDL_EMBREE_THREADS:-8}`

## OptiX Pod Command

`python scripts/goal3828_current_benchmark_scale_profile_runner.py --output-json docs/reports/goal4346_cpu_only_pod_comparison_run/optix_scale_summary.json --output-dir docs/reports/goal4346_cpu_only_pod_comparison_run/optix_scale_outputs --materialize-rayjoin-public-cdb`

## Embree CPU Commands

| App | Bucket | Output | Command |
| --- | --- | --- | --- |
| hausdorff_xhd | `clean_internal_query_ratio` | `docs/reports/goal4346_cpu_only_pod_comparison_run/embree_scale_outputs/hausdorff_xhd.json` | `python examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py --backend embree --optix-summary-mode directed_threshold_prepared --hausdorff-threshold 0.25 --copies 1024 --repeat 5 --warmup 1` |
| robot_collision | `boundary_limited_phase_ratio` | `docs/reports/goal4346_cpu_only_pod_comparison_run/embree_scale_outputs/robot_collision.json` | `python examples/current/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py --mode embree_prepared_buffers --dataset scaled --pose-count 1024 --obstacle-count 128 --link-count 4 --repeats 50000 --warmup 100 --no-probe-reference --summary-only-runs` |
| contact_manifold | `clean_internal_query_ratio` | `docs/reports/goal4346_cpu_only_pod_comparison_run/embree_scale_outputs/contact_manifold.json` | `python examples/current/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py --mode native_collect_k --backend embree --dataset grid --grid-count 64 --witness-capacity 128 --repeat-count 3` |
| raydb_style | `boundary_limited_phase_ratio` | `docs/reports/goal4346_cpu_only_pod_comparison_run/embree_scale_outputs/raydb_style.json` | `python examples/current/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py --mode count --backend paper_rt_embree --fixture-kind generated --generated-rows 262144 --generated-groups 1024 --repeat 5000 --warmup 50 --summary-only-iterations` |
| librts_spatial_index | `fully_optimized_measured_pair` | `docs/reports/goal4346_cpu_only_pod_comparison_run/embree_scale_outputs/librts_spatial_index.json` | `python examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py --mode embree_aabb_index --dataset uniform --box-count 1024 --query-count 1024 --operation all --repeat 2 --warmup 1 --skip-counts` |
| triangle_counting | `clean_internal_query_ratio` | `docs/reports/goal4346_cpu_only_pod_comparison_run/embree_scale_outputs/triangle_counting.json` | `python examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py --mode rt_graph_2a1_generic_rt --backend embree --fixture degree_oriented_two_triangles --rt-graph-copies 2048 --detail summary --repeat 3 --warmup 1` |

## Contract-Choice Blockers

| App | Reason | Next Action |
| --- | --- | --- |

## Current Comparison Shape

- `fully_optimized_measured_pair_count`: 1
- `fresh_scale_comparison_row_count`: 5
- `clean_internal_query_ratio_count`: 8
- `boundary_limited_phase_ratio_count`: 2
- `contract_choice_blocker_count`: 0

## Postprocess

`python scripts/rtdl_optimized_optix_embree_comparison_packet.py --output-json docs/reports/goal4346_cpu_only_pod_comparison_run/comparison_packet.json --output-markdown docs/reports/goal4346_cpu_only_pod_comparison_run/comparison_packet.md`
`python scripts/rtdl_backend_comparison_campaign_closeout.py --output-json docs/reports/goal4346_cpu_only_pod_comparison_run/closeout.json --output-markdown docs/reports/goal4346_cpu_only_pod_comparison_run/closeout.md`

## Boundary

Goal4346 is a CPU-only OptiX-vs-Embree launch packet. It targets NVIDIA RT-core OptiX rows versus Embree CPU rows only. It has no Intel-GPU lane and does not authorize release action, public speedup wording, whole-app acceleration wording, broad RT-core wording, paper reproduction wording, true-zero-copy wording, automatic partner selection, or app-specific native-engine logic.

Validation status: `accept`.

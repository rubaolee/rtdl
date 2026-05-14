# Goal2006 Prepared CuPy Exact Filter Reuse

Date: 2026-05-14

Status: pod-pass-with-boundary

## Summary

Goal2006 closes the correctness gap found in the Goal1889 prepared road-hazard
reuse row. The native OptiX engine still emits only
`generic_ray_primitive_candidate_witness_pairs`; the Python partner layer now
keeps the caller-owned triangle columns attached to the reusable prepared scene
so the CuPy RawKernel exact segment/triangle filter can run before partner-side
unique-pair counting.

This preserves the v1.8/v2.0 boundary:

- RTDL native remains app-agnostic and candidate-only;
- exact road/hazard semantics live in the Python+CuPy partner layer;
- the prepared scene and witness buffers are reused across repeated queries;
- v2.0 release remains blocked until the wider release audit and final
  consensus gate authorize it.

## What Changed

- `prepare_segment_polygon_anyhit_optix_partner_device_scene(...)` now returns a
  small partner wrapper around the native prepared scene. The wrapper delegates
  native calls while retaining `polygon_triangle_columns` and
  `polygon_triangle_aabbs` for partner exact filtering.
- `_segment_polygon_all_witness_columns_optix_partner_columns(...)` now counts
  triangles from the wrapper's retained triangle columns, avoiding the false
  empty-scene path.
- `segment_polygon_hitcount_optix_prepared_partner_device_count_columns(...)`
  uses `_cupy_exact_segment_triangle_witness_pairs(...)` for prepared CuPy
  scenes, then counts exact unique segment/triangle pairs on the partner GPU.
- Road-hazard perf scripts now build ray columns as `float32`, matching the
  native OptiX all-witness device-column ABI after Goal2000.

## Pod Evidence

Host: `69.30.85.251:22085`

GPU: `NVIDIA RTX A5000, 570.211.01`

Workspace: `/root/rtdl_goal2000`

Artifact:

- `docs/reports/goal2006_pod_smoke/road_hazard_prepared_cupy_exact_filter_2048.json`

Command shape:

```bash
timeout 900 env \
  PYTHONPATH=src:. \
  RTDL_OPTIX_LIBRARY=/root/rtdl_goal2000/build/librtdl_optix.so \
  CUDA_PATH=/usr/local/cuda-12.8 \
  CUDA_HOME=/usr/local/cuda-12.8 \
  LD_LIBRARY_PATH=/usr/local/cuda-12.8/lib64 \
  CUPY_CACHE_DIR=/tmp/cupy-cache-rtdl \
  RTDL_SOURCE_COMMIT_LABEL=cbbffaa9-plus-goal2006-prepared-cupy-exact \
  python3 scripts/goal1869_road_hazard_v2_partner_perf.py \
    --count 2048 \
    --threshold 2 \
    --iterations 5 \
    --partners cupy \
    --output docs/reports/goal2006_pod_smoke/road_hazard_prepared_cupy_exact_filter_2048.json
```

The run printed progress for each timing iteration and completed with strict
priority-flag parity.

## Timing Result

| Row | Median seconds | Ratio vs v1.8 prepared |
| --- | ---: | ---: |
| v1.8 one-shot native OptiX road-hazard rows | 16.327098407 | 4699.62x slower |
| v1.8 prepared native OptiX road-hazard rows | 0.003474137 | 1.000x |
| v2.0 unprepared CuPy priority columns | 0.003750768 | 1.080x |
| Goal2006 prepared CuPy exact-filter priority columns | 0.003149398 | 0.907x |

The prepared CuPy path is therefore about `1.10x` faster than the v1.8 prepared
native row baseline and about `1.19x` faster than the unprepared v2.0 CuPy row
for the same `count=2048` synthetic road-hazard contract.

The artifact also records the exact prepared-path metadata:

- `native_engine_row_contract: generic_ray_primitive_candidate_witness_pairs`
- `app_exact_filter: cupy_rawkernel_segment_triangle_filter_from_generic_witness_candidates`
- `app_count_materialization: partner_gpu_unique_pair_counts_from_prepared_cupy_exact_filter`
- `whole_app_true_zero_copy_authorized: true`

## Boundary

This is a narrow same-contract road-hazard prepared CuPy timing row. It
authorizes saying that this path can keep exact app filtering and counting on
the partner GPU while reusing native prepared RT state.

It does not authorize:

- v2.0 release readiness;
- broad RT-core speedup wording;
- whole-app speedup wording outside this measured row;
- package-install claims;
- treating native candidate witness rows as exact app rows.

## Follow-Up Debt

The prepared CuPy exact filter still sorts segment and triangle IDs inside each
query. That is correct, but the triangle-side sort is reusable for a prepared
scene and should be cached in a later optimization pass if this row becomes a
headline v2.0 performance path.

Update: Goal2009 implements the triangle-side lookup cache in the Python partner
wrapper and records a faster pod timing row.

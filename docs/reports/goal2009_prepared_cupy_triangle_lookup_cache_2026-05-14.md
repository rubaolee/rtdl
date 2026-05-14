# Goal2009 Prepared CuPy Triangle Lookup Cache

Date: 2026-05-14

Status: pod-pass-with-boundary

## Summary

Goal2009 resolves the main non-blocking performance debt identified during the
Goal2006 Claude review: the prepared CuPy exact filter was rebuilding the
triangle-ID lookup on every query even though the prepared triangle scene is
fixed across repeated calls.

The prepared Python wrapper now owns a small CuPy triangle lookup cache. The
native OptiX scene remains unchanged and app-agnostic; the cache lives entirely
in the Python partner layer and is used only to map generic candidate primitive
IDs back to triangle-column positions before the CuPy exact filter runs.

## Pod Evidence

Host: `69.30.85.251:22085`

GPU: `NVIDIA RTX A5000, 570.211.01`

Artifact:

- `docs/reports/goal2009_pod_smoke/road_hazard_prepared_cupy_cached_triangle_lookup_2048.json`
- `docs/reports/goal2009_pod_smoke/road_hazard_prepared_cupy_cached_triangle_lookup_4096.json`

Command shape:

```bash
timeout 900 env \
  PYTHONPATH=src:. \
  RTDL_OPTIX_LIBRARY=/root/rtdl_goal2000/build/librtdl_optix.so \
  CUDA_PATH=/usr/local/cuda-12.8 \
  CUDA_HOME=/usr/local/cuda-12.8 \
  LD_LIBRARY_PATH=/usr/local/cuda-12.8/lib64 \
  CUPY_CACHE_DIR=/tmp/cupy-cache-rtdl \
  RTDL_SOURCE_COMMIT_LABEL=f8697ee2-plus-goal2009-cached-triangle-lookup \
  python3 scripts/goal1869_road_hazard_v2_partner_perf.py \
    --count 2048 \
    --threshold 2 \
    --iterations 5 \
    --partners cupy \
    --output docs/reports/goal2009_pod_smoke/road_hazard_prepared_cupy_cached_triangle_lookup_2048.json
```

## Timing Result

| Row | Median seconds | Ratio vs v1.8 prepared |
| --- | ---: | ---: |
| v1.8 one-shot native OptiX road-hazard rows | 16.492227267 | 4741.70x slower |
| v1.8 prepared native OptiX road-hazard rows | 0.003478130 | 1.000x |
| v2.0 unprepared CuPy priority columns | 0.003188476 | 0.917x |
| Goal2009 prepared CuPy cached exact-filter priority columns | 0.002519239 | 0.724x |

The prepared cached path is therefore about `1.38x` faster than the v1.8
prepared native row baseline and about `1.27x` faster than the unprepared v2.0
CuPy row for the same count-2048 road-hazard contract. Strict priority-flag
parity passed.

The larger count-4096 follow-up strengthens the scaling picture:

| Row | Median seconds | Ratio vs v1.8 prepared |
| --- | ---: | ---: |
| v1.8 one-shot native OptiX road-hazard rows | 104.259560453 | 10757.88x slower |
| v1.8 prepared native OptiX road-hazard rows | 0.009691451 | 1.000x |
| v2.0 unprepared CuPy priority columns | 0.005996620 | 0.619x |
| Goal2009 prepared CuPy cached exact-filter priority columns | 0.003932310 | 0.406x |

At count 4096, the prepared cached path is about `2.46x` faster than the v1.8
prepared native row baseline and about `1.52x` faster than unprepared v2.0 CuPy,
with strict priority-flag parity.

The artifact records:

- `native_engine_row_contract: generic_ray_primitive_candidate_witness_pairs`
- `app_exact_filter: cupy_rawkernel_segment_triangle_filter_from_generic_witness_candidates`
- `app_count_materialization: partner_gpu_unique_pair_counts_from_prepared_cupy_exact_filter`
- `whole_app_true_zero_copy_authorized: true`

## Boundary

This is still a narrow same-contract road-hazard prepared CuPy timing row. It
does not authorize v2.0 release readiness, broad RT-core speedup wording,
package-install claims, or general whole-app speedup claims.

## External Review

Claude reviewed Goal2009 in
`docs/reviews/goal2010_claude_review_goal2009_prepared_cupy_triangle_lookup_cache_2026-05-14.md`
with verdict `accept`.

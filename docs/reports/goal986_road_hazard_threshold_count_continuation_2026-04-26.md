# Goal986 Road-Hazard Threshold-Count Continuation

Date: 2026-04-26

Goal986 reduces road-hazard prepared OptiX summary overhead by adding a native `count_at_least` continuation to the prepared segment/polygon hit-count API. It does not authorize public RTX speedup claims.

## Motivation

Goal978 rejected the current `road_hazard_screening / road_hazard_native_summary_gate` public speedup claim because the RTX phase was much slower than the fastest same-semantics non-OptiX baseline.

The compact road-hazard summary only needs the number of road segments whose hazard hit count is at least the priority threshold. Returning one row per road segment and scanning those rows in Python is unnecessary for that summary path.

## Change

Native OptiX ABI:

- Added `rtdl_optix_count_prepared_segment_polygon_hitcount_at_least_2d(...)`.
- The function reuses the prepared polygon BVH and the existing custom-AABB OptiX traversal pipeline.
- It returns only a scalar count of segments whose native hit count is at least the caller-provided threshold.

Python runtime:

- Added `PreparedOptixSegmentPolygonHitcount2D.count_at_least(segments, threshold=...)`.
- Empty polygon scenes return `segment_count` only for threshold `0`, otherwise `0`.
- Closed handles and invalid thresholds are rejected.

Road-hazard profiler:

- `scripts/goal933_prepared_segment_polygon_optix_profiler.py` now uses `prepared.count_at_least(roads, threshold=2)` for `road_hazard_prepared_summary`.
- The profiler no longer calls `prepared.run(roads)` or materializes per-road hit-count rows for the warm query samples.
- Strict validation compares the scalar priority count against the CPU reference priority count.

## Boundary

This is a native continuation and interface-overhead reduction for one compact summary path. The current implementation still downloads per-segment native records internally before reducing them on the host side inside the native library. A future optimization can move the threshold reduction fully onto the GPU.

This goal does not claim:

- full road-hazard app speedup,
- GIS/routing acceleration,
- public RTX speedup authorization,
- or row-returning segment/polygon acceleration.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal933_prepared_segment_polygon_optix_test \
  tests.goal933_prepared_segment_polygon_profiler_test
```

Result:

```text
Ran 15 tests in 0.016s
OK
```

Additional checks:

```text
python3 -m py_compile src/rtdsl/optix_runtime.py scripts/goal933_prepared_segment_polygon_optix_profiler.py
git diff --check
```

Both passed.

## Next Cloud Action

On the next RTX pod, rerun:

```text
python3 scripts/goal933_prepared_segment_polygon_optix_profiler.py \
  --scenario road_hazard_prepared_summary \
  --copies 20000 \
  --iterations 5 \
  --mode run \
  --output-json docs/reports/goal933_road_hazard_prepared_summary_rtx.json
```

If this remains slower than Embree, the next likely target is an actual device-side threshold reduction instead of the current native-host reduction after GPU row download.

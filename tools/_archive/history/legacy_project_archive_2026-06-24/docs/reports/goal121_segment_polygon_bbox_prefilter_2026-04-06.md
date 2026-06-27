# Goal 121 Report: Segment-Polygon BBox Prefilter Attempt

Date: 2026-04-06
Status: accepted

## Summary

Goal 121 added a cheap axis-aligned bounding-box prefilter to the exact
`segment_polygon_hitcount` paths in the Python reference, native CPU oracle,
Embree, and Vulkan implementations.

The intent was simple:

- skip exact `segment_hits_polygon` work when the segment bbox and polygon bbox
  are disjoint

This is a correctness-preserving candidate-reduction change. It does not alter
the accepted semantics.

## Code touched

- [reference.py](/Users/rl2025/rtdl_python_only/src/rtdsl/reference.py)
- [rtdl_oracle.cpp](/Users/rl2025/rtdl_python_only/src/native/rtdl_oracle.cpp)
- [rtdl_embree.cpp](/Users/rl2025/rtdl_python_only/src/native/rtdl_embree.cpp)
- [rtdl_vulkan.cpp](/Users/rl2025/rtdl_python_only/src/native/rtdl_vulkan.cpp)

Linux artifact copies:

- [summary.json](/Users/rl2025/rtdl_python_only/docs/reports/goal121_segment_polygon_bbox_prefilter_artifacts_2026-04-06/summary.json)
- [summary.md](/Users/rl2025/rtdl_python_only/docs/reports/goal121_segment_polygon_bbox_prefilter_artifacts_2026-04-06/summary.md)

## Correctness result

Local focused regression:

- `PYTHONPATH=src:. python3 -m unittest tests.goal110_segment_polygon_hitcount_closure_test tests.goal114_segment_polygon_postgis_test tests.goal116_segment_polygon_backend_audit_test tests.goal118_segment_polygon_linux_large_perf_test`
- result:
  - `12` tests
  - `OK`
  - `5` skipped on the local Mac because the existing `geos_c` native-library
    dependency is absent there

Clean Linux host:

- `PYTHONPATH=src:. python3 -m unittest tests.goal110_segment_polygon_hitcount_closure_test tests.goal114_segment_polygon_postgis_test tests.goal116_segment_polygon_backend_audit_test tests.goal118_segment_polygon_linux_large_perf_test`
- result:
  - `12` tests
  - `OK`

Large deterministic PostGIS parity remained clean on Linux for:

- `x64`
- `x256`
- `x512`
- `x1024`

## Why this looked promising

The accepted tiled family is sparse at the bbox level.

Examples measured before implementation:

- `x64`
  - total segment/polygon pairs: `81920`
  - bbox-overlap candidates: `704`
  - candidate ratio: about `0.86%`
- `x256`
  - total pairs: `1310720`
  - the same tiling structure implies similarly sparse bbox selectivity

So the prefilter looked like a reasonable low-risk attempt.

## Performance result on Linux

### Current-run means after Goal 121

- `x64`
  - CPU: `0.037097 s`
  - Embree: `0.036325 s`
  - OptiX: `0.024354 s`
  - Vulkan: `0.037412 s`
- `x256`
  - CPU: `0.570643 s`
  - Embree: `0.570537 s`
  - OptiX: `0.378245 s`
  - Vulkan: `0.607216 s`
- `x1024`
  - PostGIS: `0.315025 s`
  - CPU: `9.040836 s`
  - Embree: `9.114836 s`
  - OptiX: `5.999233 s`
  - Vulkan: `9.044485 s`

### Before vs after comparison

Compared with Goal 118:

- `x64`
  - CPU improved from `0.047770 s` to `0.037097 s`
  - Embree improved from `0.047068 s` to `0.036325 s`
  - Vulkan was effectively flat around `0.037 s`
  - OptiX was effectively flat
- `x256`
  - CPU remained about `0.57 s`
  - Embree remained about `0.57 s`
  - OptiX remained about `0.38 s`
  - Vulkan remained near the same correctness-first range
- `x1024`
  - the large-row story did not materially change

## Interpretation

The prefilter is real and useful, but it is not the decisive missing fix.

What it achieved:

- removed obviously impossible exact checks
- improved the smaller audited row
- preserved correctness cleanly

What it did not achieve:

- a meaningful shift on the main large deterministic performance rows
- competitiveness with PostGIS
- a strong new advantage for OptiX, Embree, or Vulkan

The most likely reason is:

- the remaining exact refine and aggregation work still dominates once the case
  becomes large

So Goal 121 improves the implementation, but it does not change the basic
performance conclusion from Goals 118 through 120:

- `segment_polygon_hitcount` is a strong correctness/product feature
- but it is still not a performance flagship

## Final conclusion

Goal 121 closes successfully as a bounded algorithmic improvement:

- the code is better
- correctness stayed clean
- the small sparse row improved

But the large-row bottleneck remains. Further progress would need a stronger
candidate-generation and aggregation redesign rather than another small local
prefilter alone.

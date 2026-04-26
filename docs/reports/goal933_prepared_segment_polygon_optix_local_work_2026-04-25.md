# Goal933 Prepared Segment/Polygon OptiX Local Work

Date: 2026-04-25

## Purpose

Goal933 addresses the road-hazard and segment/polygon OptiX bottleneck found in
Goal929: strict RTX correctness passed, but the native one-shot path was not a
usable speedup claim because every call mixed polygon upload, OptiX custom-AABB
BVH build, traversal, copyback, and Python postprocessing.

This goal does not promote either app.  It adds the local mechanism and replay
contract needed for the next RTX run to measure the right thing: prepared scene
setup once, then repeated warm segment-batch traversal.

## Code Changes

- Added native C ABI:
  - `rtdl_optix_prepare_segment_polygon_hitcount_2d`
  - `rtdl_optix_run_prepared_segment_polygon_hitcount_2d`
  - `rtdl_optix_destroy_prepared_segment_polygon_hitcount_2d`
- Added `PreparedSegmentPolygonHitcount2D` in the OptiX native workload layer.
  It uploads polygon references and vertices once, builds the OptiX custom-AABB
  BVH once, then accepts repeated segment batches.
- Added Python API:
  - `rt.prepare_optix_segment_polygon_hitcount_2d(polygons)`
  - `PreparedOptixSegmentPolygonHitcount2D.run(segments)`
- Added `scripts/goal933_prepared_segment_polygon_optix_profiler.py`.
  It supports:
  - `segment_polygon_hitcount_prepared`
  - `road_hazard_prepared_summary`
  - `--mode dry-run` for local oracle/shape checks without OptiX
  - `--mode run` for RTX cloud phase evidence
- Updated the RTX cloud manifest so road-hazard and segment hit-count deferred
  entries use the Goal933 prepared profiler instead of the older one-shot
  strict gates.
- Updated the Goal762 artifact analyzer to parse Goal933 artifacts and preserve
  prepare/query/postprocess/validation/close phase fields.

## Claim Boundary

This is a tuning mechanism and evidence-contract change only.

Allowed claim after this local goal:

- RTDL now has a prepared OptiX segment/polygon hit-count API for repeated
  segment batches against a fixed polygon set.
- The next cloud run can distinguish setup cost from warm RT traversal query
  cost for road-hazard and segment/polygon hit-count workloads.

Not allowed:

- No public RTX speedup claim for road hazard.
- No public RTX speedup claim for segment/polygon hit-count.
- No claim that the default public app path changed from conservative
  host-indexed behavior.
- No pair-row any-hit scalability claim.

## Verification

Passed:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal933_prepared_segment_polygon_optix_test \
  tests.goal933_prepared_segment_polygon_profiler_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal762_rtx_cloud_artifact_report_test \
  tests.goal824_pre_cloud_rtx_readiness_gate_test \
  tests.goal848_v1_rt_core_goal_series_test

Ran 40 tests in 0.985s
OK
```

Passed:

```text
python3 -m py_compile \
  scripts/goal933_prepared_segment_polygon_optix_profiler.py \
  scripts/goal759_rtx_cloud_benchmark_manifest.py \
  scripts/goal762_rtx_cloud_artifact_report.py \
  src/rtdsl/optix_runtime.py \
  src/rtdsl/__init__.py
```

Passed:

```text
git diff --check
```

Regenerated:

- `docs/reports/goal759_rtx_cloud_benchmark_manifest_2026-04-22.json`
- `docs/reports/goal824_pre_cloud_rtx_readiness_gate_2026-04-23.json`
- `docs/reports/goal848_v1_0_rt_core_goal_series_2026-04-23.json`
- `docs/reports/goal848_v1_0_rt_core_goal_series_2026-04-23.md`

## Next Step

Run the Goal933 profiler on a real RTX pod only after other local prep is
batched.  The important outputs for review are `optix_prepare_sec`,
`optix_query_sec.median_sec`, `python_postprocess_sec.median_sec`, and
`matches_oracle`.

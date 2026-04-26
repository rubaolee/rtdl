# Goal934 Prepared Segment/Polygon Pair-Row OptiX Local Work

Date: 2026-04-25

## Verdict

Local implementation and contract checks are complete. This is not a release
claim and not RTX performance evidence. It prepares the next consolidated RTX
pod run to measure `segment_polygon_anyhit_rows` with a prepared polygon BVH and
bounded pair-row output.

## Problem

Goal929 proved that the small native OptiX pair-row gate can match the CPU row
digest without overflow, but it did not measure a scalable prepared path. The old
cloud manifest still used `scripts/goal873_native_pair_row_optix_gate.py` on
`authored_segment_polygon_minimal`, which was useful for correctness but too
small and too one-shot for performance tuning.

## Changes

- Added native prepared pair-row OptiX ABI:
  `rtdl_optix_prepare_segment_polygon_anyhit_rows_2d`,
  `rtdl_optix_run_prepared_segment_polygon_anyhit_rows_2d`, and
  `rtdl_optix_destroy_prepared_segment_polygon_anyhit_rows_2d`.
- Added `PreparedSegmentPolygonAnyhitRows2D` in the native OptiX workload layer.
  It uploads polygon refs/vertices once, builds the polygon custom-AABB BVH once,
  then launches repeated bounded segment/polygon pair-row traversal batches.
- Added Python API:
  `rt.prepare_optix_segment_polygon_anyhit_rows_2d(polygons)` and
  `PreparedOptixSegmentPolygonAnyHitRows2D`.
- Added `run_with_metadata(...)` for bounded row output so artifacts can record
  `emitted_count`, `copied_count`, and `overflowed` without hiding capacity
  failures.
- Added `scripts/goal934_prepared_segment_polygon_pair_rows_optix_profiler.py`.
  It supports dry-run local validation and real RTX `--mode run`, emits separated
  input, CPU-reference, prepare, query, postprocess, validation, and close phases,
  and keeps explicit non-claim boundaries.
- Updated Goal759 manifest so deferred `segment_polygon_anyhit_rows` now uses the
  Goal934 prepared profiler at `copies=256`, `iterations=5`,
  `output_capacity=4096`.
- Updated Goal762 artifact analyzer to parse the new Goal934 schema.

## Verification

Focused local verification passed:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal933_prepared_segment_polygon_optix_test \
  tests.goal934_prepared_segment_polygon_pair_rows_profiler_test \
  tests.goal933_prepared_segment_polygon_profiler_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal762_rtx_cloud_artifact_report_test \
  tests.goal824_pre_cloud_rtx_readiness_gate_test \
  tests.goal848_v1_rt_core_goal_series_test

Ran 48 tests in 1.045s
OK

python3 -m py_compile \
  scripts/goal933_prepared_segment_polygon_optix_profiler.py \
  scripts/goal934_prepared_segment_polygon_pair_rows_optix_profiler.py \
  scripts/goal759_rtx_cloud_benchmark_manifest.py \
  scripts/goal762_rtx_cloud_artifact_report.py \
  src/rtdsl/optix_runtime.py \
  src/rtdsl/__init__.py

git diff --check
```

Generated contract artifacts were refreshed:

- `docs/reports/goal759_rtx_cloud_benchmark_manifest_2026-04-22.json`
- `docs/reports/goal824_pre_cloud_rtx_readiness_gate_2026-04-23.json`
- `docs/reports/goal848_v1_0_rt_core_goal_series_2026-04-23.json`
- `docs/reports/goal848_v1_0_rt_core_goal_series_2026-04-23.md`

## Boundaries

- No cloud pod was used for Goal934.
- No RTX speedup claim is authorized.
- No unbounded pair-row performance claim is authorized.
- `segment_polygon_anyhit_rows` remains `needs_native_kernel_tuning` until a
  real RTX artifact proves no overflow, CPU-reference parity, and accepted
  same-semantics baseline review.
- This change only improves the prepared native OptiX path. The public app's
  default/conservative path remains separate.

## Next Cloud Command

The next consolidated RTX pod run should include the manifest entry:

```text
PYTHONPATH=src:. python3 scripts/goal934_prepared_segment_polygon_pair_rows_optix_profiler.py \
  --copies 256 \
  --iterations 5 \
  --output-capacity 4096 \
  --mode run \
  --output-json docs/reports/goal934_segment_polygon_anyhit_rows_prepared_bounded_rtx.json
```

Run it only as part of a batched pod session, not as a single-app restart.

# Goal 117 v0.2 Feature Usage Surface

Date: 2026-04-06
Status: accepted

## Summary

Goal 117 improves how the first v0.2 feature line is presented to users.

The feature already had:

- workload-family closure
- backend audit
- PostGIS validation
- generate-only support

What it still lacked was a simple answer to:

- what does a real app using this feature look like?
- what is actually new in v0.2 compared with v0.1?

This goal adds those two missing user-facing pieces.

## New Example

New app-style example:

- [rtdl_road_hazard_screening.py](/Users/rl2025/rtdl_python_only/examples/rtdl_road_hazard_screening.py)

What it shows:

- roads as probe segments
- hazard polygons as build polygons
- one output row per road segment:
  - `segment_id`
  - `hit_count`
- one simple application rule:
  - roads with `hit_count >= 2` become `priority_segments`

This is intentionally not a broad GIS application. It is a clean screening
primitive that matches the actual workload semantics.

## New Status Note

New note:

- [v0_2_feature_status_2026-04-06.md](/Users/rl2025/rtdl_python_only/docs/reports/v0_2_feature_status_2026-04-06.md)

This note answers a narrow release-facing question:

- what is actually new in the current v0.2 line compared with the archived
  `v0.1.0` baseline?

It keeps the answer concrete:

- one new closed workload family
- one narrow kept generate-only feature
- stronger correctness and backend evidence

## Cookbook Update

The workload cookbook now points readers to the app-style example:

- [workload_cookbook.md](/Users/rl2025/rtdl_python_only/docs/rtdl/workload_cookbook.md)

That makes the feature surface easier to discover without searching through
goal reports.

## Validation

Validated locally:

- `python3 -m py_compile examples/rtdl_road_hazard_screening.py`
- `PYTHONPATH=src:. python3 examples/rtdl_road_hazard_screening.py --backend cpu_python_reference`

Observed output:

- `row_count: 3`
- `priority_segments: [1]`

## Conclusion

Goal 117 closes as a user-surface improvement.

It does not change backend claims, but it does make the first v0.2 feature line
much easier to explain:

- here is the workload
- here is a real app-style program
- here is what is genuinely new versus v0.1

# Handoff: Claude Review For Goal3495 Device Active Shape Ordinals

Please perform an independent read-only review of Goal3495.

## Files To Read

- `docs/reports/goal3495_overlay_area_device_active_shape_ordinals_2026-06-05.md`
- `docs/reports/goal3495_overlay_area_device_active_shape_ordinals_pod_2026-06-05.json`
- `tests/goal3495_overlay_area_device_active_shape_ordinals_test.py`
- `src/rtdsl/geometry_relation_continuations.py`
- `scripts/goal3492_overlay_area_public_cdb_tile_task_executor.py`
- `src/rtdsl/v2_8_benchmark_runtime_gap.py`

## Review Questions

1. Does Goal3495 keep the runtime/engine app-agnostic?
2. Is the new CuPy continuation genuinely generic over relation ordinals rather than RayJoin-specific?
3. Does the pod artifact support only the narrow claim made: device-side unique active-shape ordinal discovery, not device-resident tile-task planning or true zero-copy?
4. Are the negative timing findings framed honestly, especially that full relation ordinal download is tiny at this scale and the remaining bottleneck is payload construction/planning?
5. Are any release, public speedup, RT-core speedup, true-zero-copy, or full-overlay completion claims accidentally authorized?
6. What should the next engineering target be: device-resident component-pair/tile-task planning, native prepared-payload construction, or another smaller preparatory step?

## Required Output

Write the review to:

`docs/reviews/goal3496_claude_review_goal3495_device_active_shape_ordinals_2026-06-05.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.


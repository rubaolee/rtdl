# Handoff: Claude Review For Goals3497-3498 Overlay Filter And Device Planner

Please perform an independent read-only review of Goals3497 and 3498.

## Files To Read

- `docs/reports/goal3497_overlay_area_bounds_positive_filtered_tile_tasks_2026-06-05.md`
- `docs/reports/goal3497_overlay_area_bounds_positive_filtered_tile_tasks_pod_2026-06-05.json`
- `docs/reports/goal3498_overlay_area_device_tile_task_planner_2026-06-05.md`
- `docs/reports/goal3498_overlay_area_device_tile_task_planner_pod_2026-06-05.json`
- `tests/goal3497_overlay_area_bounds_positive_filtered_tile_tasks_test.py`
- `tests/goal3498_overlay_area_device_tile_task_planner_test.py`
- `src/rtdsl/v2_8_overlay_area_prepared_payload.py`
- `scripts/goal3492_overlay_area_public_cdb_tile_task_executor.py`
- `src/rtdsl/v2_8_benchmark_runtime_gap.py`

## Review Questions

1. Do Goals3497 and 3498 preserve the app-agnostic RTDL engine/runtime boundary?
2. Is Goal3497's bounds-positive filter a valid generic zero-area rejection rule?
3. Does Goal3498 correctly distinguish first-use CuPy/JIT cost from steady-state device-planning cost?
4. Are the pod numbers interpreted honestly, especially that Goal3498 is a steady-state planning win but not a payload-construction fix?
5. Do all claim boundaries remain false for release, public speedup, RT-core speedup, true zero-copy, and full-overlay completion?
6. Is the next recommended target component-level bounds filtering, native prepared-payload construction, or something else?

## Required Output

Write the review to:

`docs/reviews/goal3500_claude_review_goal3497_3498_overlay_filter_planner_2026-06-05.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.


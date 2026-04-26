# Goal 712 Review: App Mode Identity And Embree Parity Cleanup

Date: 2026-04-21
Reviewer: Claude (claude-sonnet-4-6)
Verdict: **ACCEPT**

---

## Scope

This review covers:

- `examples/rtdl_segment_polygon_hitcount.py` (modified)
- `examples/rtdl_segment_polygon_anyhit_rows.py` (modified)
- `tests/goal712_app_mode_parity_test.py` (new)
- `docs/reports/goal712_app_mode_identity_parity_2026-04-21.md` (new)

---

## What Changed

Both diffs are single-line additions:

```python
# rtdl_segment_polygon_hitcount.py  run_case() return dict
+ "app": "segment_polygon_hitcount",

# rtdl_segment_polygon_anyhit_rows.py  run_case() payload dict
+ "app": "segment_polygon_anyhit_rows",
```

In both cases the field is placed unconditionally in the payload — it is not behind a backend branch, so it is emitted for all five backends (cpu_python_reference, cpu, embree, optix, vulkan). The string literals match the established naming convention used by `robot_collision_screening` (line 253 of that app).

---

## Test Coverage Assessment

### `test_segment_polygon_hitcount_identifies_app`

Directly asserts `payload["app"] == "segment_polygon_hitcount"` after a cpu_python_reference call. Because the `app` key is unconditional in the return literal, this single-backend check is sufficient to verify the field is wired correctly. No gap.

### `test_segment_polygon_anyhit_modes_match_embree`

Iterates all three output modes (`rows`, `segment_flags`, `segment_counts`), calls both cpu_python_reference and embree, and asserts:

1. `app` field present and correct on both.
2. `_canonical(cpu) == _canonical(embree)` for each mode.

The `_canonical` helper strips `backend`, `requested_backend`, `data_flow`, and `prepared_dataset` before comparison — exactly the keys expected to differ between backends. The remaining fields (`row_count`, `optix_performance`, `boundary`, and the mode-specific payload) should be identical. `optix_performance` is computed by `rt.optix_app_performance_support(app_name)` independently of backend, so it is safe to include in the equality check.

This closes the Gap 711 left open: Goal 711 tested only compact modes for anyhit; Goal 712 now also covers `rows` mode.

### `test_robot_collision_output_modes_match_embree`

Tests `full`, `pose_flags`, and `hit_count` modes for robot_collision_screening. The robot app was not modified in this goal; this is a new regression net around pre-existing code. The app already emits `"app": "robot_collision_screening"` unconditionally (lines 253, 271). Test is valid.

---

## Issues Found

**None blocking.**

One minor observation:

- `test_segment_polygon_hitcount_identifies_app` does not assert hitcount CPU-vs-Embree numerical parity. This is outside the stated scope of Goal 712 (which is identity and anyhit-mode parity), and hitcount parity was presumably gated in Goal 711. No action required — noting for the record.

---

## Boundary Compliance

The `boundary` string in both example payloads is pre-existing text (not introduced by this diff) and correctly notes that OptiX app exposure is classified separately from RT-core performance. Goal 712 does not make any new performance claim and does not expand engine support. The scope as stated in the report is accurate.

---

## Summary

The changes are minimal, surgical, and correct. The new `app` fields are unconditional, match the project naming convention, and are directly verified by the new test. The test suite closes a real coverage gap (anyhit `rows` mode against Embree) and adds a new regression net for the robot app. No regressions, no security issues, no scope creep.

**ACCEPT.**

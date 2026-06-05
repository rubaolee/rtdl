# Handoff: Gemini Review For Goals3417-3418

Please perform an independent read-only review of Goals3417 and 3418.

Goal3417 added a runtime page-plan object:

- `OptixExactDevicePairColumnPagePlan`
- `PreparedOptixPointClosedShapeMembership2D.exact_device_columns_page_plan(...)`
- `scripts/goal3417_runtime_page_plan_probe.py`
- `docs/reports/goal3417_runtime_pair_column_page_plan_2026-06-04.md`
- `docs/reports/goal3417_runtime_page_plan_probe_2026-06-04.json`
- `tests/goal3417_runtime_pair_column_page_plan_test.py`

Goal3418 added the first native page-plan handle:

- `RtdlNativePairColumnPagePlanInfo`
- `rtdl_optix_prepare_point_closed_shape_membership_exact_device_columns_page_plan_2d`
- `rtdl_optix_produce_point_closed_shape_membership_exact_device_columns_page_2d`
- `rtdl_optix_destroy_point_closed_shape_membership_exact_device_columns_page_plan_2d`
- `OptixExactDevicePairColumnNativePagePlan`
- `PreparedOptixPointClosedShapeMembership2D.exact_device_columns_native_page_plan(...)`
- `scripts/goal3418_native_page_plan_handle_probe.py`
- `docs/reports/goal3418_native_pair_column_page_plan_handle_2026-06-04.md`
- `docs/reports/goal3418_native_page_plan_handle_probe_2026-06-04.json`
- `tests/goal3418_native_pair_column_page_plan_handle_test.py`

Final pushed evidence head: `3ae0a4dd`.

Review questions:

1. Do Goals3417-3418 preserve the app-agnostic boundary?
2. Does Goal3417 correctly add a runtime page-plan object without claiming a
   native handle?
3. Does Goal3418 actually add a native page-plan handle, native produce-page
   function, and native destroy function?
4. Is the remaining boundary honest: the native plan owns a host point copy,
   exact predicates are still host-refined, and no true-zero-copy/device-only
   exact claim is authorized?
5. Are the artifacts internally consistent: 9 pages, 47,262 exact rows, 16,476
   final groups, 16,541 per-page grouped-row sum, and zero missing/extra/mismatch?
6. What is the next required engineering step toward the final native paged
   stream shape?

Suggested validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3418_native_pair_column_page_plan_handle_test `
  tests.goal3417_runtime_pair_column_page_plan_test `
  tests.goal3414_native_exact_page_producer_surface_test
```

Write the review to:

`docs/reviews/goal3419_gemini_review_goals3417_3418_native_page_plan_2026-06-04.md`

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, `reject`.

Do not edit source files. If you find problems, write them in the review.

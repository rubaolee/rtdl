# Goal1313 Claude Review Request: Native Jaccard Device-Level Plan

Please review the native Jaccard v1.5 plan in `/Users/rl2025/rtdl_python_only`.

Read:

- `docs/reports/goal1313_v1_5_native_jaccard_device_plan_2026-05-05.md`
- `docs/reports/goal1312_v1_5_jaccard_optix_slower_reason_2026-05-05.md`
- `docs/reports/goal1311_v1_5_jaccard_generic_fail_closed_collection_2026-05-05.md`
- `src/rtdsl/bounded_collection_contracts.py`
- `src/rtdsl/generic_polygon_primitives.py`
- `src/rtdsl/jaccard_performance_diagnostics.py`
- `src/rtdsl/v1_5_migration_inventory.py`

Judge whether:

1. The plan keeps `polygon_set_jaccard` diagnostic and avoids public speedup overclaim.
2. The proposed native ABI is generic enough and not an app-specific shortcut.
3. The fail-closed bounded collection and guarded reduction gates are sufficient.
4. The plan correctly keeps Vulkan, HIPRT, and Apple RT frozen before v2.1.
5. The next slice should prioritize OptiX native bounded collection.

Write your review to:

`docs/reports/goal1313_claude_review_2026-05-05.md`

Use sections Verdict, Findings, Risks, Required Fixes, Conclusion. Do not modify source code.

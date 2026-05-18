# Goal2326 Gemini Follow-up Post-Fix Review

**Date:** 2026-05-18

**Reviewer:** Gemini

**Verdict:** `accept-with-boundary`

## Context

This is a follow-up review of the fixes made after the initial Claude and Gemini
reviews of Goal2326, which returned `accept-with-boundary`. Claude's initial
review identified a blocker-grade leak related to
`allocate_robot_collision_pose_partner_device_output_columns` being re-exported.

## Fixes Verified

1.  `src/rtdsl/adapters/prepared_handles.py` no longer re-exports
    `allocate_robot_collision_pose_partner_device_output_columns`. This was confirmed by inspecting the `__all__` list in the file.
2.  `tests/goal2326_adapter_partition_test.py` now correctly scans adapter `__all__` symbols for app/domain fragments, including `robot` and `pose`, which are part of its `FORBIDDEN` list.
3.  `src/rtdsl/execution.py` reports `memory_status` and `copy_status` as
    `not_reported_by_runtime`. This was confirmed by direct inspection of the `_build_report` function.
4.  `tests/goal2326_execution_report_contract_test.py` covers the `not_reported_by_runtime` sentinel for `memory_status` and `copy_status`.
5.  `src/rtdsl/__init__.py` defines a curated `__dir__()` that exposes the contract-first surface for interactive users, as intended.
6.  `tests/goal2326_public_primitive_contract_test.py` validates that `dir(rtdsl)` exposes the contract-first surface and correctly filters app-shaped learner-facing names.

## Questions Addressed

1.  **Are Claude's blocker-grade items resolved?**
    Yes, the blocker-grade leak related to
    `allocate_robot_collision_pose_partner_device_output_columns` is resolved.
    The symbol is no longer re-exported, and tests are in place to prevent
    future regressions of this nature.

2.  **Is the remaining legacy top-level compatibility surface adequately bounded for this slice, assuming a later deprecation-cleanup slice owns `__all__`?**
    Yes, the `__dir__()` implementation in `rtdsl/__init__.py` effectively
    curates the interactive learning surface to prioritize contract-first
    elements. Legacy compatibility attributes remain importable but are no
    longer prominently displayed, setting a clear boundary for this slice and
    aligning with a future deprecation cleanup.

3.  **Should Goal2326 now close as `accept-with-boundary`, or does it still need more evidence?**
    Based on the verification of all specified fixes and the resolution of the
    blocker-grade item, Goal2326 should now close as `accept-with-boundary`.
    The changes align with the architectural goals and provide sufficient
    evidence for this stage.

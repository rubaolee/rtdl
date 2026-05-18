# External Follow-Up Review: Goal2326 Post-Review Fixes

Please perform a short independent follow-up review of the Goal2326 fixes made
after the initial Claude and Gemini reviews.

## Context

Initial reviews:

- `docs/reviews/goal2326_claude_contract_first_primitive_architecture_review_2026-05-18.md`
- `docs/reviews/goal2326_gemini_contract_first_primitive_architecture_review_2026-05-18.md`

The initial reviews both returned `accept-with-boundary`. Claude identified a
specific blocker-grade leak in the new adapter skeleton and several boundary
items.

## Files To Re-Read

- `src/rtdsl/adapters/prepared_handles.py`
- `src/rtdsl/execution.py`
- `src/rtdsl/__init__.py`
- `tests/goal2326_adapter_partition_test.py`
- `tests/goal2326_execution_report_contract_test.py`
- `tests/goal2326_public_primitive_contract_test.py`
- `docs/reports/goal2326_contract_first_primitive_reconstruction_plan_2026-05-18.md`

## Fixes To Verify

1. `src/rtdsl/adapters/prepared_handles.py` no longer re-exports
   `allocate_robot_collision_pose_partner_device_output_columns` through the
   new generic adapter package.
2. `tests/goal2326_adapter_partition_test.py` now scans adapter `__all__`
   symbols for app/domain fragments, including `robot` and `pose`.
3. `src/rtdsl/execution.py` now reports `memory_status` and `copy_status` as
   `not_reported_by_runtime`, not `not_measured`.
4. `tests/goal2326_execution_report_contract_test.py` covers that sentinel.
5. `src/rtdsl/__init__.py` now defines a curated `__dir__()` so interactive
   learners see the contract-first surface first, while legacy compatibility
   attributes remain importable.
6. `tests/goal2326_public_primitive_contract_test.py` checks that `dir(rtdsl)`
   exposes the contract-first surface and filters app-shaped learner-facing
   names.

## Questions

1. Are Claude's blocker-grade items resolved?
2. Is the remaining legacy top-level compatibility surface adequately bounded
   for this slice, assuming a later deprecation-cleanup slice owns `__all__`?
3. Should Goal2326 now close as `accept-with-boundary`, or does it still need
   more evidence?

## Expected Output

Claude follow-up:

`docs/reviews/goal2326_claude_followup_post_fix_review_2026-05-18.md`

Gemini follow-up:

`docs/reviews/goal2326_gemini_followup_post_fix_review_2026-05-18.md`

Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.

# Handoff: Review Goal2195 RayJoin Query Export Patch Plan

Please perform a read-only review of Goal2195.

## Files To Read

- `docs/reports/goal2195_rayjoin_query_exec_export_patch_plan_2026-05-17.md`
- `docs/reports/goal2195_rayjoin_query_exec_export_patch_2026-05-17.diff`
- `tests/goal2195_rayjoin_query_exec_export_patch_plan_test.py`
- `docs/reports/goal2192_rayjoin_same_query_stream_adapter_2026-05-17.md`
- `scripts/goal2192_rayjoin_same_query_stream_runner.py`

## Review Questions

1. Does the patch target the correct RayJoin phase: exporting generated PIP/LSI
   query streams from `query_exec`?
2. Does the patch preserve RayJoin algorithm behavior and only add an optional
   export flag/path?
3. Are exported PIP/LSI fields sufficient for RTDL's Goal2192 consumer?
4. Is it correct to export unscaled coordinates and RayJoin-native zero-based
   query ids?
5. Does the report avoid treating this patch as compiled pod evidence?
6. Are the next pod commands and blocked claims clear?

## Required Output

Write:

- `docs/reviews/goal2196_gemini_review_goal2195_rayjoin_export_patch_2026-05-17.md`

Use one verdict:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

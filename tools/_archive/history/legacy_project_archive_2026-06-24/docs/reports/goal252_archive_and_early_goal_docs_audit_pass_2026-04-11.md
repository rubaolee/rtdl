# Goal 252 Report: Archive And Early Goal Docs Audit Pass

Date: 2026-04-11
Status: implemented

## Summary

Goal 252 expands the audit into the archive index and the early v0.1/v0.2 goal
definition documents.

This slice is mostly historical by nature. The right standard here is not to
rewrite old goals until they read like current product docs. The right standard
is:

- archived entrypoints should be explicit about archive versus current release
- dated goal docs should remain historically understandable
- old planning and acceptance language should not be mistaken for the current
  `v0.4.0` release surface

## What Changed

Updated:

- `docs/archive/README.md`

Reviewed as acceptable historical records in this pass:

- `docs/archive/v0_1/README.md`
- `docs/goal_100_release_validation_rerun.md`
- `docs/goal_101_hello_world_all_backend_validation.md`
- `docs/goal_102_full_honest_rayjoin_reproduction.md`
- `docs/goal_103_full_honest_rayjoin_reproduction_vulkan.md`
- `docs/goal_104_rayjoin_reproduction_performance_report.md`
- `docs/goal_105_final_release_audit.md`
- `docs/goal_106_repo_wide_review_and_audit.md`
- `docs/goal_107_v0_2_roadmap_planning.md`
- `docs/goal_108_v0_2_workload_scope_charter.md`
- `docs/goal_109_archive_v0_1_baseline.md`
- `docs/goal_110_v0_2_segment_polygon_hitcount_closure.md`
- `docs/goal_111_v0_2_generate_only_mvp.md`

## Direct Outcome

- the archive index now explicitly points users back to the live `v0.4.0`
  release surface
- the early goal docs remain preserved as dated historical planning and closure
  records
- this slice confirms that the early goal-doc layer is mostly archive noise, not
  active release debt

## Why This Matters

The audit system should distinguish between:

- live docs that must stay fully current
- historical goal docs that are allowed to stay dated as long as they remain
  honest and discoverable in the right way

This pass reduces the risk of over-cleaning the historical layer while still
making the archive entrypoint safer for ordinary users.

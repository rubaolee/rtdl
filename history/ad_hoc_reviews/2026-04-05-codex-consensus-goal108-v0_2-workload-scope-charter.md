# Codex Consensus: Goal 108 v0.2 Workload Scope Charter

Date: 2026-04-05
Status: complete

## Reviewed package

- `docs/goal_108_v0_2_workload_scope_charter.md`
- `docs/v0_2_workload_scope_charter.md`
- `docs/reports/goal108_v0_2_workload_scope_charter_2026-04-05.md`
- `docs/reports/goal108_v0_2_workload_scope_charter_critique_2026-04-05.md`
- `history/ad_hoc_reviews/2026-04-05-copernicus-review-goal108-v0_2-workload-scope-charter.md`
- `history/ad_hoc_reviews/2026-04-05-meitner-review-goal108-v0_2-workload-scope-charter.md`

## Review result

- Codex:
  - APPROVE after revision
- Copernicus:
  - aggressive critique
  - demanded that the counting/ranking category be narrowed or demoted
  - demanded harder exclusion logic
- Meitner:
  - aggressive critique
  - demanded one flagship in-scope family and removal of codegen from the
    workload matrix

## Surviving charter position

The final charter that survives criticism is:

- one release-defining in-scope family:
  - additional spatial filter/refine workloads
- experimental only:
  - counting/ranking kernels
  - generalized ray/path/filter/count kernels
  - small graph/geometric counting kernels
- generate-only mode is no longer classified as a workload family
- hard gray-area non-examples are explicit
- only one in-scope family may define the v0.2 expansion at a time

## Final position

Goal 108 is accepted.

This charter is now strict enough to act as the real scope gate required by
Goal 107.

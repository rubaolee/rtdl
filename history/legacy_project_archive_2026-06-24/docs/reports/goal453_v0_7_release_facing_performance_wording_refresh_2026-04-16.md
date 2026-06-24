# Goal 453: v0.7 Release-Facing Performance Wording Refresh

Date: 2026-04-16
Author: Codex
Status: Accepted with 2-AI consensus

## Verdict

PASS. Release-facing v0.7 DB performance wording now uses Goal 452 as the
canonical comparison and separates query-only results from setup-plus-10-query
total-time results.

## Files Updated

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/README.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/features/db_workloads/README.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/tutorials/db_workloads.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_facing_examples.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/release_statement.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/support_matrix.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/audit_report.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/tag_preparation.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/history/goals/v0_7_goal_sequence_2026-04-15.md`

## New Canonical Wording

The release-facing docs now use this performance boundary:

- Goal 452 is the canonical v0.7 DB performance comparison.
- Goal 450 remains historical evidence against the original single-column
  indexed PostgreSQL baseline.
- Against the best PostgreSQL modes tested so far, query-only results are mixed.
- Embree loses query-only for `conjunctive_scan` and `grouped_count`.
- OptiX and Vulkan win query-only for all measured workloads.
- All three RTDL backends win setup-plus-10-query total time in the measured
  Linux evidence.

## Validation

Searched release-facing docs for stale broad performance wording:

```text
rg -n "Goal 443|setup/index plus repeated|setup/index plus query|fresh setup plus 10-query total against PostgreSQL|all three RT backends winning|performance win is bounded|PostgreSQL temp-table setup/index|beats PostgreSQL|fully tuned PostgreSQL" README.md docs/features/db_workloads/README.md docs/tutorials/db_workloads.md docs/release_reports/v0_7 docs/release_facing_examples.md
```

Remaining matches are acceptable:

- `docs/release_reports/v0_7/release_statement.md` says RTDL does **not** claim
  it beats fully tuned PostgreSQL in general.
- `docs/release_reports/v0_7/release_statement.md` says all RT backends win
  setup-plus-10-query total time while query-only results are mixed.
- `docs/release_reports/v0_7/audit_report.md` says the total-time performance
  win is bounded and query-only results are mixed.

Searched for required Goal 452 wording and found it in:

- README
- DB feature docs
- DB tutorial
- release-facing examples
- v0.7 release statement
- v0.7 support matrix
- v0.7 audit report
- v0.7 tag preparation

## Boundary

The refreshed docs do not claim:

- exhaustive PostgreSQL tuning
- arbitrary SQL support
- DBMS behavior
- release/tag readiness
- staging, commit, push, merge, or release authorization

## Conclusion

Goal 453 brings the public/release-facing performance story into alignment with
Goal 452. The performance claim is now narrower and more defensible than the
Goal 450 wording alone.

## External Review

External review:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal453_external_review_2026-04-16.md`

Verdict: ACCEPT.

Consensus record:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-16-codex-consensus-goal453-v0_7-release-facing-performance-wording-refresh.md`

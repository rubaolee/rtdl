# Goal 416 Review: v0.7 RT DB Lowering Runtime Contract

Date: 2026-04-15
Goal:
`/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_416_v0_7_rt_db_lowering_runtime_contract.md`
Basis:
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal416_v0_7_rt_db_lowering_runtime_contract_2026-04-15.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal415_416_ai_checker_review_2026-04-15.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal415_416_ai_verifier_review_2026-04-15.md`

## Verdict

Accept.

## Reason

Goal 416 now gives the backend line a concrete, bounded contract:

- `DbScanXYZ` for `conjunctive_scan`
- `DbGroupAggScan` for `grouped_count` and `grouped_sum`
- explicit decomposition instead of pretending arbitrary predicates fit one RT job
- explicit first-wave ceilings for rows, candidate fan-out, and grouped
  cardinality
- explicit integer-only semantics for first-wave `grouped_sum` parity

Those additions make “bounded” operational enough to start Embree bring-up
without overclaiming correctness or performance.

# Codex Consensus: Goal 416 v0.7 RT DB Lowering Runtime Contract

Date: 2026-04-15
Goal:
`/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_416_v0_7_rt_db_lowering_runtime_contract.md`

Consensus basis:
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal415_416_ai_checker_review_2026-04-15.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal415_416_ai_verifier_review_2026-04-15.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal416_v0_7_rt_db_lowering_runtime_contract_review_2026-04-15.md`

## Decision

Goal 416 is closed.

## Meaning

RTDL now has an accepted bounded RT lowering contract for the first DB backend
wave:

- `conjunctive_scan` lowers through `DbScanXYZ`
- `grouped_count` and `grouped_sum` lower through `DbGroupAggScan`
- explicit ceilings and fallback/decomposition rules are part of the contract
- Embree is the next correct implementation target

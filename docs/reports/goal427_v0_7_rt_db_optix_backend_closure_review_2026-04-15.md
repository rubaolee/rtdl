# Goal 427 Codex Review: v0.7 RT DB OptiX Backend Closure

Date: 2026-04-15
Goal:
`/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_427_v0_7_rt_db_optix_backend_closure.md`

Primary report:
`/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal427_v0_7_rt_db_optix_backend_closure_2026-04-15.md`

External review:
`/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal427_external_review_2026-04-15.md`

## Judgment

Accept.

## Basis

- The OptiX DB backend is a real RT backend, not a CPU fallback:
  - custom-primitive GAS build
  - RT candidate discovery through OptiX traversal/hit handling
  - bounded native refine and accumulation after candidate discovery
- The first bounded `v0.7` DB family is implemented on OptiX for:
  - `conjunctive_scan`
  - `grouped_count`
  - `grouped_sum`
- Linux authoritative correctness is closed:
  - `python3 -m unittest tests.goal427_v0_7_rt_db_optix_backend_test tests.goal427_v0_7_rt_db_optix_perf_test -v`
  - `Ran 8 tests`
  - `OK`
- The Linux performance package includes PostgreSQL as required by the current DB performance rule.
- The report language is honest:
  - correctness-credible
  - not yet performance-leading
  - not a warm-query PostgreSQL winner

## Boundary check

The current Goal 427 implementation stays within Goal 416:

- max 3 primary RT clauses per RT job
- max `1000000` rows per RT job
- max `250000` candidate rows per RT job
- max `65536` groups per grouped RT job
- one group key
- integer-compatible `grouped_sum` with exact `int64` accumulation

## Conclusion

Goal 427 is closed.

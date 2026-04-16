# Goal 428 Codex Review: v0.7 RT DB Vulkan Backend Closure

Date: 2026-04-15
Goal:
`/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_428_v0_7_rt_db_vulkan_backend_closure.md`

Primary report:
`/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal428_v0_7_rt_db_vulkan_backend_closure_2026-04-15.md`

## Judgment

Accept on the technical merits. Do not mark closed until an external review
artifact confirms the current Linux-backed package.

## Basis

- The Vulkan DB backend is a real RT backend, not a CPU fallback:
  - Vulkan RT AABB traversal is used for candidate discovery
  - hits set candidate-row state before bounded native refine and accumulation
- The first bounded `v0.7` DB family is implemented on Vulkan for:
  - `conjunctive_scan`
  - `grouped_count`
  - `grouped_sum`
- Linux authoritative correctness is closed:
  - `RTDL_POSTGRESQL_DSN="dbname=postgres" python3 -m unittest tests.goal428_v0_7_rt_db_vulkan_backend_test tests.goal428_v0_7_rt_db_vulkan_perf_test -v`
  - `Ran 7 tests`
  - `OK`
- The Linux performance package includes PostgreSQL as required by the current
  DB performance rule.
- The report language is honest:
  - correctness-credible
  - not yet performance-leading
  - not a warm-query PostgreSQL winner

## Boundary check

The current Goal 428 implementation stays within Goal 416:

- max 3 primary RT clauses per RT job
- max `1000000` rows per RT job
- max `250000` candidate rows per RT job
- max `65536` groups per grouped RT job
- one group key
- integer-compatible `grouped_sum` with exact `int64` accumulation

## Conclusion

Goal 428 can be closed as soon as one fresh external review artifact lands.

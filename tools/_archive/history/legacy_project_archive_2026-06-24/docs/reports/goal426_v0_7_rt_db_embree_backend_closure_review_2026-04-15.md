# Codex Review: Goal 426 — v0.7 RT DB Embree Backend Closure

Date: 2026-04-15
Reviewer: Codex
Reviewed:
- /Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal426_v0_7_rt_db_embree_backend_closure_2026-04-15.md
- /Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/embree/rtdl_embree_prelude.h
- /Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/embree/rtdl_embree_scene.cpp
- /Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/embree/rtdl_embree_api.cpp
- /Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/embree_runtime.py
- /Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal426_v0_7_rt_db_embree_backend_test.py
- /Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal426_v0_7_rt_db_embree_perf_test.py
- /Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal426_v0_7_rt_db_embree_perf_linux_2026-04-15.json

## Verdict

Accept on the technical merits. Do not mark closed until a fresh external review artifact confirms the post-fix state.

## Findings

No blocking correctness issue remains in the current implementation.

The patched Embree DB backend now satisfies the two previously material Goal 416 gaps:

- runtime ceilings are enforced in the Embree code path:
  - `1000000` rows per RT job
  - `250000` candidate rows per RT job
  - `65536` groups per grouped RT job
- `grouped_sum` now uses exact `int64` accumulation in the Embree path and emits integer sums back through the Embree runtime

The implementation remains honestly bounded:

- real Embree BVH/user-geometry traversal is used for candidate discovery
- residual clause checking still happens in native refine logic in the intersect callback
- grouped kernels remain single-group-key only
- public Embree DB execution is still direct-run only
- scalar `rtcIntersect1` dispatch is used; packet/SIMD Embree traversal is not yet implemented

## Evidence

Local focused Goal 426 band:

- `python3 -m unittest tests.goal426_v0_7_rt_db_embree_backend_test -v`
- result:
  - `Ran 7 tests`
  - `OK`

Local perf-harness unit band:

- `python3 -m unittest tests.goal426_v0_7_rt_db_embree_perf_test -v`
- result:
  - `Ran 6 tests`
  - `OK`

Fresh Linux authoritative band on `lestat-lx1`:

- `RTDL_POSTGRESQL_DSN="dbname=postgres" python3 -m unittest tests.goal426_v0_7_rt_db_embree_backend_test tests.goal426_v0_7_rt_db_embree_perf_test -v`
- result:
  - `Ran 13 tests`
  - `OK`

Linux bounded perf artifact:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal426_v0_7_rt_db_embree_perf_linux_2026-04-15.json`

The Linux performance record is internally consistent and honest:

- Embree is real and correctness-credible
- Embree is not yet faster than the CPU oracle on these bounded kernels
- PostgreSQL query-only timing is much lower on this synthetic workload, while setup dominates PostgreSQL total wall time

## Remaining blocker

The only remaining blocker to formal Goal 426 closure is process, not code:

- the fresh external review artifact has not landed yet
- the old Claude review file is stale and still reflects the pre-fix implementation

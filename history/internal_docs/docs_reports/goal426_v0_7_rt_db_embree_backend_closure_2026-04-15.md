# Goal 426 Report: v0.7 RT DB Embree Backend Closure

Date: 2026-04-15
Goal:
`/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_426_v0_7_rt_db_embree_backend_closure.md`

## Scope

Bring the first bounded `v0.7` DB kernel family onto a real Embree RT path for:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

under the accepted Goal 415/416 contract.

## What was implemented

### Native Embree DB path

New Embree ABI and scene support were added for:

- `rtdl_embree_run_conjunctive_scan`
- `rtdl_embree_run_grouped_count`
- `rtdl_embree_run_grouped_sum`

Files:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/embree/rtdl_embree_prelude.h`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/embree/rtdl_embree_scene.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/embree/rtdl_embree_api.cpp`

### Runtime integration

Embree runtime dispatch now supports the first DB family through direct
`run_embree(...)` execution:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/embree_runtime.py`

### Test coverage

Focused Embree DB tests were added:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal426_v0_7_rt_db_embree_backend_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal426_v0_7_rt_db_embree_perf_test.py`

### Performance harness

Bounded Embree DB performance harness added:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/db_perf.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal426_embree_db_perf.py`

## Execution model actually used

The Embree implementation follows the bounded RT contract:

- denormalized rows become per-row AABB/cube-style user primitives
- up to three primary scan clauses are uniformly encoded onto `x/y/z`
- Embree BVH traversal and ray/user-primitive callbacks do candidate discovery
- exact clause checking still happens in bounded native refine logic
- grouped kernels reuse the same candidate discovery path and perform bounded
  native accumulation
- the first wave currently uses scalar `rtcIntersect1` dispatch rather than
  Embree packet/SIMD traversal

This is a real RT backend path, not a CPU fallback disguised as Embree.

## Boundaries

The first Embree DB wave remains explicitly bounded:

- `grouped_count`
  - exactly one group key
- `grouped_sum`
  - exactly one group key
  - integer-compatible value fields only
  - exact `int64` partial accumulation in the Embree path
- multi-group-key grouped queries are rejected
- runtime ceilings from Goal 416 are now enforced:
  - max rows per RT job: `1000000`
  - max candidate rows per RT job: `250000`
  - max distinct groups per grouped RT job: `65536`
- the current public Embree DB path is direct-run only
  - prepared-mode support is not claimed by this goal

## Local result

Focused Embree DB band on the local worktree:

- `python3 -m unittest tests.goal426_v0_7_rt_db_embree_backend_test -v`
- result:
  - `Ran 7 tests`
  - `OK`

Focused local perf-harness unit band:

- `python3 -m unittest tests.goal426_v0_7_rt_db_embree_perf_test -v`
- result:
  - `Ran 6 tests`
  - `OK`

## Linux authoritative result

Fresh synced checkout:

- `/home/lestat/tmp/rtdl_v0_7_db_embree_check`

Focused Embree DB band on `lestat-lx1`:

- `RTDL_POSTGRESQL_DSN="dbname=postgres" python3 -m unittest tests.goal426_v0_7_rt_db_embree_backend_test tests.goal426_v0_7_rt_db_embree_perf_test -v`
- result:
  - `Ran 13 tests`
  - `OK`

Supporting native/PostgreSQL correctness band on the same fresh Linux checkout:

- `RTDL_POSTGRESQL_DSN="dbname=postgres" python3 -m unittest tests.goal420_v0_7_rt_db_conjunctive_scan_native_oracle_truth_path_test tests.goal421_v0_7_rt_db_grouped_count_native_oracle_truth_path_test tests.goal422_v0_7_rt_db_grouped_sum_native_oracle_truth_path_test tests.goal423_v0_7_postgresql_db_correctness_test tests.goal424_v0_7_postgresql_db_grouped_correctness_test -v`
- result:
  - `Ran 17 tests`
  - `OK`

Linux local perf-harness unit band:
- covered in the `13`-test fresh Linux band above

## Linux bounded performance result

Perf artifact:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal426_v0_7_rt_db_embree_perf_linux_2026-04-15.json`

Measured on `lestat-lx1` with:

- row count: `200000`
- repeats: `3`
- PostgreSQL DSN: `dbname=postgres`

### `conjunctive_scan`

- row count: `22268`
- row hash: `19461bddd250025c3d24a174f82e5f66046e40dded85ef27614143a08c9590c8`
- CPU median: `2.538s`
- Embree median: `2.642s`
- PostgreSQL query median: `0.026s`
- PostgreSQL setup median: `10.464s`

### `grouped_count`

- row count: `8`
- row hash: `869ed487d7eda66115bb00dceaf75df016fac2e2e0a6d75119f993d63137a77b`
- CPU median: `2.497s`
- Embree median: `2.554s`
- PostgreSQL query median: `0.021s`
- PostgreSQL setup median: `9.947s`

### `grouped_sum`

- row count: `8`
- row hash: `123b2f6fc6fa9f69e2df8da24441116549271314ef3b602482467c6ad47ed330`
- CPU median: `2.465s`
- Embree median: `2.591s`
- PostgreSQL query median: `0.036s`
- PostgreSQL setup median: `10.132s`

## Performance reading

The first bounded Embree DB engine is correctness-credible, but not yet
performance-leading.

What the numbers mean:

- Embree stays close to the native CPU oracle on these bounded kernels
- Embree is currently slightly slower than the CPU oracle
- PostgreSQL query-only time is much lower on this synthetic bounded workload
- PostgreSQL setup time dominates total wall time
- this first wave uses scalar rays and exact per-hit refine, so it should not
  yet be described as a performance-tuned Embree implementation

So the honest position after Goal 426 is:

- Embree DB backend: real and correct
- Embree DB backend: not yet a performance win
- further performance claims should wait for OptiX/Vulkan and the broader
  cross-engine gate

## Conclusion

Goal 426 is technically implemented and verified.

The `v0.7` DB kernel family now has:

- Python truth
- native/oracle CPU
- PostgreSQL correctness on Linux
- Embree RT backend for the first bounded family

and Goal 426 now also has a bounded Linux performance record for the Embree
engine.

The next backend target is Goal 427:

- OptiX DB backend closure

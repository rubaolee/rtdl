# Goal 428 Report: v0.7 RT DB Vulkan Backend Closure

Date: 2026-04-15
Goal:
`/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_428_v0_7_rt_db_vulkan_backend_closure.md`

## Scope

Bring the first bounded `v0.7` DB kernel family onto a real Vulkan RT path for:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

under the accepted Goal 415/416 contract.

## What was implemented

### Native Vulkan DB path

New Vulkan ABI, shader, and workload support were added for:

- `rtdl_vulkan_run_conjunctive_scan`
- `rtdl_vulkan_run_grouped_count`
- `rtdl_vulkan_run_grouped_sum`

Files:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/vulkan/rtdl_vulkan_prelude.h`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/vulkan/rtdl_vulkan_core.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/vulkan/rtdl_vulkan_api.cpp`

### Runtime integration

Vulkan runtime dispatch now supports the first DB family through direct
`run_vulkan(...)` execution:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/vulkan_runtime.py`

### Test coverage

Focused Vulkan DB tests were added:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal428_v0_7_rt_db_vulkan_backend_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal428_v0_7_rt_db_vulkan_perf_test.py`

### Performance harness

Bounded Vulkan DB performance harness added:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/db_perf.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal428_vulkan_db_perf.py`

## Execution model actually used

The Vulkan implementation follows the bounded RT contract:

- denormalized rows become per-row AABB primitives
- up to three primary scan clauses are uniformly encoded onto `x/y/z`
- Vulkan RT traversal and any-hit handling do candidate discovery
- exact clause checking still happens in bounded native refine logic
- grouped kernels reuse the same candidate discovery path and perform bounded
  native accumulation
- grouped sums keep first-wave exact `int64` accumulation parity

This is a real RT backend path, not a CPU fallback disguised as Vulkan.

## Boundaries

The first Vulkan DB wave remains explicitly bounded:

- `grouped_count`
  - exactly one group key
- `grouped_sum`
  - exactly one group key
  - integer-compatible value fields only
  - exact `int64` partial accumulation in the Vulkan path
- multi-group-key grouped queries are rejected
- runtime ceilings from Goal 416 are enforced:
  - max rows per RT job: `1000000`
  - max candidate rows per RT job: `250000`
  - max distinct groups per grouped RT job: `65536`
- the current public Vulkan DB path is direct-run only
  - prepared-mode support is not claimed by this goal

## Local result

Local Vulkan perf-harness unit band:

- `python3 -m unittest tests.goal428_v0_7_rt_db_vulkan_perf_test -v`
- result:
  - `Ran 3 tests`
  - `OK`

## Linux authoritative result

Fresh synced checkout:

- `/home/lestat/tmp/rtdl_v0_7_db_vulkan_check`

Host bring-up after fresh sync:

- `make build-vulkan`
- `rt.vulkan_version()` available after rebuild

Focused Vulkan DB band on `lestat-lx1`:

- `RTDL_POSTGRESQL_DSN="dbname=postgres" python3 -m unittest tests.goal428_v0_7_rt_db_vulkan_backend_test tests.goal428_v0_7_rt_db_vulkan_perf_test -v`
- result:
  - `Ran 7 tests`
  - `OK`

This validates:

- `conjunctive_scan` parity against Python truth and native/oracle CPU
- `grouped_count` parity against native/oracle CPU
- `grouped_sum` parity against native/oracle CPU
- PostgreSQL perf-harness helpers and backend-family measurement utilities

## Linux bounded performance result

Perf artifact:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal428_v0_7_rt_db_vulkan_perf_linux_2026-04-15.json`

Measured on `lestat-lx1` with:

- row count: `200000`
- repeats: `3`
- PostgreSQL DSN: `dbname=postgres`

### `conjunctive_scan`

- row count: `22268`
- row hash: `19461bddd250025c3d24a174f82e5f66046e40dded85ef27614143a08c9590c8`
- CPU median: `2.540s`
- Vulkan median: `2.574s`
- PostgreSQL query median: `0.026s`
- PostgreSQL setup median: `10.262s`

### `grouped_count`

- row count: `8`
- row hash: `869ed487d7eda66115bb00dceaf75df016fac2e2e0a6d75119f993d63137a77b`
- CPU median: `2.499s`
- Vulkan median: `2.597s`
- PostgreSQL query median: `0.021s`
- PostgreSQL setup median: `10.424s`

### `grouped_sum`

- row count: `8`
- row hash: `123b2f6fc6fa9f69e2df8da24441116549271314ef3b602482467c6ad47ed330`
- CPU median: `2.464s`
- Vulkan median: `2.563s`
- PostgreSQL query median: `0.036s`
- PostgreSQL setup median: `11.447s`

## Performance reading

The first bounded Vulkan DB engine is correctness-credible, but not yet
performance-leading.

What the numbers mean:

- Vulkan stays close to the native CPU oracle on these bounded kernels
- Vulkan is currently slightly slower than the CPU oracle
- PostgreSQL query-only time is much lower on this synthetic bounded workload
- PostgreSQL setup time dominates total wall time
- this first wave should not yet be described as a performance-tuned Vulkan DB
  implementation

So the honest position after Goal 428 is:

- Vulkan DB backend: real and correct
- Vulkan DB backend: not yet a performance win
- against fresh build-plus-query PostgreSQL, Vulkan remains materially faster
- against warm-query PostgreSQL, Vulkan is much slower
- broader performance claims should wait for the full cross-engine gate

## Conclusion

Goal 428 is technically implemented and verified.

The `v0.7` DB kernel family now has:

- Python truth
- native/oracle CPU
- PostgreSQL correctness on Linux
- Embree RT backend for the first bounded family
- OptiX RT backend for the first bounded family
- Vulkan RT backend for the first bounded family

and Goal 428 now also has a bounded Linux performance record for the Vulkan
engine with PostgreSQL included.

The next goal is Goal 429:

- cross-engine correctness closure against PostgreSQL on Linux

# Goal 427 Report: v0.7 RT DB OptiX Backend Closure

Date: 2026-04-15
Goal:
`/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_427_v0_7_rt_db_optix_backend_closure.md`

## Scope

Bring the first bounded `v0.7` DB kernel family onto a real OptiX RT path for:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

under the accepted Goal 415/416 contract.

## What was implemented

### Native OptiX DB path

New OptiX ABI, kernel, and workload support were added for:

- `rtdl_optix_run_conjunctive_scan`
- `rtdl_optix_run_grouped_count`
- `rtdl_optix_run_grouped_sum`

Files:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/optix/rtdl_optix_prelude.h`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/optix/rtdl_optix_core.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/optix/rtdl_optix_workloads.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/optix/rtdl_optix_api.cpp`

### Runtime integration

OptiX runtime dispatch now supports the first DB family through direct
`run_optix(...)` execution:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/optix_runtime.py`

### Test coverage

Focused OptiX DB tests were added:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal427_v0_7_rt_db_optix_backend_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal427_v0_7_rt_db_optix_perf_test.py`

### Performance harness

Bounded OptiX DB performance harness added:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/db_perf.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal427_optix_db_perf.py`

## Execution model actually used

The OptiX implementation follows the bounded RT contract:

- denormalized rows become per-row AABB custom primitives
- up to three primary scan clauses are uniformly encoded onto `x/y/z`
- OptiX GAS traversal and hit programs do candidate discovery
- exact clause checking still happens in bounded native refine logic
- grouped kernels reuse the same candidate discovery path and perform bounded
  native accumulation
- grouped sums keep first-wave exact `int64` accumulation parity

This is a real RT backend path, not a CPU fallback disguised as OptiX.

## Boundaries

The first OptiX DB wave remains explicitly bounded:

- `grouped_count`
  - exactly one group key
- `grouped_sum`
  - exactly one group key
  - integer-compatible value fields only
  - exact `int64` partial accumulation in the OptiX path
- multi-group-key grouped queries are rejected
- runtime ceilings from Goal 416 are enforced:
  - max rows per RT job: `1000000`
  - max candidate rows per RT job: `250000`
  - max distinct groups per grouped RT job: `65536`
- the current public OptiX DB path is direct-run only
  - prepared-mode support is not claimed by this goal

## Local result

Focused local OptiX-supporting unit band:

- `python3 -m unittest tests.goal427_v0_7_rt_db_optix_backend_test tests.goal427_v0_7_rt_db_optix_perf_test -v`
- result on macOS:
  - `Ran 8 tests`
  - `OK (skipped=4)`

The local skips are expected because the macOS host does not provide the OptiX
runtime library.

## Linux authoritative result

Fresh synced checkout:

- `/home/lestat/tmp/rtdl_v0_7_db_optix_check`

Host bring-up after fresh sync:

- `make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev CUDA_PREFIX=/usr NVCC=/usr/bin/nvcc`
- `rt.optix_version()`:
  - `(9, 0, 0)`

Focused OptiX DB band on `lestat-lx1`:

- `python3 -m unittest tests.goal427_v0_7_rt_db_optix_backend_test tests.goal427_v0_7_rt_db_optix_perf_test -v`
- result:
  - `Ran 8 tests`
  - `OK`

This validates:

- `conjunctive_scan` parity against Python truth and native/oracle CPU
- `grouped_count` parity against native/oracle CPU
- `grouped_sum` parity against native/oracle CPU
- PostgreSQL perf-harness helpers and backend-family measurement utilities

## Linux bounded performance result

Perf artifact:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal427_v0_7_rt_db_optix_perf_linux_2026-04-15.json`

Measured on `lestat-lx1` with:

- row count: `200000`
- repeats: `3`
- PostgreSQL DSN: `dbname=postgres`

### `conjunctive_scan`

- row count: `22268`
- row hash: `19461bddd250025c3d24a174f82e5f66046e40dded85ef27614143a08c9590c8`
- CPU median: `2.523s`
- OptiX median: `2.563s`
- PostgreSQL query median: `0.026s`
- PostgreSQL setup median: `10.300s`

### `grouped_count`

- row count: `8`
- row hash: `869ed487d7eda66115bb00dceaf75df016fac2e2e0a6d75119f993d63137a77b`
- CPU median: `2.487s`
- OptiX median: `2.526s`
- PostgreSQL query median: `0.021s`
- PostgreSQL setup median: `10.959s`

### `grouped_sum`

- row count: `8`
- row hash: `123b2f6fc6fa9f69e2df8da24441116549271314ef3b602482467c6ad47ed330`
- CPU median: `2.460s`
- OptiX median: `2.546s`
- PostgreSQL query median: `0.036s`
- PostgreSQL setup median: `10.146s`

## Performance reading

The first bounded OptiX DB engine is correctness-credible, but not yet
performance-leading.

What the numbers mean:

- OptiX stays close to the native CPU oracle on these bounded kernels
- OptiX is currently slightly slower than the CPU oracle
- PostgreSQL query-only time is much lower on this synthetic bounded workload
- PostgreSQL setup time dominates total wall time
- this first wave should not yet be described as a performance-tuned OptiX DB
  implementation

So the honest position after Goal 427 is:

- OptiX DB backend: real and correct
- OptiX DB backend: not yet a performance win
- against fresh build-plus-query PostgreSQL, OptiX remains materially faster
- against warm-query PostgreSQL, OptiX is much slower
- broader performance claims should wait for Vulkan and the cross-engine gate

## Conclusion

Goal 427 is technically implemented and verified.

The `v0.7` DB kernel family now has:

- Python truth
- native/oracle CPU
- PostgreSQL correctness on Linux
- Embree RT backend for the first bounded family
- OptiX RT backend for the first bounded family

and Goal 427 now also has a bounded Linux performance record for the OptiX
engine with PostgreSQL included.

The next backend target is Goal 428:

- Vulkan DB backend closure

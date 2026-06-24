# Goal 432 Report: v0.7 RT DB Phase-Split Performance Clarification

Date: 2026-04-15
Goal:
`/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_432_v0_7_rt_db_phase_split_perf_clarification.md`

## Purpose

Goal 430 established the bounded Linux performance record for the first `v0.7`
DB family, but the comparison still mixed:

- RTDL end-to-end total

with PostgreSQL's already-separated:

- setup
- query

Goal 432 closes that methodological gap by splitting RTDL into:

- `prepare`
- `execute`
- `total`

for all three RT backends on Linux.

## What was added

### Runtime support

Prepared DB execution paths were added for:

- Embree
- OptiX
- Vulkan

Files:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/embree_runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/optix_runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/vulkan_runtime.py`

These prepared DB paths do not claim a persistent warm-query scene cache. They
support a bounded measurement split where:

- `prepare`
  - normalizes/encodes the DB workload inputs
  - builds the backend-side prepared execution object
- `execute`
  - runs the prepared execution object once
- `total`
  - measures `prepare + execute` together

### Harness support

Files:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/db_perf.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal432_db_phase_split_perf_gate.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal432_v0_7_rt_db_phase_split_perf_test.py`

Artifact:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal432_db_phase_split_perf_linux_2026-04-15.json`

## Validation

Local:

- `python3 -m py_compile`
  - updated runtimes
  - `db_perf.py`
  - `goal432_db_phase_split_perf_gate.py`
  - `goal432_v0_7_rt_db_phase_split_perf_test.py`
- `python3 -m unittest tests.goal432_v0_7_rt_db_phase_split_perf_test -v`
  - `Ran 1 test`
  - `OK`

Linux authoritative:

- `python3 -m unittest tests.goal432_v0_7_rt_db_phase_split_perf_test -v`
  - `Ran 1 test`
  - `OK`
- `RTDL_POSTGRESQL_DSN="dbname=postgres" PYTHONPATH=src:. python3 scripts/goal432_db_phase_split_perf_gate.py --row-count 200000 --repeats 3`

## Linux phase-split result

Measured on `lestat-lx1` with:

- row count: `200000`
- repeats: `3`
- PostgreSQL DSN: `dbname=postgres`

### `conjunctive_scan`

- Embree
  - prepare `2.614s`
  - execute `0.093s`
  - total `2.708s`
- OptiX
  - prepare `2.732s`
  - execute `0.068s`
  - total `3.055s`
- Vulkan
  - prepare `2.706s`
  - execute `0.076s`
  - total `2.869s`
- PostgreSQL
  - setup `10.169s`
  - query `0.026s`

### `grouped_count`

- Embree
  - prepare `2.501s`
  - execute `0.071s`
  - total `2.572s`
- OptiX
  - prepare `2.583s`
  - execute `0.042s`
  - total `2.624s`
- Vulkan
  - prepare `2.435s`
  - execute `0.050s`
  - total `2.485s`
- PostgreSQL
  - setup `10.054s`
  - query `0.021s`

### `grouped_sum`

- Embree
  - prepare `2.553s`
  - execute `0.082s`
  - total `2.635s`
- OptiX
  - prepare `2.588s`
  - execute `0.047s`
  - total `2.630s`
- Vulkan
  - prepare `2.598s`
  - execute `0.050s`
  - total `2.647s`
- PostgreSQL
  - setup `10.028s`
  - query `0.036s`

## Reading

This split clarifies the Linux performance story materially.

### What dominates RTDL today

For the current first-wave RT DB family, RTDL time is dominated by:

- prepare/build work

The backend execute phase itself is much smaller:

- about `0.04s` to `0.09s`

### What dominates PostgreSQL today

For the current harness, PostgreSQL time is dominated by:

- setup/materialization/index work

The PostgreSQL query phase itself is even smaller:

- about `0.02s` to `0.036s`

### Clean comparison

The correct apples-to-apples readings are now:

- RTDL total vs PostgreSQL total
- RTDL execute vs PostgreSQL query

From this artifact:

- RTDL total still beats PostgreSQL setup+query clearly
- RTDL execute still loses to warm-query PostgreSQL clearly

### Backend reading

Across the RT backends:

- execute phase:
  - OptiX and Vulkan are usually somewhat better than Embree
- total phase:
  - all three remain close because prepare dominates total time

## Honest conclusion

Goal 432 does not change the overall bounded DB performance conclusion.

What it improves is the methodological clarity:

- RTDL is now measured in a two-phase form on Linux
- PostgreSQL remains measured in a two-phase form on Linux
- the repo can now state explicitly that:
  - RTDL total beats fresh PostgreSQL total in this harness
  - RTDL execute does not beat PostgreSQL query

So the current honest performance position after Goal 432 is:

- RTDL DB performance is correctness-credible and methodologically clearer
- RTDL is not a warm-query PostgreSQL winner
- RTDL is competitive only under the fresh-build one-shot reading in this
  bounded first-wave harness

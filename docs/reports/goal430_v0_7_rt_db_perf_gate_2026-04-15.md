# Goal 430 Report: v0.7 RT DB Performance Gate

Date: 2026-04-15
Goal:
`/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_430_v0_7_rt_db_perf_gate.md`

## Scope

Measure the first bounded `v0.7` DB kernel family across all implemented RT
engines against PostgreSQL on Linux.

Measured workloads:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

Measured engines:

- `embree`
- `optix`
- `vulkan`
- `postgresql`

Boundary:

- the native CPU oracle is not the performance target for this goal
- PostgreSQL on Linux is required in every meaningful DB perf reading

## What was implemented

Added a merged Linux DB performance gate script:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal430_db_perf_gate.py`

This script runs the bounded DB family through:

- Embree
- OptiX
- Vulkan

and merges those RT measurements with:

- PostgreSQL query timing
- PostgreSQL setup timing

Perf artifact:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal430_v0_7_rt_db_perf_gate_linux_2026-04-15.json`

## Linux authoritative result

Measured on `lestat-lx1` with:

- row count: `200000`
- repeats: `3`
- PostgreSQL DSN: `dbname=postgres`

Command:

- `RTDL_POSTGRESQL_DSN="dbname=postgres" python3 scripts/goal430_db_perf_gate.py --row-count 200000 --repeats 3`

## Bounded performance result

### `conjunctive_scan`

- row count: `22268`
- row hash: `19461bddd250025c3d24a174f82e5f66046e40dded85ef27614143a08c9590c8`
- Embree median: `2.594s`
- OptiX median: `2.633s`
- Vulkan median: `2.624s`
- PostgreSQL query median: `0.026s`
- PostgreSQL setup median: `10.286s`

### `grouped_count`

- row count: `8`
- row hash: `869ed487d7eda66115bb00dceaf75df016fac2e2e0a6d75119f993d63137a77b`
- Embree median: `2.645s`
- OptiX median: `2.544s`
- Vulkan median: `2.508s`
- PostgreSQL query median: `0.021s`
- PostgreSQL setup median: `11.104s`

### `grouped_sum`

- row count: `8`
- row hash: `123b2f6fc6fa9f69e2df8da24441116549271314ef3b602482467c6ad47ed330`
- Embree median: `2.598s`
- OptiX median: `2.566s`
- Vulkan median: `2.547s`
- PostgreSQL query median: `0.036s`
- PostgreSQL setup median: `11.172s`

## Reading

The first bounded `v0.7` RT DB engines are now all in the same rough
performance band on Linux:

- low-single-digit seconds for the current `200000`-row bounded cases
- small spread between Embree, OptiX, and Vulkan

The PostgreSQL comparison has two clearly different readings:

### Warm-query reading

If the PostgreSQL table is already materialized and indexed, PostgreSQL query
execution is much faster than the current RT backends:

- about `0.021s` to `0.036s` for the three bounded queries
- versus about `2.5s` to `2.6s` for the current RT backends

So none of the current RT backends is a warm-query PostgreSQL winner.

### Fresh build-plus-query reading

If PostgreSQL has to pay fresh setup/materialization/index cost inside the same
run, PostgreSQL total wall time is much larger:

- about `10.3s` to `11.2s` setup
- plus a much smaller query term

Under that one-shot reading, the RT backends are materially faster than fresh
PostgreSQL build-plus-query on these bounded cases.

## Honest claim boundary

Goal 430 establishes a bounded performance record, not a blanket database
performance claim.

What is now justified:

- all three RT backends are real and correctness-credible
- all three RT backends have bounded Linux performance records with PostgreSQL
  included
- fresh PostgreSQL setup dominates PostgreSQL total wall time in this harness

What is not justified:

- claiming RT backends beat warm PostgreSQL query execution
- claiming these numbers generalize to full SQL or full DBMS behavior
- claiming a broad RT database performance win from the current first-wave
  kernels

## Conclusion

Goal 430 is technically implemented and verified.

The first bounded `v0.7` DB family now has:

- cross-engine correctness closure
- bounded Linux performance records for:
  - Embree
  - OptiX
  - Vulkan
  - PostgreSQL

The current honest performance position is:

- RT correctness: closed for the first bounded DB family
- RT performance credibility: established
- RT performance leadership over warm PostgreSQL: not established

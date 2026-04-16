# Goal 413 Report: v0.7 RT Database Workload Scope And Goal Ladder

Date: 2026-04-15
Goal:
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_413_v0_7_rt_db_workload_scope_and_goal_ladder.md`

Sequence:
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/history/goals/v0_7_goal_sequence_2026-04-15.md`

Planning basis:
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal412_rt_db_workload_analysis_for_next_version_2026-04-15.md`

## Decision

The next RTDL version is opened as `v0.7`.

`v0.7` is defined as the bounded RTDL line for **database-style analytical
workloads** that can be transformed into RT traversal/intersection work, while
preserving RTDL as a workload-kernel/runtime system rather than a DBMS.

## Why this is a new version line

The released `v0.6.1` line is already coherent and bounded around:

- RT graph kernels
- `bfs`
- `triangle_count`

The accepted database-style direction changes the workload family, the data
assumptions, the correctness baselines, and the public narrative enough that it
should not be treated as a patch-level continuation of `v0.6.1`.

Therefore:

- `v0.6.1` remains the released RT graph line
- `v0.7` opens as the bounded RT database-workload line

## Scope accepted for v0.7

`v0.7` accepts:

- denormalized / pre-joined flat data as the core data model
- offline or amortized encoding and BVH/index build assumptions
- predicate-driven analytical scan/filter kernels
- fused grouped aggregate kernels over filtered denormalized data
- explicit external correctness/performance comparison against PostgreSQL

## Scope rejected for v0.7

`v0.7` rejects:

- full SQL engine claims
- online joins as first-class RT workloads
- transactional / OLTP claims
- arbitrary relational operator closure
- optimizer-complete claims
- arbitrary subquery support

## Initial kernel family for execution

The first execution ladder is intentionally narrow.

The first RT-kernel family is:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

Reason:

- `conjunctive_scan` is the strongest direct continuation from RTScan
- `grouped_count` and `grouped_sum` are the lowest-friction grouped aggregates
  to bring up from the RayDB side
- this is enough to test the RTDL database-workload interpretation without
  overcommitting the language or runtime

Other candidates such as `grouped_avg`, `grouped_min`, and `grouped_max`
remain justified by the paper analysis, but they do not need to be in the
first implementation slice.

## Implementation ladder

The `v0.7` ladder is:

1. define the kernel surface
2. define the execution interpretation
3. define the lowering/runtime contract
4. close bounded Python truth paths for the first three kernels
5. close bounded oracle/native truth paths for the same kernels
6. anchor correctness against PostgreSQL
7. measure bounded performance against PostgreSQL
8. expose the public tutorial/example surface
9. run release review/doc/audit gates

This keeps the work ordered from semantics to truth path to external evidence.

## Why PostgreSQL is the right external anchor

For this line, PostgreSQL is a better first external anchor than a custom host
reference alone because:

- the target workload family is database-style analytical work
- correctness claims should be checked against a real database execution model
- the project already has a disciplined PostgreSQL-backed correctness/perf
  workflow from earlier bounded gates

This does not imply that RTDL is competing as a DBMS. It means the bounded
analytical kernel results should be checked against a professional database
baseline.

## Version-level honesty boundary

The right `v0.7` claim is:

- RTDL supports a bounded family of RT-accelerated analytical database-style
  workloads

The wrong `v0.7` claim would be:

- RTDL is a database system
- RTDL is a SQL execution engine
- RTDL supports general relational query processing

## Final planning judgment

`v0.7` is now correctly opened as a bounded new line.

The ladder in `/docs/history/goals/v0_7_goal_sequence_2026-04-15.md` is narrow
enough to execute honestly and broad enough to deliver a real next-version
workload family.

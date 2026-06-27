# Goal 452: v0.7 RTDL vs Best-Tested PostgreSQL Performance Rebase

Date: 2026-04-16
Author: Codex
Status: Accepted with 2-AI consensus

## Verdict

The strongest honest performance comparison is now:

- RTDL wins **setup-plus-10-query total time** against the best PostgreSQL mode
  tested in Goal 451 for all measured workload/backend combinations.
- RTDL does **not** universally win **query-only median time** against the best
  PostgreSQL mode tested. Embree loses query-only comparison for
  `conjunctive_scan` and `grouped_count`; OptiX and Vulkan win the query-only
  comparison in all measured workloads.

This replaces the simpler Goal 450 phrasing that compared only against the
single-column indexed PostgreSQL baseline.

## Evidence

Script:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal452_rtdl_vs_best_tested_postgresql_perf_rebase.py`

Generated JSON:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal452_rtdl_vs_best_tested_postgresql_perf_rebase_2026-04-16.json`

Source evidence:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal450_columnar_repeated_query_perf_linux_2026-04-16.json`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal451_postgresql_baseline_index_audit_linux_2026-04-16.json`

Compatibility checks:

- Row count: 200,000 in both source files.
- Repeats: 10 in both source files.
- PostgreSQL DSN: `dbname=postgres` in both source files.
- Workload row hashes match between RTDL/Goal 450 and PostgreSQL/Goal 451.

## Best-Tested PostgreSQL Modes

| Workload | Best PostgreSQL query-time mode | Best PostgreSQL total-time mode |
|---|---|---|
| conjunctive_scan | composite | composite |
| grouped_count | composite | no_index |
| grouped_sum | single_column | covering |

These are best among the modes tested in Goal 451 only:

- `no_index`
- `single_column`
- `composite`
- `covering`

They are not a claim of exhaustive PostgreSQL tuning.

## Rebased Comparison

Speedup values are `PostgreSQL time / RTDL time`. Values below `1.00x` mean
PostgreSQL was faster for that phase.

| Workload | Backend | Query speedup vs best-tested PG | Total speedup vs best-tested PG | Hash match |
|---|---:|---:|---:|---|
| conjunctive_scan | Embree | 0.98x | 8.61x | yes |
| conjunctive_scan | OptiX | 1.44x | 5.88x | yes |
| conjunctive_scan | Vulkan | 1.20x | 6.19x | yes |
| grouped_count | Embree | 0.92x | 9.04x | yes |
| grouped_count | OptiX | 2.71x | 10.25x | yes |
| grouped_count | Vulkan | 1.82x | 9.91x | yes |
| grouped_sum | Embree | 1.02x | 7.84x | yes |
| grouped_sum | OptiX | 3.08x | 9.84x | yes |
| grouped_sum | Vulkan | 2.53x | 9.53x | yes |

## Claim Boundary

Allowed claim:

> On the tested Linux host and bounded v0.7 DB workloads, RTDL columnar
> prepared datasets beat the best PostgreSQL index mode tested for
> setup-plus-10-query total time across Embree, OptiX, and Vulkan. Query-only
> median time is mixed: OptiX and Vulkan win in this evidence, while Embree is
> roughly comparable and loses two query-only comparisons.

Not allowed:

- RTDL is faster than PostgreSQL in general.
- RTDL beats a fully tuned PostgreSQL deployment.
- RTDL supports arbitrary SQL.
- RTDL is a DBMS.

## Interpretation

Goal 452 is the more defensible performance story:

- Goal 450 remains useful as continuity against the original indexed baseline.
- Goal 451 proves that the original PostgreSQL baseline was indexed but not
  fully tuned.
- Goal 452 rebases the performance comparison against the best PostgreSQL mode
  that was actually tested.

The main RTDL advantage in this evidence is total time when a prepared RTDL
dataset can be reused for repeated query execution. The query-only advantage is
backend-dependent and should be reported separately from total time.

## Release Boundary

No staging, commit, tag, push, merge, or release action was performed.

## External Review

Valid external review:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal452_external_review_2026-04-16.md`

Verdict: ACCEPT.

Invalid preserved attempt:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal452_external_review_gemini_attempt_overbroad_2026-04-16.md`

The invalid attempt is preserved because its conclusion was too broad about
performance advantages and did not emphasize the Embree query-only losses.

Consensus record:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-16-codex-consensus-goal452-v0_7-rtdl-vs-best-tested-postgresql-perf-rebase.md`

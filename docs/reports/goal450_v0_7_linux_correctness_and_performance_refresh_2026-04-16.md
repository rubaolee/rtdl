# Goal 450: v0.7 Linux Correctness And Performance Refresh

Date: 2026-04-16
Author: Codex
Status: Accepted with 2-AI consensus

## Verdict

PASS. The current v0.7 DB columnar state passed the Linux correctness sweep with
live PostgreSQL enabled, and the PostgreSQL-inclusive repeated-query performance
gate completed successfully on Embree, OptiX, and Vulkan.

## Linux Host

- Host: `lestat-lx1`
- Synced checkout: `/home/lestat/work/rtdl_v0_7_linux_validation`
- PostgreSQL: `psql (PostgreSQL) 16.13 (Ubuntu 16.13-0ubuntu0.24.04.1)`
- PostgreSQL readiness: `/var/run/postgresql:5432 - accepting connections`
- GPU: `NVIDIA GeForce GTX 1070`
- Embree runtime: `(4, 3, 0)`
- OptiX runtime: `(9, 0, 0)`
- Vulkan runtime: `(0, 1, 0)`

OptiX and Vulkan libraries were built in the Linux validation checkout before
running the final tests.

## Correctness Evidence

Final correctness command used live PostgreSQL:

```text
RTDL_POSTGRESQL_DSN=dbname=postgres PYTHONPATH=src:. python3 -m unittest -v <v0.7 DB correctness modules>
```

Evidence:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/linux_correctness_db_sweep_with_postgresql_2026-04-16.log`

Result:

- Ran 75 tests.
- Failures: 0.
- Errors: 0.
- Skips: 0.
- Final status: `OK`.

Coverage included:

- Python DB truth paths.
- Native CPU oracle truth paths.
- Live PostgreSQL correctness for scan, grouped count, and grouped sum.
- Embree DB backend correctness.
- OptiX DB backend correctness.
- Vulkan DB backend correctness.
- Cross-engine PostgreSQL correctness gate.
- Prepared native DB datasets.
- Row/columnar transfer parity.
- High-level prepared DB columnar defaults.

## Performance Evidence

Performance command:

```text
PYTHONPATH=src:. python3 scripts/goal443_columnar_repeated_query_perf_gate.py --row-count 200000 --repeats 10 --dsn dbname=postgres
```

Evidence:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/linux_perf_goal443_columnar_repeated_query_2026-04-16.log`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal450_columnar_repeated_query_perf_linux_2026-04-16.json`

The performance comparison uses:

- RTDL prepared columnar dataset build plus 10 repeated queries.
- PostgreSQL setup plus 10 repeated queries.
- Row-hash comparison against PostgreSQL for correctness.

## Performance Summary

| Workload | Backend | RTDL prepare s | RTDL median query s | RTDL total repeated s | PostgreSQL total repeated s | Total speedup vs PostgreSQL | Hash match |
|---|---:|---:|---:|---:|---:|---:|---|
| conjunctive_scan | Embree | 0.864253 | 0.016818 | 1.032492 | 12.932132 | 12.53x | yes |
| conjunctive_scan | OptiX | 0.987057 | 0.011392 | 1.512182 | 12.932132 | 8.55x | yes |
| conjunctive_scan | Vulkan | 0.991006 | 0.013680 | 1.436118 | 12.932132 | 9.00x | yes |
| grouped_count | Embree | 0.836521 | 0.014136 | 0.978067 | 10.265618 | 10.50x | yes |
| grouped_count | OptiX | 0.813415 | 0.004817 | 0.862707 | 10.265618 | 11.90x | yes |
| grouped_count | Vulkan | 0.818828 | 0.007159 | 0.891568 | 10.265618 | 11.51x | yes |
| grouped_sum | Embree | 0.829535 | 0.031795 | 1.148854 | 10.962589 | 9.54x | yes |
| grouped_sum | OptiX | 0.809463 | 0.010510 | 0.915717 | 10.962589 | 11.97x | yes |
| grouped_sum | Vulkan | 0.815303 | 0.012808 | 0.945158 | 10.962589 | 11.60x | yes |

## Interpretation Boundary

This is a Linux validation result for the current bounded v0.7 DB workload
family. It supports the claim that the columnar prepared RTDL path is
correctness-aligned with PostgreSQL for the tested workloads and faster than
PostgreSQL setup-plus-10-query timing in this benchmark configuration.

It does not claim RTDL is a database system, does not cover arbitrary SQL, and
does not replace external release testing.

## Release Boundary

No staging, commit, tag, push, or main merge was performed.

## External Review

External review:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal450_external_review_2026-04-16.md`

Verdict: ACCEPT.

Consensus record:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-16-codex-consensus-goal450-v0_7-linux-correctness-and-performance-refresh.md`

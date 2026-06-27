# Codex Consensus: Goal 443 v0.7 Columnar Repeated-Query Performance Gate

Date: 2026-04-16

## Verdict

ACCEPT.

Goal 443 has the required 2-AI consensus:

- Codex review: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal443_v0_7_columnar_repeated_query_perf_gate_review_2026-04-16.md`
- Claude external review: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal443_external_review_2026-04-16.md`

## Basis

The refreshed Linux repeated-query gate now measures the three RT backends with
columnar prepared DB dataset transfer:

- Embree: `transfer="columnar"`
- OptiX: `transfer="columnar"`
- Vulkan: `transfer="columnar"`

PostgreSQL setup/query is included on Linux through `dbname=postgres`.

Correctness is enforced by row-count/hash equality across:

- Python truth
- PostgreSQL
- Embree
- OptiX
- Vulkan

Measured workloads:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

All nine backend/workload pairs report `wins_from_first_query` under this
fresh-setup 200k-row, 10-query gate. Total RTDL speedups versus PostgreSQL
fresh setup plus 10 queries range from about 6.84x to 14.01x.

## Boundary

This consensus does not change the claim boundary. RTDL remains a bounded
workload-kernel/runtime system, not a DBMS or arbitrary SQL engine. The
performance claim is limited to the measured Linux synthetic gate.

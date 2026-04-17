# Codex Consensus: Goal 436 v0.7 Vulkan Native Prepared DB Dataset

Date: 2026-04-16

## Verdict

ACCEPT.

Goal 436 has the required 2-AI consensus:

- Codex review: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal436_v0_7_vulkan_native_prepared_db_dataset_review_2026-04-16.md`
- Claude external review: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal436_external_review_2026-04-16.md`

## Basis

The Vulkan backend now exposes a native prepared DB dataset handle, owns copied table data and built BLAS/TLAS state, and reuses that state for `conjunctive_scan`, `grouped_count`, and `grouped_sum`.

Linux validation on `lestat-lx1` passed:

- `make build-vulkan`
- `PYTHONPATH=src:. python3 -m unittest tests.goal436_v0_7_vulkan_native_prepared_db_dataset_test -v`
- `RTDL_POSTGRESQL_DSN="dbname=postgres" PYTHONPATH=src:. python3 scripts/goal436_vulkan_native_prepared_db_dataset_perf_gate.py --row-count 200000 --repeats 10 --dsn "dbname=postgres"`

The PostgreSQL-inclusive perf gate shows matching row hashes for all three workloads and lower Vulkan median query latency plus lower prepare-once plus ten-query total for the bounded synthetic cases.

## Boundary

This consensus closes Vulkan prepared acceleration-structure reuse. It does not claim that final large-table ingestion is solved, because Python-to-native table ingestion still uses the compatibility ctypes row path.

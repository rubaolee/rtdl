# Goal 438: v0.7 Release Gate Refresh After Native Prepared DB

Date: 2026-04-16

## Verdict

Goal 438 is implemented and ready for external review.

The `v0.7` branch-facing docs now reflect the native prepared DB dataset closure and repeated-query performance gate from Goals 434-437. The refresh preserves the no-merge/no-tag boundary.

## Files Updated

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/README.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/README.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/quick_tutorial.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_facing_examples.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/tutorials/db_workloads.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/features/README.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/features/db_workloads/README.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/release_statement.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/support_matrix.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/audit_report.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/tag_preparation.md`

## Refresh Summary

The front page now states that the bounded `v0.7` DB branch includes native prepared DB dataset reuse on Embree, OptiX, and Vulkan.

The `v0.7` release statement and support matrix now record:

- native prepared scene/GAS/TLAS reuse
- PostgreSQL-inclusive repeated-query performance gate
- Linux 200k-row bounded synthetic evidence
- compatibility ctypes ingestion caveat
- no-DBMS and no-arbitrary-SQL boundaries

The tutorial and example docs now point users to:

- DB CLI examples for `conjunctive_scan`, `grouped_count`, and `grouped_sum`
- DB tutorial ladder entry
- DB feature home
- Goal 437 repeated-query evidence

The tag-preparation document still says not to tag `v0.7` yet.

## Verification

Local checks:

```text
python3 -m py_compile scripts/goal437_repeated_query_db_perf_summary.py
PYTHONPATH=src:. python3 -m unittest tests.goal436_v0_7_vulkan_native_prepared_db_dataset_test -v
OK (skipped=1 on local macOS because Vulkan library is not built)
```

Linux evidence already closed by Goals 436 and 437:

```text
make build-vulkan
PYTHONPATH=src:. python3 -m unittest tests.goal436_v0_7_vulkan_native_prepared_db_dataset_test -v
Ran 4 tests in 0.704s
OK
```

```text
RTDL_POSTGRESQL_DSN="dbname=postgres" PYTHONPATH=src:. python3 scripts/goal436_vulkan_native_prepared_db_dataset_perf_gate.py --row-count 200000 --repeats 10 --dsn "dbname=postgres"
```

## Boundary

This is a documentation/release-gate refresh only. It does not merge to `main`, does not create a tag, and does not broaden `v0.7` beyond the bounded DB kernel family.

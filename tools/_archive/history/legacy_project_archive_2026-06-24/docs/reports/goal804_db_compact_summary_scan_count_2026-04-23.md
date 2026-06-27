# Goal804: DB Compact Summary Scan Count

## Objective

Move the public `database_analytics` app one step closer to the v1.0 NVIDIA
RT-core target by avoiding row-ID materialization when the app only needs a
scan count. This is local-first work for the next batched RTX cloud run; it
does not authorize a DB speedup claim by itself.

## Changes

- Added native OptiX prepared DB scan-count ABI:
  - `rtdl_optix_db_dataset_conjunctive_scan_count(...)`
  - Python wrapper: `PreparedOptixDbDataset.conjunctive_scan_count(...)`
- Added app-level `compact_summary` output mode to:
  - `examples/rtdl_database_analytics_app.py`
  - `examples/rtdl_sales_risk_screening.py`
  - `examples/rtdl_v0_7_db_app_demo.py`
- Updated the DB prepared-session profiler to accept
  `--output-mode compact_summary`.
- Updated the RTX cloud benchmark manifest so the next paid DB entries use
  `compact_summary` instead of materializing scan row IDs.
- Corrected the public OptiX DB wording:
  - OptiX DB already uses real BVH candidate discovery.
  - Exact filtering and grouped aggregation are native C++ host-side work after
    candidate bitset copy-back, not Python logic.
  - Remaining blockers are Python/ctypes preparation, candidate bitset
    copy-back, grouped-row decoding, row materialization where still requested,
    and missing native phase counters.

## Boundaries

- This goal does not claim broad DB app speedup.
- This goal does not make RTDL a SQL engine or DBMS.
- `compact_summary` intentionally drops full scan row IDs and returns counts
  for app-level summary timing. Use `summary` or `full` when row IDs are needed.
- Cloud policy remains batched-only: no per-app pod restart is required for
  this change.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal804_db_compact_summary_scan_count_test \
  tests.goal756_prepared_db_app_session_test \
  tests.goal756_db_prepared_session_perf_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal803_rt_core_app_maturity_contract_test \
  tests.goal690_optix_performance_classification_test \
  tests.goal705_optix_app_benchmark_readiness_test

Result: 31 tests OK
```

```text
python3 -m py_compile \
  src/rtdsl/optix_runtime.py \
  src/rtdsl/app_support_matrix.py \
  examples/rtdl_database_analytics_app.py \
  examples/rtdl_sales_risk_screening.py \
  examples/rtdl_v0_7_db_app_demo.py \
  scripts/goal756_db_prepared_session_perf.py \
  scripts/goal759_rtx_cloud_benchmark_manifest.py \
  tests/goal804_db_compact_summary_scan_count_test.py

Result: OK
```

```text
git diff --check

Result: OK
```

```text
PYTHONPATH=src:. python3 scripts/goal756_db_prepared_session_perf.py \
  --backend cpu \
  --scenario sales_risk \
  --copies 2 \
  --iterations 2 \
  --output-mode compact_summary \
  --strict

Result: compact_summary accepted; backend status OK; risky_order_count 8.
```

## Next Work

- Rebuild OptiX on Linux/RTX in the next batched cloud session and confirm that
  the new native scan-count symbol is exported and used.
- Add native DB phase counters if we want to promote DB from
  `rt_core_partial_ready` to `rt_core_ready`.
- Keep DB cloud evidence separate from fixed-radius and robot scalar-summary
  evidence.

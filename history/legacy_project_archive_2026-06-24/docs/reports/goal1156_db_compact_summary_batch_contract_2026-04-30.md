# Goal1156 DB Compact-Summary Batch Contract

Date: 2026-04-30

## Summary

Goal1156 added a prepared DB compact-summary batch contract for the `database_analytics` app path.

This is a local interface and contract improvement. It does not authorize public RTX speedup wording and does not claim a native OptiX single-launch batch implementation yet.

## Changes

- Added `compact_summary_batch(requests)` and `last_compact_summary_batch_phase_timings()` to prepared OptiX DB datasets.
- Added the same contract to prepared Embree DB datasets for same-semantics baseline parity.
- Added an optional Python runtime hook for a future `rtdl_optix_db_dataset_compact_summary_batch` native symbol. If the symbol is absent, the runtime falls back to the current dispatcher path.
- Updated `examples/rtdl_v0_7_db_app_demo.py` to use one compact-summary batch call for its scan count, grouped count summary, and grouped sum summary.
- Updated `examples/rtdl_sales_risk_screening.py` to use one compact-summary batch call for its scan count, grouped count summary, and grouped sum summary.
- Updated the Goal756 DB profiler to recognize `query_compact_summary_batch_sec` as a compact-summary operation covering scan, grouped count, and grouped sum.
- Added `tests/goal1156_db_compact_summary_batch_contract_test.py`.

## Local Evidence

Focused tests:

`PYTHONPATH=src:. python3 -m unittest tests.goal1156_db_compact_summary_batch_contract_test tests.goal954_database_native_continuation_contract_test tests.goal1128_embree_db_compact_summary_contract_test tests.goal851_optix_db_sales_grouped_summary_fastpath_test tests.goal850_optix_db_grouped_summary_fastpath_test tests.goal756_db_prepared_session_perf_test -v`

Result: `20 tests OK`.

Follow-up native-hook focused tests:

`PYTHONPATH=src:. python3 -m unittest tests.goal1156_db_compact_summary_batch_contract_test tests.goal954_database_native_continuation_contract_test tests.goal756_db_prepared_session_perf_test -v`

Result: `16 tests OK`.

Local Embree profile:

`PYTHONPATH=src:. python3 scripts/goal756_db_prepared_session_perf.py --backend embree --scenario all --copies 1000 --iterations 5 --output-mode compact_summary --output-json /tmp/goal1156_db_batch_profile.json`

Key result:

- Backend: `embree`
- Warm query median: `0.0024431670317426324` seconds for both DB scenarios combined at `copies=1000`
- Row-materializing operations: `0`
- Compact-summary operations represented: `6`
- Run phase mode for both scenarios: `batch_summary`

## Technical Boundary

The current batch contract still dispatches to existing prepared dataset primitives unless a future OptiX shared library exports `rtdl_optix_db_dataset_compact_summary_batch`. The Python runtime can decode that optional native result shape, but the C++ exported symbol is not implemented yet. Therefore this remains a contract and runtime-hook step, not a native OptiX single-launch batch ABI.

## Next Required Work

- Implement the native OptiX prepared DB compact-summary batch ABI behind the new contract.
- Preserve per-request phase counters, plus aggregate traversal/copy/filter/output counters.
- Mirror the ABI in Embree after OptiX so same-semantics baselines remain fair.
- Only then rerun `database_analytics` in the consolidated RTX pod batch.

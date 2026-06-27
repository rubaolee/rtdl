# Goal1157 OptiX DB Compact-Summary Native ABI

Date: 2026-04-30

## Summary

Goal1157 adds the native OptiX C ABI for prepared DB compact-summary batches behind the Goal1156 Python/runtime contract.

This is still a conservative native batch ABI: it executes each requested compact-summary operation through the existing prepared DB helpers and returns one native result array with per-request phase counters. It reduces Python/ctypes round trips and gives the runtime a stable native hook, but it is not yet a shared single-traversal optimization.

## Changes

- Added `RtdlDbCompactSummaryRequest` and `RtdlDbCompactSummaryResult` to `src/native/optix/rtdl_optix_prelude.h`.
- Added operation constants for scan count, grouped count summary, and grouped sum summary.
- Added `rtdl_optix_db_dataset_compact_summary_batch(...)`.
- Added `rtdl_optix_db_compact_summary_results_destroy(...)` with explicit `result_count` so nested grouped rows are freed correctly.
- Wired the Python OptiX runtime to call the optional native symbol when present and fall back to the Goal1156 dispatcher when absent.
- Added static and fake-native tests in `tests/goal1157_optix_db_compact_summary_native_abi_test.py` and `tests/goal1156_db_compact_summary_batch_contract_test.py`.

## Verification

Focused command:

`PYTHONPATH=src:. python3 -m unittest tests.goal1157_optix_db_compact_summary_native_abi_test tests.goal1156_db_compact_summary_batch_contract_test tests.goal954_database_native_continuation_contract_test tests.goal756_db_prepared_session_perf_test -q`

Result: `19 tests OK`.

## Boundary

This was verified locally by static source tests and Python fake-native decoding tests. It has not yet been compiled on a CUDA/OptiX host in this goal. The next pod batch must build `librtdl_optix.so`, confirm the exported symbol is present, run DB compact-summary parity, and compare timings.

No public RTX speedup wording is authorized by this goal.

## Next Work

- Build the updated OptiX backend on an RTX pod.
- Run `database_analytics` compact-summary parity with the native batch symbol present.
- Record whether `query_compact_summary_batch_sec` improves relative to previous OptiX evidence.
- If still slower than Embree, inspect phase counters and decide whether shared predicate traversal is needed.

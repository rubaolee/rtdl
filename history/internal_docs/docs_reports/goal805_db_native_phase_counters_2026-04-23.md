# Goal805: DB Native Phase Counters

## Objective

Add DB-specific native timing/counter evidence so the prepared OptiX DB app can
be judged by phase-clean data in the next batched RTX run. This follows
Goal804's compact summary mode and still does not authorize a broad DB speedup
claim.

## Implementation

- Added C ABI `rtdl_optix_db_get_last_phase_timings(...)`.
- Added public Python probe `rtdsl.get_last_db_phase_timings()`.
- Added `last_phase_timings()` on prepared OptiX DB dataset wrappers.
- Embedded `native_db_phases` in the DB scenario app outputs when the loaded
  backend exports the native counters.
- Updated the prepared DB profiler so cloud artifacts carry
  `reported_native_db_phases_sec`.

## Phase Fields

- `traversal`: OptiX launch plus ray/custom-primitive traversal.
- `bitset_copyback`: GPU candidate bitset copy-back.
- `exact_filter`: native C++ exact predicate filtering after candidate bitset
  discovery.
- `output_pack`: native output packing/sorting/allocation for the requested
  row or scalar output.
- `raw_candidate_count`: row candidates discovered by the RT pass before exact
  filtering.
- `emitted_count`: rows or scalar count emitted for the specific operation.

## Boundaries

- The exact DB filter/group stage remains native host-side C++, not GPU RT-core
  traversal.
- The counters are useful only after the OptiX library is rebuilt from this
  commit on Linux/RTX.
- DB remains `rt_core_partial_ready` until RTX rerun plus independent review
  confirms materialization and host-side phases are no longer dominant for the
  app claim being considered.

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

Result: 33 tests OK
```

```text
python3 -m py_compile \
  src/rtdsl/optix_runtime.py \
  src/rtdsl/__init__.py \
  examples/rtdl_sales_risk_screening.py \
  examples/rtdl_v0_7_db_app_demo.py \
  scripts/goal756_db_prepared_session_perf.py \
  tests/goal804_db_compact_summary_scan_count_test.py

Result: OK
```

```text
git diff --check

Result: OK
```

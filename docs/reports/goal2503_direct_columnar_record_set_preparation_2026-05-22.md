# Goal2503: Direct ColumnarRecordSet Preparation

## Result

Goal2503 promotes the RayDB-style slice from row-mapping compatibility
preparation to direct ColumnarRecordSet preparation for the existing Embree and
OptiX generic columnar payload runtimes.

The new public Python entry points are:

- `rtdsl.prepare_embree_columnar_record_set(record_set, primary_fields=...)`
- `rtdsl.prepare_optix_columnar_record_set(record_set, primary_fields=...)`

Both paths normalize a generic `ColumnarRecordSet` into backend column
descriptors directly. They no longer build `tuple[dict]` row mappings before
calling the backend payload creator.

Focused local validation passed:

- `PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest tests.goal2497_raydb_style_embree_count_sum_parity_test tests.goal2498_raydb_style_optix_count_sum_parity_test tests.goal2499_raydb_style_lowering_plan_test tests.goal2500_raydb_style_backend_matrix_runner_test tests.goal2501_raydb_style_optix_pod_results_test tests.goal2502_raydb_style_benchmark_slice_closeout_test tests.goal2503_direct_columnar_record_set_preparation_test`
- Result: `37 tests OK, 3 skipped`

Fresh OptiX pod validation also passed on `root@69.30.85.198 -p 22017` with
key `~/.ssh/id_ed25519_rtdl_codex`:

- `PYTHONPATH=src:. python3 -m unittest tests.goal2498_raydb_style_optix_count_sum_parity_test tests.goal2499_raydb_style_lowering_plan_test tests.goal2503_direct_columnar_record_set_preparation_test`
- Result: `18 tests OK, 1 skipped`
- App artifact: `docs/reports/goal2503_direct_columnar_optix_app_pod_2026-05-22.json`
- Matrix artifact: `docs/reports/goal2503_direct_columnar_optix_backend_matrix_pod_2026-05-22.json`

## Architecture Boundary

This change does not add native ABI. It reuses the already-generic native
columnar payload symbols:

- `rtdl_embree_columnar_payload_create_from_columns`
- `rtdl_optix_columnar_payload_create_from_columns`
- existing grouped count and grouped sum payload reduction symbols

The engine remains app-agnostic at this layer. The benchmark app still owns its
fixture, predicates, group key, and result-mode selection in Python.

## Updated Lowering Contract

For `embree` and `optix`, `plan_columnar_aggregate_lowering()` now reports:

- `transfer_path = direct_columnar_record_set_to_columnar_payload`
- `uses_compatibility_wrapper = False`
- `materializes_input_rows_for_wrapper = False`
- `direct_columnar_record_set_api = True`
- `true_zero_copy_authorized = False`

This closes the Goal2499/Goal2502 row-mapping gap, but it does not authorize true zero-copy wording.
The runtime still builds backend-owned ctypes column arrays before native
execution.

## Remaining Boundary

Supported native aggregate modes remain count and sum. CPU reference still owns
count, sum, min, max, and `avg_as_sum_count`.

This goal does not claim:

- RayDB reproduction
- SQL or DBMS support
- authors-code comparison
- public speedup
- whole-app acceleration
- true zero-copy
- min/max/avg native support

## Next Target

The next engine target is typed host buffer or partner-resident column handoff.
That is the point where RTDL can start reducing or eliminating another copy
layer for Python+partner+RTDL, while still keeping user Python performance
outside the engine's responsibility boundary.

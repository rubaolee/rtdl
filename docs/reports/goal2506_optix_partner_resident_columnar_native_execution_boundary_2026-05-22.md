# Goal2506 OptiX Partner-Resident Columnar Native Execution Boundary

Date: 2026-05-22

## Summary

Goal2505 finished the descriptor-only partner-resident columnar handoff: CUDA
partner tensors can be represented as RTDL field descriptors without copying
their values into Python row mappings. Goal2506 defines the next native
execution boundary for OptiX and keeps the path fail-closed until the native
device-column ABI exists.

Status: `blocked_pending_optix_device_column_abi`

Required native symbol: `rtdl_optix_columnar_payload_create_from_device_columns`

Current action taken: expose an RTDL requirements packet through
`partner_resident_columnar_native_execution_requirements()` and a per-descriptor
planning gate through `plan_partner_resident_columnar_native_execution(...)`.
The planning gate always returns `native_execution_allowed=False` today.

## Why Native Execution Is Still Blocked

The current OptiX DB/columnar path is not just a thin transfer layer. It is a
host-row-value execution path:

- `RtdlPayloadField` in `src/native/optix/rtdl_optix_prelude.h` accepts host
  pointers such as `const int64_t* int_values` and `const double* double_values`.
- `OptixDbDatasetImpl` in `src/native/optix/rtdl_optix_workloads.cpp` stores
  `std::vector<RtdlDbScalar> row_values`.
- `db_copy_dataset_columnar_payload(...)` copies column values into
  `row_values`.
- `db_collect_candidate_row_indices_optix(...)` performs OptiX candidate
  discovery, then uses host `row_values` for exact predicate filtering.
- `run_db_grouped_count_optix(...)` and `run_db_grouped_sum_optix(...)` perform
  grouped reductions from host `row_values`.

Because of this structure, wiring Goal2505 CUDA pointers directly into the
current native path would either copy the partner-resident table back to host or
produce incorrect semantics. That would violate the claim boundary, so the
correct behavior is to fail closed.

## Required Device-Column ABI

The first native OptiX ABI must describe device-resident columns explicitly
instead of reusing host `RtdlPayloadField`:

- column name
- logical kind
- dtype token
- CUDA device pointer
- row count
- CUDA device id
- contiguous layout contract

The proposed first symbol is:

```c
int rtdl_optix_columnar_payload_create_from_device_columns(...);
```

The exact C struct can be stabilized in the implementation goal, but it must not
hide a full device-to-host table staging step behind a native-execution name.
In particular: do not fall back to hidden device-to-host table staging while
claiming partner-resident native execution.

## First Executable Slice

The safe first native slice should be narrow:

- numeric RayDB-style columns only
- `row_id` dtype `int64` or `uint32`
- data column dtype `int64`, `uint32`, or `float64`
- count and int64 sum aggregates only
- one int64-compatible group key
- device-side exact predicate evaluation
- device-side grouped reduction
- host result materialization only at the API boundary

This slice is intentionally smaller than a SQL engine. It is a primitive-level
RTDL execution path for typed columnar payloads.

## Excluded Scope

The following remain explicitly out of scope until separate implementation and
evidence exist:

- text columns
- bool columns
- min/max/avg aggregates
- SQL or DBMS claims
- whole-app speedup claims
- true zero-copy public claims

## Tests

Focused local validation:

```text
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest tests.goal2506_optix_partner_resident_native_execution_boundary_test
```

Expected result:

```text
4 tests OK
```

The tests check that the native-execution requirements are exported, descriptor
planning does not authorize execution, the current OptiX DB path is still
host-row-value centered, and this report records the required ABI boundary.

Combined RayDB-style local validation through Goal2506:

```text
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest \
  tests.goal2497_raydb_style_embree_count_sum_parity_test \
  tests.goal2498_raydb_style_optix_count_sum_parity_test \
  tests.goal2499_raydb_style_lowering_plan_test \
  tests.goal2500_raydb_style_backend_matrix_runner_test \
  tests.goal2501_raydb_style_optix_pod_results_test \
  tests.goal2502_raydb_style_benchmark_slice_closeout_test \
  tests.goal2503_direct_columnar_record_set_preparation_test \
  tests.goal2504_columnar_typed_host_buffer_handoff_test \
  tests.goal2505_partner_resident_columnar_descriptor_contract_test \
  tests.goal2506_optix_partner_resident_native_execution_boundary_test
```

Observed result:

```text
57 tests OK, 4 skipped
```

## Conclusion

Goal2506 does not implement native partner-resident OptiX execution. It makes
the boundary explicit and test-backed: Goal2505 descriptors are valid metadata,
but native execution is blocked until OptiX gains a real device-column ABI plus
device-side predicate and grouped-reduction execution.

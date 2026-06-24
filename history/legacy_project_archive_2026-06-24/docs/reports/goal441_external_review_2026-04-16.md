# External Review: Goal 441 v0.7 OptiX Columnar Prepared DB Dataset Transfer

Date: 2026-04-16
Reviewer: Claude (external AI, second consensus seat)

## Verdict

**ACCEPT**

No blockers. All Goal 441 requirements are satisfied.

## Evidence Reviewed

- `src/native/optix/rtdl_optix_prelude.h` — C ABI declarations
- `src/native/optix/rtdl_optix_api.cpp` — C ABI implementations
- `src/native/optix/rtdl_optix_workloads.cpp` — `db_validate_columnar_inputs`, `db_copy_dataset_columnar_table`, `create_db_dataset_optix_columnar`
- `src/rtdsl/optix_runtime.py` — Python `transfer="columnar"` opt-in path
- `tests/goal441_v0_7_optix_columnar_prepared_db_dataset_transfer_test.py`
- `docs/reports/goal441_optix_columnar_transfer_perf_linux_2026-04-16.json`
- `docs/reports/goal441_v0_7_optix_columnar_prepared_db_dataset_transfer_2026-04-16.md`
- `docs/reports/goal441_v0_7_optix_columnar_prepared_db_dataset_transfer_review_2026-04-16.md` (Codex review)

## ABI Review

`RtdlDbColumn` is correctly defined in `rtdl_optix_prelude.h` with `name`, `kind`, `int_values`,
`double_values`, and `string_values`. The new export `rtdl_optix_db_dataset_create_columnar` matches
the signature declared in the prelude and is properly implemented in `rtdl_optix_api.cpp` — it
delegates to `create_db_dataset_optix_columnar` in the workloads file and wraps it in the standard
`handle_native_call` error-handling envelope, consistent with every other C ABI entry point in the
file.

The existing row-struct ABI (`rtdl_optix_db_dataset_create`) is unchanged. Both entry points
resolve to the same `OptixDbDatasetImpl*` opaque type, so all downstream query functions
(`db_dataset_conjunctive_scan`, `db_dataset_grouped_count`, `db_dataset_grouped_sum`) are shared
without modification — correct.

## Native Columnar Ingestion

`db_copy_dataset_columnar_table` (workloads.cpp:439–480) transposes the column-major input back
into the row-major `RtdlDbScalar` layout that all existing query helpers expect. String ownership is
handled via `scalar_strings` storage — same pattern as the row-struct path. `db_validate_columnar_inputs`
(workloads.cpp:411–437) validates null guards and the 1 M row cap before any allocation, consistent
with `db_validate_db_inputs` on the row path.

## Python Transfer Path

`PreparedOptixDbDataset.__init__` (optix_runtime.py:839–868) correctly:

1. Rejects any `transfer` value outside `{"row", "columnar"}` before reaching the native layer.
2. On `transfer="columnar"`, calls the shared `_encode_db_table_columnar` (imported from
   `embree_runtime`) to build the ctypes column array, then forwards it to
   `OptixPreparedDbDataset` with `columns_array` and `column_count=len(columns_array)`.
3. On `transfer="row"`, follows the existing path unchanged.
4. Guards against an older .so that does not export `rtdl_optix_db_dataset_create_columnar`, with a
   clear rebuild message.

The `column_count` calculation (`len(columns_array) if columns_array is not None else None`) is
correct; ctypes array types support `len()`.

## Test Coverage

Four tests, all necessary:

- `test_columnar_conjunctive_scan_matches_row_transfer_and_python_truth` — row parity and Python
  truth for `conjunctive_scan`
- `test_columnar_grouped_count_matches_row_transfer_and_python_truth` — row parity and Python
  truth for `grouped_count`
- `test_columnar_grouped_sum_matches_row_transfer_and_python_truth` — row parity and Python truth
  for `grouped_sum`
- `test_invalid_transfer_mode_rejected` — ValueError on unrecognised transfer string

Linux native result: `Ran 4 tests — OK`.

## Linux Prepare-Time Gate

JSON artifact is consistent with the report table:

| Workload | Row median (s) | Columnar median (s) | Speedup |
|---|---:|---:|---:|
| `conjunctive_scan` | 2.7024 | 0.7996 | 3.38x |
| `grouped_count` | 2.6093 | 0.7959 | 3.28x |
| `grouped_sum` | 2.5096 | 0.7908 | 3.17x |

Five-sample variance is tight (< 4 % spread) for both paths. Speedup is material and plausible:
the columnar path avoids per-cell branching and pointer indirection during struct packing, which is
the dominant cost at 200 k rows. Output row counts (22 268 for conjunctive_scan, 8 for the grouped
workloads) are internally consistent with the bounded test dataset's group cardinality.

Row hashes match the previously established DB truth hashes, confirming correctness is not
compromised by the faster transfer path.

## Claim Boundary Check

The implementation is correctly scoped as an ingestion-path improvement:

- Vulkan columnar transfer is explicitly deferred to a follow-up goal.
- No DBMS / arbitrary-SQL boundary has been crossed.
- The row-struct ABI is preserved, so existing callers are unaffected.

## Blockers

None.

## Summary

Goal 441 delivers the OptiX columnar prepared DB dataset transfer path following the established
Goal 440 Embree pattern. The C ABI, native ingestion logic, Python opt-in path, test coverage, and
Linux prepare-time evidence are all present and correct. The claim boundary is maintained. ACCEPT.

# External Review: Goal 442 v0.7 Vulkan Columnar Prepared DB Dataset Transfer

Date: 2026-04-16
Reviewer: Claude Sonnet 4.6 (external AI, second reviewer)

## Verdict

**ACCEPT**

No release-blocking issues found. Goal 442 is correctly scoped, fully
implemented, and backed by passing tests and Linux prepare-time evidence.

## Evidence Reviewed

- `src/native/vulkan/rtdl_vulkan_prelude.h` — ABI declarations
- `src/native/vulkan/rtdl_vulkan_api.cpp` — C ABI entry points
- `src/native/vulkan/rtdl_vulkan_core.cpp` — native implementation
- `src/rtdsl/vulkan_runtime.py` — Python opt-in transfer path
- `tests/goal442_v0_7_vulkan_columnar_prepared_db_dataset_transfer_test.py`
- `docs/reports/goal442_vulkan_columnar_transfer_perf_linux_2026-04-16.json`
- `docs/reports/goal442_v0_7_vulkan_columnar_prepared_db_dataset_transfer_2026-04-16.md`
- `docs/reports/goal442_v0_7_vulkan_columnar_prepared_db_dataset_transfer_review_2026-04-16.md`
  (first AI review, Codex — ACCEPT)

## C ABI

`RtdlDbColumn` is declared in `rtdl_vulkan_prelude.h` with the correct layout
(name, kind, int_values, double_values, string_values).
`rtdl_vulkan_db_dataset_create_columnar` is declared in the prelude and
implemented in `rtdl_vulkan_api.cpp` delegating to
`create_db_dataset_vulkan_columnar` in `rtdl_vulkan_core.cpp`.

The existing row-struct ABI (`rtdl_vulkan_db_dataset_create`) is untouched.
Both paths coexist.

## Native Implementation

`db_validate_columnar_inputs` (core.cpp:3077) validates that column pointers
are non-null, row_count is within the 1M-row limit, and each column carries
the expected value pointer for its kind (text vs. numeric).

`db_copy_dataset_columnar_table` (core.cpp:3107) transposes column-major input
into the row-major internal `row_values` vector — the same format used by the
row-struct path — so all downstream AABB construction, BLAS, and TLAS code is
shared without modification.

`create_db_dataset_vulkan_columnar` (core.cpp:4387) handles primary-field
selection, axis construction, row-meta and AABB generation, and then builds
BLAS and TLAS using the same helpers as the row path.  No new code paths for
query execution — only the ingestion differs.

## Python Path

`vulkan_runtime.py` imports `_RtdlDbColumn` and `_encode_db_table_columnar`
from `embree_runtime` (the same helpers introduced in Goals 440 and 441).

`PreparedVulkanDbDataset.__init__` (line 734) validates `transfer in {"row",
"columnar"}` and raises `ValueError` for anything else.  When
`transfer="columnar"`, it calls `_encode_db_table_columnar` to produce
column arrays, then passes them to `VulkanPreparedDbDataset` with the
`transfer="columnar"` flag.

`VulkanPreparedDbDataset.__init__` (line 591) branches on the flag: columnar
calls `rtdl_vulkan_db_dataset_create_columnar`, row calls
`rtdl_vulkan_db_dataset_create`.  A runtime guard checks that the symbol
exists and raises a helpful message if the binary is stale.

The `argtypes` for `rtdl_vulkan_db_dataset_create_columnar` are registered
correctly in `_register_argtypes` (line 1586).

The public entry point `prepare_vulkan_db_dataset` defaults to
`transfer="row"`, so existing callers are unaffected.

## Tests

Four tests in the test file:

| Test | Coverage |
|---|---|
| `test_columnar_conjunctive_scan_matches_row_transfer_and_python_truth` | parity for conjunctive_scan |
| `test_columnar_grouped_count_matches_row_transfer_and_python_truth` | parity for grouped_count |
| `test_columnar_grouped_sum_matches_row_transfer_and_python_truth` | parity for grouped_sum |
| `test_invalid_transfer_mode_rejected` | ValueError on invalid mode |

Each parity test creates both a row-transfer and a columnar-transfer dataset,
runs the workload on both, and asserts equality against the Python reference.
Coverage is complete for the three bounded DB workloads.

Linux result: 4 tests, OK.

## Linux Prepare-Time Evidence

JSON at `docs/reports/goal442_vulkan_columnar_transfer_perf_linux_2026-04-16.json`
records 5-repeat results at 200k input rows:

| Workload | Row median (s) | Columnar median (s) | Speedup |
|---|---:|---:|---:|
| `conjunctive_scan` | 2.761 | 0.821 | 3.36x |
| `grouped_count` | 2.708 | 0.846 | 3.20x |
| `grouped_sum` | 2.623 | 0.852 | 3.08x |

Speedups of 3x+ are consistent with the pattern seen in Goals 440 and 441 for
Embree and OptiX.  Result hashes are recorded and match the upstream DB truth
hashes cited in the implementation report.

Note: the JSON `row_count` fields for `grouped_count` and `grouped_sum` reflect
result cardinality (8 rows), not input cardinality.  The `input_row_count` field
correctly records 200000.  This is an internal reporting convention, not a data
integrity issue.

## Boundary Check

Goal 442 is strictly an ingestion-path improvement.  The DBMS boundary is
preserved: no arbitrary SQL, no joins as first-class features, no PostgreSQL
indexing claims.  The goal text, implementation report, and Codex review all
state this clearly.

## Consensus

- First AI (Codex): ACCEPT
- This review (Claude Sonnet 4.6): ACCEPT

2-AI consensus reached. Goal 442 may be closed.

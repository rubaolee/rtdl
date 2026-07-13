# Goal4947 - LSI Pair Columns To Numba Execution

## Verdict Requested

`complete_lsi_pair_columns_to_numba_capability_no_performance_claim`

## Goal

Prove the Layer 1/2 bridge for the LSI side:

```text
native segment-pair/LSI device columns
-> generic device-column row buffer
-> existing Numba segmented-count continuation
```

This goal is a capability/execution gate only. It is not a RayJoin app-level
performance measurement and it does not authorize any speedup claim.

## What Changed

1. `run_numba_segmented_count_i64(...)` now accepts CUDA array-interface
   columns through the same `_as_numba_cuda_vector(...)` path already used by
   newer Numba continuations.
2. Added a focused Goal4947 test file:
   `tests/goal4947_lsi_pair_columns_numba_handoff_test.py`.
3. Added a POD probe script:
   `history/internal_docs/goal4947_lsi_pair_columns_to_numba_pod_probe.py`.
4. Recorded the POD artifact:
   `history/internal_docs/goal4947_lsi_pair_columns_to_numba_pod_artifact_2026-07-04.json`.

## Why The Code Change Was Needed

The row-buffer carrier exposes native CUDA columns through
`RtdlRawCudaColumn.__cuda_array_interface__`. Newer Numba operations already
convert those columns with `_as_numba_cuda_vector(...)`.

The older `segmented_count_i64` path still called `_validate_numba_cuda_vector`
directly, so it rejected a valid RTDL row-buffer column with:

```text
ValueError: group_ids must be a Numba CUDA device array
```

Goal4947 fixed that generic partner-interface inconsistency. The operation
semantics did not change.

## POD Runtime Evidence

Hardware runtime used the existing POD checkout at `/root/rtdl_goal4937`.

Focused CUDA tests:

```text
python3 -m unittest \
  tests.goal4947_lsi_pair_columns_numba_handoff_test \
  tests.goal4946_native_device_columns_numba_execution_test

Ran 9 tests in 0.712s
OK
```

Native LSI fixture:

```text
right segments: 3 vertical segments
left segments: 4 horizontal segments
expected left-id counts: [1, 1, 2, 0]
```

POD artifact summary:

```json
{
  "schema": "rtdl.goal4947.lsi_pair_columns_to_numba.v1",
  "row_count": 4,
  "columns": ["left_id", "right_id"],
  "device_resident_candidate": true,
  "native_device_column_output_proven_on_hardware": true,
  "host_rows_materialized_before_partner_handoff": false,
  "partner_packet_status": "accept",
  "torch_conversion_used": false,
  "numba_operation": "segmented_count_i64",
  "counts": [1, 1, 2, 0],
  "expected_counts": [1, 1, 2, 0],
  "counts_match": true
}
```

## Local Test Evidence

```text
$env:PYTHONPATH='src'
py -m unittest \
  tests.goal4947_lsi_pair_columns_numba_handoff_test \
  tests.goal4946_native_device_columns_numba_execution_test \
  tests.goal4942_device_column_row_buffer_handoff_test

Ran 17 tests in 0.009s
OK (skipped=3)
```

I also attempted to include the old Goal2875 conformance test, but it is not a
valid current gate because it depends on archived `docs/reports` files and an
older conformance matrix assumption:

```text
ValueError: preview conformance row is not classified:
triton/adjacent_midpoint_candidates_i64x2_by_key
FileNotFoundError: docs/reports/goal2875_numba_runtime_conformance_smoke_2026-05-31.md
```

That failure is recorded as historical-test drift, not as a Goal4947 failure.

## Boundaries

Authorized:

- Generic segment-pair/LSI native device columns can enter the Layer 1 row
  buffer.
- The row-buffer column can be consumed by the existing Numba segmented-count
  continuation.
- No CuPy dependency is required for this path.

Not authorized:

- No RayJoin app-level performance claim.
- No whole-app speedup claim.
- No true-zero-copy public claim.
- No claim that Goal4947 moved the RayJoin hot path.
- No Layer 3 writer/output-assembly work.

## Next Goal

Goal4948 should prove the same row-buffer/Numba machinery on a useful
non-RayJoin workload, not merely with a foreign column or toy connector.

Goal4949 remains the first RayJoin-relevant performance gate and must measure
real hot-path continuations such as reprojection/sort/dedupe/midpoint work,
not generic demo operations.

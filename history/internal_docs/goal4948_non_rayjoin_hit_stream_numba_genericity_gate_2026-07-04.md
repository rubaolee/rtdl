# Goal4948 - Non-RayJoin Row-Buffer/Numba Genericity Gate

## Verdict Requested

`complete_non_rayjoin_row_buffer_numba_genericity_gate_no_performance_claim`

## Goal

Prove that the Layer 1/2 row-buffer plus Numba path is not only an LSI/RayJoin
shape. The gate uses a structurally different spatial workload:

```text
OptiX 3D ray/triangle hit stream device columns
-> generic device-column row buffer
-> Numba segmented-count continuation
-> per-ray hit counts
```

This is a useful non-RayJoin operation: counting hit-stream rows per ray from a
generic ray/triangle primitive. It is not merely a foreign-column connector and
does not exercise RayJoin, planar-map LSI, PIP, polygon overlay, or output-chain
logic.

## Files Added

- `tests/goal4948_non_rayjoin_hit_stream_numba_genericity_test.py`
- `history/internal_docs/goal4948_non_rayjoin_hit_stream_numba_pod_probe.py`
- `history/internal_docs/goal4948_non_rayjoin_hit_stream_numba_pod_artifact_2026-07-04.json`

No RTDL runtime code was changed for Goal4948. It reuses:

- `device_column_row_buffer_from_hit_stream_handoff(...)`
- `PreparedOptixStaticTriangleScene3D.ray_triangle_hit_stream_device_columns(...)`
- `run_numba_segmented_count_i64(...)`

## POD Runtime Evidence

POD focused tests:

```text
python3 -m unittest \
  tests.goal4948_non_rayjoin_hit_stream_numba_genericity_test \
  tests.goal4947_lsi_pair_columns_numba_handoff_test \
  tests.goal4946_native_device_columns_numba_execution_test

Ran 11 tests in 1.022s
OK
```

POD probe fixture:

```text
3 rays:
  ray 0 hits triangles 0 and 1
  ray 1 hits triangle 2
  ray 2 hits nothing

expected per-ray counts: [2, 1, 0]
```

Artifact summary:

```json
{
  "schema": "rtdl.goal4948.non_rayjoin_hit_stream_numba.v1",
  "row_count": 3,
  "columns": ["ray_ids", "primitive_ids"],
  "device_resident_candidate": true,
  "native_device_column_output_proven_on_hardware": true,
  "host_rows_materialized_before_partner_handoff": false,
  "numba_operation": "segmented_count_i64",
  "counts": [2, 1, 0],
  "expected_counts": [2, 1, 0],
  "counts_match": true
}
```

## Local Test Evidence

```text
$env:PYTHONPATH='src'
py -m unittest \
  tests.goal4948_non_rayjoin_hit_stream_numba_genericity_test \
  tests.goal4947_lsi_pair_columns_numba_handoff_test \
  tests.goal4946_native_device_columns_numba_execution_test

Ran 11 tests in 0.007s
OK (skipped=4)
```

## Genericity Boundary

This gate proves a second producer family:

| Producer | Columns | Consumer | App identity |
|---|---|---|---|
| segment-pair/LSI candidate columns | `left_id`, `right_id` | Numba segmented count | none |
| ray/triangle hit-stream columns | `ray_ids`, `primitive_ids` | Numba segmented count | none |

The second line is the Goal4948 evidence. It is structurally different from
RayJoin: 3D ray/triangle hit rows, not 2D planar-map LSI/PIP/overlay rows.

## Claim Boundary

Authorized:

- The same row-buffer/Numba machinery works on a useful non-RayJoin spatial
  workload.
- The bridge executes without host row materialization before partner handoff.

Not authorized:

- No public speedup claim.
- No whole-app acceleration claim.
- No true-zero-copy public claim.
- No RayJoin hot-path movement claim.
- No Layer 3 writer/output-assembly claim.

## Next Goal

Goal4949 can now perform the first RayJoin-relevant hot-path measurement. Per
Claude's AM1, it must target real RayJoin continuation phases such as
reprojection/sort/dedupe/midpoint work. It must not use demo operations like
`uint32_equal_mask` or unrelated segmented counts as a proxy for RayJoin
performance.

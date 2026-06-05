# Goal3394 - OptiX Exact Membership Device Columns Bridge

Date: 2026-06-04

Verdict: accept-with-boundary.

## Purpose

Goal3390 showed that first-boundary-event reconstruction fails at 4096 chains.
Goal3391/3392 gave users a Python/CuPy bridge over exact host-refined rows.

Goal3394 moves that bridge into the OptiX runtime ABI:

```text
rtdl_optix_prepared_point_closed_shape_membership_exact_device_columns_2d
```

The symbol uses the existing exact host-refined membership implementation, then
uploads exact `(point_id, shape_id)` pairs into native-owned CUDA device columns.
This avoids Python row materialization for partner continuations while staying
honest that the exact predicate is not yet device-only.

## Evidence

Build:

```text
make build-optix
```

passed on the RTX A5000 pod and produced `build/librtdl_optix.so`.

Live probe artifact:
`docs/reports/goal3394_optix_exact_membership_device_columns_live_probe_2026-06-04.json`

Source commit:
`3b09c58ab9750df289f4991437803bd67f8f5a53`

## Result

| Measure | Value |
| --- | ---: |
| Chains | 4096 |
| Shapes | 3762 |
| Exact host-refined rows | 11316 |
| Native exact device-column rows | 11316 |
| Exact relation row-count alias | 11316 |
| Missing exact pairs | 0 |
| Extra pairs | 0 |
| Device resident | true |
| Overflow | false |
| Native bridge seconds | 0.001629 |

The live probe compared `prepared.run(points)` against
`prepared.exact_device_columns(points).as_cupy_columns()` and found exact pair
identity.

## Metadata Boundary

The typed stream is now labeled as:

```text
stream_id = point_closed_shape_membership_2d_exact_device_columns
stream_kind = exact_relation_stream
producer_primitive = point_closed_shape_membership_2d_exact_host_refined
output_residency = device_resident_exact_id_columns
```

The implementation boundary remains explicit:

```text
host_refined_exact_rows_inside_native_bridge = true
native_exact_device_row_stream_produced = true
device_only_exact_predicate_produced = false
true_zero_copy_claim_authorized = false
exact_relation_row_count = 11316
legacy_pair_column_count_field = candidate_event_count
capacity = 11316
```

## Boundary

This does not authorize release, public speedup, RayJoin paper reproduction,
RTDL-beats-RayJoin, RT-core speedup, true-zero-copy, or native default-route
claims.

The next performance step is to remove the host-refinement phase by implementing
a robust device-side exact relation predicate or a richer relation-witness
stream that can be consumed by a partner without host materialization.

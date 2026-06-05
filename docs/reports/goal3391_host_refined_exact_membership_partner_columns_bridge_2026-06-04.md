# Goal3391 - Host-Refined Exact Membership Partner Columns Bridge

Date: 2026-06-04

Verdict: accept-with-boundary.

## Purpose

Goal3390 showed that first-boundary-event columns are not rich enough to
reconstruct exact closed-shape membership at a 4096-chain CDB slice. The exact
RTDL/OptiX path still exists, but today it returns host rows after exact
refinement.

Goal3391 adds a small bridge for users and benchmark apps:

```python
rt.materialize_closed_shape_membership_rows_as_cupy_columns(rows)
```

It uploads exact membership rows into CuPy columns so a partner continuation can
consume them without each app reimplementing row parsing and upload logic.

## Contract

Inputs:

- exact membership rows exposing `point_id`/`shape_id`, or generic
  `left_id`/`right_id`;
- optional `membership`, defaulting to `1`;
- optional `source_protocol`, defaulting to `host_refined_exact_rows`.

Outputs:

- `point_id` CuPy column;
- `shape_id` CuPy column;
- `membership` CuPy column;
- row count and claim-boundary metadata.

The output metadata explicitly states:

```text
output_residency = partner_device_after_host_refine_upload
host_refined_rows_materialized = true
native_exact_device_row_stream_produced = false
true_zero_copy_claim_authorized = false
```

## Why This Is Useful

This bridge is not the final high-performance primitive. It is still useful
because it gives user code a consistent partner-column shape for exact relation
rows:

```python
prepared = rt.prepare_point_closed_shape_membership_2d_optix(shapes)
rows = prepared.run(points)
columns = rt.materialize_closed_shape_membership_rows_as_cupy_columns(rows)
```

After that, app code can use ordinary CuPy/partner reductions over
`columns["point_id"]`, `columns["shape_id"]`, and `columns["membership"]`.

## Boundary

This bridge does not authorize release, public speedup, RT-core speedup,
true-zero-copy, native default route, or RayJoin paper reproduction claims.

The next real performance primitive remains a generic exact closed-shape relation stream that emits exact relation columns directly from the native backend, or emits enough robust relation evidence for a partner to decide exact membership without host materialization.

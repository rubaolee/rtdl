# Goal3392 - Exact Membership Bridge Live Probe

Date: 2026-06-04

Verdict: accept-with-boundary.

## Purpose

Goal3391 added a bounded bridge that uploads exact host-refined membership rows
into CuPy columns. Goal3392 validates that bridge on the same 4096-chain CDB
slice where the first-boundary-event route failed in Goal3390.

## Evidence

Artifact:
`docs/reports/goal3392_exact_membership_bridge_live_probe_2026-06-04.json`

Pod: NVIDIA RTX A5000, driver 580.126.09

Source commit:
`d7c7f92d7024e8f327add0b0b61b88b9b2dfe88a`

## Result

| Measure | Value |
| --- | ---: |
| Chains | 4096 |
| Shapes | 3762 |
| Exact RTDL/OptiX rows | 11316 |
| Bridge CuPy rows | 11316 |
| Missing exact pairs | 0 |
| Extra pairs | 0 |
| Exact pair match | true |
| Exact run seconds | 0.026099 |
| Bridge upload seconds | 0.067060 |

The bridge preserves every exact `(point_id, shape_id)` pair in partner-device
columns.

## Boundary

This is a correctness and usability bridge, not the final performance primitive.

The artifact explicitly records:

```text
output_residency = partner_device_after_host_refine_upload
host_refined_rows_materialized = true
native_exact_device_row_stream_produced = false
true_zero_copy_claim_authorized = false
```

This does not authorize release, public speedup, RayJoin paper reproduction,
RTDL-beats-RayJoin, RT-core speedup, true-zero-copy, or native default-route
claims.

## Interpretation

Users can now write a correct partner continuation over exact closed-shape
membership rows without rebuilding row-upload plumbing in every app. The next
performance target is still a native exact closed-shape relation stream or an
equivalent robust relation-witness stream that avoids host refinement and
re-upload.

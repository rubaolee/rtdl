# Goal3271 Closed-Shape Membership Point-ID Count Device Columns

Date: 2026-06-03

Status: implemented with local source gates and pod build/smoke evidence.

## Purpose

Goal3269 added a generic device-resident point/shape candidate stream for
prepared closed-shape membership. Goal3271 adds the first direct generic
device-side continuation over the same RT traversal: count positive memberships
by caller point ID and keep the dense count column on the device.

This targets the main RayJoin lesson without adding RayJoin-specific engine
logic: users need a way to continue from RT traversal results on device instead
of materializing candidate pair rows on the host.

## What Changed

New native OptiX C ABI:

- `rtdl_optix_prepared_point_closed_shape_membership_point_id_count_device_columns_2d`

New Python runtime front door:

- `PreparedOptixPointClosedShapeMembership2D.point_id_count_device_columns(points, group_capacity=...)`

Output:

- `OptixNativeDeviceGroupedCountI64Output`
- device-resident grouped count column
- keyed by caller point ID
- direct-address `group_capacity` semantics

## Boundary

This is a generic closed-shape membership continuation. It is not a RayJoin
native kernel. No candidate pair array is materialized, and no host-refined
membership rows are produced by this path. In exact gate wording:
no candidate pair array is materialized.

Claim flags:

- release authorized: false
- public speedup claim authorized: false
- RT-core speedup claim authorized: false
- true zero-copy claim authorized: false
- RayJoin-specific native logic added: false

## Why This Matters

The previous RayJoin PIP probes showed that small micro-optimizations were not
enough. The larger missing primitive is device-resident continuation after RT
candidate discovery or device predicate evaluation.

Goal3271 provides one such continuation:

1. RT traversal and the generic closed-shape predicate identify positive
   memberships.
2. The any-hit path increments a dense device count column indexed by caller
   point ID.
3. Downstream partners or later native continuations can consume that count
   column without first receiving host materialized candidate rows.

## Validation

Local validation:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal3271_closed_shape_membership_point_id_count_device_columns_test \
  tests.goal3269_closed_shape_membership_candidate_device_columns_test
```

Result: 10 tests passed locally.

Pod validation:

```text
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
  python3 -m unittest \
    tests.goal3271_closed_shape_membership_point_id_count_device_columns_test \
    tests.goal3269_closed_shape_membership_candidate_device_columns_test
```

Result: OptiX build passed and the same 10-test focused slice passed on the pod.

Live smoke artifact:

- `docs/reports/goal3271_pod_closed_shape_point_id_count_device_columns_smoke_2026-06-03.json`

Live smoke result:

- exact device-filtered count: `2`
- source row count: `2`
- dense count output is device resident: `true`
- overflow: `false`
- group capacity: `64`
- selected counts after CuPy wrapping: `10 -> 1`, `20 -> 1`, `30 -> 0`
- metadata schema: `device_grouped_count_i64_dense_columns`
- metadata output residency: `device_resident_dense_grouped_count_column`

The selected-count check proves this continuation is keyed by caller point ID.

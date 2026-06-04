# Goal3269 Closed-Shape Membership Candidate Device Columns

Date: 2026-06-03

Status: implemented locally; pod build/timing evidence still pending.

## Purpose

Goal3266 and Goal3267 showed that the next RayJoin-side improvement is not a
small boundary-mode or scalar-layout micro-probe. The missing substrate is a
generic device-resident stream between RT traversal and continuation logic.

This goal adds the first narrow substrate piece for closed-shape membership:
device-resident point/shape candidate ID columns produced by the prepared OptiX
closed-shape membership primitive.

## What Changed

New native OptiX C ABI:

- `rtdl_optix_prepared_point_closed_shape_membership_candidate_device_columns_2d`
- `rtdl_optix_release_point_closed_shape_membership_candidate_device_columns_2d`

The output uses the existing generic `RtdlNativeDevicePairColumns` shape. For
this producer, the left column is `point_id` and the right column is `shape_id`.

New Python runtime front door:

- `PreparedOptixPointClosedShapeMembership2D.candidate_device_columns(points, max_rows=None)`

New typed stream metadata:

- `point_closed_shape_membership_2d_candidate_device_columns`
- producer primitive: `point_closed_shape_membership_2d_candidate`
- output residency: `device_resident_candidate_id_columns`

## Boundary

These are device-resident point/shape candidate ID columns, not exact
host-refined membership rows. In short: not exact host-refined membership rows.
The path writes caller point IDs and shape IDs directly from the RT traversal
any-hit path, but it does not yet expose a
generic device-side continuation that can complete grouped predicates or richer
reductions.

Claim flags:

- release authorized: false
- public speedup claim authorized: false
- RT-core speedup claim authorized: false
- true zero-copy claim authorized: false
- RayJoin-specific native logic added: false

This goal does not authorize a release claim.
This goal does not authorize a true zero-copy claim.
It is a substrate step toward a device-resident continuation.

## Why This Is App-Agnostic

The native surface uses generic geometry vocabulary:

- point
- closed shape
- membership
- candidate device columns

No RayJoin query names, dataset names, or application-specific join semantics are
encoded in the native ABI or kernel path.

## Next Step

The next step is a generic device-side continuation over this stream: for
example, grouped count / parity / predicate accumulation over `point_id` or
`shape_id` without materializing candidate rows on the host.

That next step is where a RayJoin-level performance improvement could appear.
Goal3269 only establishes the device-resident candidate stream needed for that
work.

## Validation

Local validation target:

```text
PYTHONPATH=src;. py -3 -m unittest tests.goal3269_closed_shape_membership_candidate_device_columns_test
```

Pod validation target:

```text
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
  python3 -m unittest tests.goal3269_closed_shape_membership_candidate_device_columns_test
```

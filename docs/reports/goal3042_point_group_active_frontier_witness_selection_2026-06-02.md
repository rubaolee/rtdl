# Goal3042 Point-Group Active-Frontier Witness Selection

Date: 2026-06-02

Status: source landed; pod timing pending.

## Purpose

Goal3040 showed that writing all nearest-witness columns and then reducing them
with Numba is correct, but not fast enough for the Hausdorff benchmark. The
main cost is not the final argmax alone: it is that the current exact RT path
still makes too many query rows survive to the continuation phase.

Goal3042 adds the next generic primitive needed for the X-HD-style direction:
a device-resident active frontier over prepared point groups. The primitive is
not Hausdorff-specific. It combines:

- a point/group threshold pass over query points,
- an active mask that stays inside the native/device path,
- a nearest-witness pass that skips inactive queries,
- a generic max-distance reduction that returns only one witness row and one
  active-count scalar to Python.

## Native Contract

New OptiX export:

```text
rtdl_optix_reduce_prepared_point_group_nearest_max_distance_active_frontier_2d
```

Inputs:

- prepared point-group nearest-witness scene,
- query points,
- threshold radius,
- threshold count,
- witness radius.

Outputs:

- one `RtdlFixedRadiusNeighborRow`,
- one active-query count.

The native names stay generic: point group, threshold, active frontier, nearest
witness, max-distance reduction. The native implementation does not contain
Hausdorff, X-HD, or application-specific ABI names.

## Python Contract

`PreparedOptixPointGroupNearestWitness2D` now exposes:

```python
nearest_max_distance_active_frontier_row(
    query_points,
    threshold_radius=...,
    threshold=1,
    witness_radius=...,
)
```

The returned dictionary includes:

- `query_id`,
- `neighbor_id`,
- `distance`,
- `active_count`,
- `native_reduction = "point_group_nearest_max_distance_active_frontier"`,
- `materializes_frontier_on_host = False`.

This is not a true-zero-copy claim. Query points are still packed on the host
for this path. The bounded claim is only that the threshold-derived active
frontier is not materialized back to Python before nearest-witness reduction.

## Hausdorff App Wiring

The Hausdorff research benchmark adds:

```text
rtdl_rt_grouped_active_frontier_nearest_witness
```

The app-level strategy is:

1. Build generic uniform point groups over the target set.
2. Run a seed sample exact nearest-witness reduction to get a lower-bound
   witness distance.
3. Use `threshold_radius = seed_distance - margin`.
4. Ask the native active-frontier primitive to skip source points that already
   have a witness within that threshold radius.
5. Compare the reduced active-frontier witness with the seed witness and return
   the exact directed Hausdorff witness for that direction.

This remains app-level Python orchestration over generic native primitives.

## User-Facing Lab Changes

The multi-method language lab now lists
`rtdl_rt_grouped_active_frontier_nearest_witness` and exposes:

- `--seed-sample-count`
- `--target-points-per-group`

Those knobs are important. If the seed sample is larger than the point set, the
method intentionally falls back to the full reduced nearest-witness path.

## Claim Boundary

- `v2_6_release_authorized`: false.
- Public speedup claim: false.
- RT-core speedup claim: false.
- True-zero-copy claim: false.
- App-specific native-engine logic: false.

The next required step is an OptiX pod build and large same-contract timing
run against the current CuPy grouped-grid reference and the current RT raw-row
reference.

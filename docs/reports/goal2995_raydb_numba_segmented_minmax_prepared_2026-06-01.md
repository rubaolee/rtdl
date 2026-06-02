# Goal2995: RayDB-Style Numba Segmented Min/Max Prepared

Date: 2026-06-01

Status: prepared for pod validation.

## Purpose

Goal2994 proved that the first v2.6 benchmark-app demonstrator can route a
RayDB-style grouped aggregate through user-selected `partner="numba"` using the
neutral partner handoff, but it intentionally covered only `count`, `sum`, and
`avg_as_sum_count`.

Goal2995 closes the next generic primitive gap for this app family:

- `segmented_min_f64`
- `segmented_max_f64`

These operations are generic grouped reductions over `group_ids:int64` and
`values:float64`. They are not RayDB-specific native engine functions, do not
replace RT traversal, and do not authorize any speedup or release claim.

## Implementation

The implementation adds Numba CUDA continuation support beside the existing
count/sum path:

- `describe_numba_segmented_min_f64`
- `describe_numba_segmented_max_f64`
- `run_numba_segmented_min_f64`
- `run_numba_segmented_max_f64`

The generic partner front doors now accept `partner="numba"` for:

- `partner_group_min_by_key`
- `partner_group_max_by_key`

Both paths require the v2.6 neutral partner handoff to accept runtime-observed
device-resident columns before any Numba kernel is launched. Host NumPy arrays are rejected before CUDA execution, matching the Goal2990/Goal2994 boundary.

## RayDB-Style App Effect

The RayDB-style v2.6 Numba demonstrator now supports all five scalar aggregate modes:

- `count`
- `sum`
- `min`
- `max`
- `avg_as_sum_count`

The app remains app-level Python lowering over generic RTDL primitives. The
engine still sees only generic group ids and payload values.

## Pod Runner

Prepared runner:

`scripts/goal2995_raydb_numba_minmax_pod_runner.py`

The runner validates all five modes against CPU NumPy references over large
device-resident columns. The min/max proof uses dense per-group outputs with
`inf` and `-inf` sentinels for empty groups.

## Boundaries

This goal does not authorize:

- v2.6 release
- public speedup claims
- whole-app speedup claims
- broad RT-core speedup claims
- true zero-copy claims
- RayDB paper reproduction claims
- automatic partner selection claims

It only prepares and locally validates the generic Numba min/max continuation
path. CUDA pod evidence is still required before the goal can be marked as a
runtime conformance pass.

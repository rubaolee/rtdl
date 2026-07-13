# Goal4977: Fast Scaled-Point Host Pack Route

Date: 2026-07-04

## Purpose

Goal4976 showed that midpoint generation is not math-bound. It is dominated by host packing into `RtdlRayjoinCdbScaledPoint`:

- map0: `pack_scaled_points` 0.683992s, 97.96%
- map1: `pack_scaled_points` 0.606735s, 98.80%

Goal4977 implements the lowest-risk fix first: a vectorized host pack route that preserves the same ABI but avoids per-row Python object construction.

## Boundary

Allowed:

- Add a generic fast pack helper for the existing `RtdlRayjoinCdbScaledPoint` ABI.
- Use a NumPy structured array with a ctypes view, with the NumPy array retained as owner.
- Add an app flag to choose the fast pack route for midpoint query points.
- Compare against the Goal4976 decomposition route.

Forbidden:

- No native/core point-location semantic change.
- No RayJoin overlay logic in core.
- No zero-copy claim.
- No author-performance headline.

## Verification

The result must report:

- local parity tests for old pack vs fast pack
- POD top4 timing comparison
- whether `pack_scaled_points` moved materially
- whether downstream summaries remain identical

## Exit Labels

- `completed_fast_scaled_point_pack_moves_midpoint_floor`
- `completed_fast_scaled_point_pack_no_perf_win`
- `fail_redo_due_to_pack_layout_or_lifetime_risk`

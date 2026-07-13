# Goal4976: Midpoint Generation Downstream Floor Decomposition

Date: 2026-07-04

## Purpose

After Goal4974, PIP row materialization is no longer the largest downstream cost. The top4 RayJoin binary route now shows the largest persistent downstream phases as:

- `midpoint_points_map0_columnar_sec` around 0.69s
- `midpoint_points_map1_columnar_sec` around 0.60s
- `grouped_compiled_columnar_carrier_construction_sec` around 0.59s

Goal4976 starts with measurement, not implementation. It decomposes `midpoint_points_columnar` to identify whether the cost is:

- adjacency/owner detection
- scaled midpoint arithmetic
- world-coordinate reconstruction / finite filtering
- host packing into `RtdlRayjoinCdbScaledPoint`

## Boundary

Allowed:

- Add subphase instrumentation to the RayJoin paper reproduction binary app.
- Keep the measurement app-owned.
- Preserve the current correctness summary and binary route output.

Forbidden:

- No native/core midpoint primitive yet.
- No RayJoin-specific core API.
- No speedup claim from instrumentation.
- No treating measurement as device-resident implementation.

## Verification

The result must report, for both map sides:

- total midpoint generation time
- owner/adjacency subphase
- scaled midpoint arithmetic subphase
- world/finite-filter subphase
- scaled-point packing subphase
- whether the dominant cost is pack/upload boundary or actual midpoint math

## Exit Labels

- `completed_midpoint_decomposition_pack_boundary_dominated`
- `completed_midpoint_decomposition_math_dominated`
- `completed_midpoint_decomposition_inconclusive_redo`

## Expected Honest Outcome

Given the existing implementation, the likely dominant cost is host packing of scaled midpoint records, not midpoint arithmetic itself. If true, the next implementation goal should not be “more NumPy”; it should be a generic route that keeps midpoint query points as device/columnar data or at least avoids per-row ctypes construction.

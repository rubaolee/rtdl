# Goal1314: Native Polygon Candidate Collection Surface

Date: 2026-05-05

## Decision

RTDL now exposes the Python/ctypes surface for the planned OptiX native
bounded polygon-pair candidate collection ABI:

`rtdl_optix_collect_polygon_pair_candidates_bounded`

This is not app-specific Jaccard ABI. It is a backend-keyed native wrapper for
the generic `COLLECT_K_BOUNDED` primitive over polygon-pair candidate ids.

## Contract

- Input: left and right polygon sets using the existing packed polygon layout.
- Output: stable `(left_polygon_id, right_polygon_id)` candidate ids.
- Capacity: explicit `candidate_capacity`.
- Overflow: fail-closed with no silent truncation.
- Metadata: primitive name, backend, capacity, emitted count, overflow policy,
  complete-coverage flag, and claim boundary.

## Current Boundary

The Python surface is ready for the C++ pod implementation, but the native
OptiX shared library must export the symbol before apps can route through it.
Until that pod-built symbol exists, the wrapper raises a rebuild-oriented error.

This does not promote `polygon_set_jaccard` yet. Jaccard still needs complete
native bounded collection plus native score reduction after complete candidate
coverage before the inventory row can move out of `diagnostic_blocked`.

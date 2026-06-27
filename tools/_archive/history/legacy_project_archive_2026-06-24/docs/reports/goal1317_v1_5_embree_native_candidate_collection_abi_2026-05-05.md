# Goal1317: Embree Native Polygon Candidate Collection ABI

Date: 2026-05-05

## Scope

This slice implements the native Embree export for the v1.5 generic bounded
polygon-pair candidate collection primitive:

`rtdl_embree_collect_polygon_pair_candidates_bounded`

The export is app-name-free and mirrors the OptiX collection contract.

## Implementation

The native Embree implementation decodes left/right polygon references, applies
the existing exact `polygon_pair_flags()` helper to produce the complete
candidate set under the current LSI/PIP definition, sorts/deduplicates by
`(left_polygon_id, right_polygon_id)`, and fails closed when the caller-provided
capacity is too small.

## Local Evidence

Local machine:

- Embree version: 4.4.0.
- Rebuilt the Embree library via `RTDL_FORCE_EMBREE_REBUILD=1`.
- Real ctypes call returned `((1, 10), (2, 11))` for a two-pair authored case.
- Capacity `1` failed closed with:
  `native bounded Embree polygon-pair candidate collection overflowed capacity 1; emitted at least 2; failure_mode=fail_closed_overflow`.
- Source-level ABI tests verify symbol alignment, no app-specific Jaccard fast
  path, stable ordering, and fail-closed source behavior.

## Boundary

This closes the Embree same-contract native wrapper requirement locally. It does
not promote `polygon_set_jaccard` yet because OptiX pod build/runtime validation
and native score reduction after complete candidate coverage remain open.

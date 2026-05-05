# Goal1315: OptiX Native Polygon Candidate Collection ABI

Date: 2026-05-05

## Scope

This slice adds the native OptiX C ABI export for the v1.5 generic bounded
polygon-pair candidate collection primitive:

`rtdl_optix_collect_polygon_pair_candidates_bounded`

The export is app-name-free and returns `RtdlPolygonPairCandidate` rows. It is
not a `polygon_set_jaccard` fast path.

## Implementation

The first implementation is a fail-closed wrapper over the existing OptiX
candidate-discovery passes:

- Segment/segment LSI over polygon edges.
- First-left-vertex-in-right positive PIP.
- First-right-vertex-in-left positive PIP.
- Stable sorting and deduplication by `(left_polygon_id, right_polygon_id)`.
- Overflow check before copying rows to the caller buffer.

This satisfies the ABI and failure-mode contract needed by the Python surface.
It is still multi-pass and is expected to carry the same broad overhead profile
recorded in Goal1312 until a deeper fused implementation is designed.

## Validation State

Local validation completed:

- Python surface tests for missing symbol, success metadata, overflow, and
  capacity validation.
- Native source-level ABI tests for symbol alignment, fail-closed behavior, and
  stable ordering.
- `py_compile` for the Python runtime files.
- `git diff --check`.

Pod validation is still required because macOS local does not have CUDA/OptiX
headers or libraries. The current pod SSH endpoint refused connection during
this slice, so no native shared-library build or runtime candidate collection
artifact is recorded yet.

## Boundary

This does not promote `polygon_set_jaccard`. Remaining blockers are:

- Pod build of the OptiX shared library with the new export.
- Runtime parity against the existing Python/OptiX candidate discovery.
- Fail-closed overflow runtime artifact.
- Symmetric Embree same-contract wrapper.
- Native score reduction after complete candidate coverage.

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

Pod validation completed after syncing through git:

- Pushed `main` to GitHub at commit `492ab680`.
- Pod checkout `/workspace/rtdl_goal1292` reset to `origin/main`.
- GPU: NVIDIA RTX 2000 Ada Generation, driver 570.195.03.
- Built `build/librtdl_optix.so` with `make build-optix`.
- Ran 14 focused surface/ABI tests with
  `RTDL_OPTIX_LIB=/workspace/rtdl_goal1292/build/librtdl_optix.so`.
- Real native ctypes call returned candidate pairs `((1, 10), (2, 11))` for a
  two-pair authored case.
- Capacity `1` failed closed with:
  `native bounded OptiX polygon-pair candidate collection overflowed capacity 1; emitted at least 2; failure_mode=fail_closed_overflow`.

## Boundary

This does not promote `polygon_set_jaccard`. Remaining blockers are:

- Native score reduction after complete candidate coverage.
- App routing through the native bounded collection wrappers with same-summary
  evidence.
- Performance characterization of the native collection wrapper.

# Goal1319: Jaccard Post-Collection Status Cleanup

Date: 2026-05-05

## Scope

Goal1318 pod-validated native bounded collection routing for
`polygon_set_jaccard` on both active v1.5 backends:

- Embree local real-library route uses native bounded collection.
- OptiX pod route reset from GitHub, rebuilt OptiX, and used native bounded
  collection with complete coverage and no overflow.

This cleanup updates project metadata so future work does not keep treating
native bounded collection as missing.

## Changes

- `polygon_jaccard_diagnostic_contract()` now reports
  `future_score_primitive_status=blocked_by_native_score_reduction`.
- The primitive contract schema enforces that status while Jaccard remains
  diagnostic.
- The v1.5 migration inventory now points the Jaccard row at `Goal1318` and
  leaves exactly one remaining app-specific blocker:
  native score reduction after complete candidate coverage.
- The inventory blocker summary now names native `REDUCE_FLOAT(SUM)` score
  reduction after complete bounded collection, rather than bounded collection
  itself.

## Boundary

This is metadata cleanup after validated native collection routing. It does not
promote `polygon_set_jaccard`, does not authorize public speedup wording, and
does not implement native score reduction.

The next implementation slice should add a generic native score-reduction
surface reached only after `COLLECT_K_BOUNDED` reports complete candidate
coverage.

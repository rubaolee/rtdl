# Goal2554: Native Columnar Type Boundary

Date: 2026-05-23

## Scope

This goal continues the post-benchmark-app native cleanup by removing DB-shaped
public type names from active Embree and OptiX implementation code. It does not
remove compatibility names from Python, and it does not change exported C symbol
names or runtime behavior.

## Change

- Active Embree and OptiX implementation code now uses generic columnar names:
  `RtdlColumnField`, `RtdlColumnScalar`, `RtdlColumnClause`,
  `RtdlColumnRowIdRow`, `RtdlGroupedCountRow`, `RtdlGroupedSumRow`,
  `RtdlEmbreeColumnarPayload`, and `RtdlOptixColumnarPayload`.
- OptiX compact-summary support now uses generic names:
  `RtdlColumnCompactSummaryRequest`, `RtdlColumnCompactSummaryResult`,
  `RtdlGroupedSumCountRow`, `RtdlGroupedStatsRow`, and
  `kRtdlColumnCompactSummary*`.
- The old `RtdlDb*` C++ names remain as prelude-only compatibility aliases.
  This preserves ordinary C++ bare-type-name compatibility for local code that
  included the native prelude names directly. It does not preserve C-style
  `struct RtdlDbField` tag spelling; these native preludes are C++ headers.
- Python `ctypes` compatibility names remain unchanged because they are internal
  Python-side layout wrappers and do not define native engine semantics.

## Boundary

This is a naming and ABI-boundary cleanup only. It does not claim that all active
native internals are fully app-name-free. Remaining follow-up work includes
renaming internal helper names such as `DbPrimaryAxis`, `DbRowBox`, `db_*`
helpers, and `kDb*` constants where they are implementation details rather than
compatibility boundaries.

## Validation

- Added `tests/goal2554_native_columnar_type_boundary_test.py`.
- The test fails if active Embree/OptiX implementation files reintroduce the old
  `RtdlDb*` type tokens.
- The test confirms that old names survive only as compatibility aliases in
  prelude headers.

No pod was used. This goal does not require GPU evidence because it is a
source-level compatibility and naming cleanup.

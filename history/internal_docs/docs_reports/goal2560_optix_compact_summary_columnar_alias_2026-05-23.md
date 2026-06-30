# Goal2560: OptiX Compact-Summary Columnar Alias

Date: 2026-05-23

## Scope

Goal2560 adds generic columnar aliases for the remaining OptiX-only
compact-summary ctypes layouts and grouped integer-reduction row layouts. This
continues the Python compatibility-layer cleanup after Goal2558 and Goal2559.

Scope marker: OptiX-only compact-summary aliases.

## Change

- Added `_RtdlGroupedSumRow`, `_RtdlGroupedSumCountRow`, and
  `_RtdlGroupedStatsRow` aliases for OptiX-only grouped integer result layouts.
- Added `_RtdlColumnCompactSummaryRequest` and
  `_RtdlColumnCompactSummaryResult` aliases.
- Added `_COLUMN_COMPACT_SUMMARY_OP_*` aliases for compact-summary operation
  constants.
- Updated the active Python wrapper paths to use the generic aliases for
  compact-summary request/result ctypes signatures and OptiX-only grouped
  integer result rows.

## Boundary

No native ABI changes are made. The aliases point to the existing Python ctypes
layouts and constants. The legacy class definitions remain because historical
tests still assert those exact Python class names. The active Python wrapper
paths now use the generic aliases without breaking old code.

## Validation

- Added `tests/goal2560_optix_compact_summary_columnar_alias_test.py`.
- The test verifies alias object identity and constant equality, while also
  confirming the legacy class definitions remain available.
- The test also checks that active Python wrapper pointer declarations and
  compact-summary request encoding use the generic aliases.

No pod was used. This is local Python compatibility cleanup and does not
require new NVIDIA evidence.

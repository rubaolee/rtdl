# Goal2558: Columnar Ctypes Alias Boundary

Date: 2026-05-23

## Scope

Goal2558 adds generic columnar aliases for the low-level Python ctypes layout
and encoder names that still carried the historical DB vocabulary. This is a
compatibility-layer cleanup: the existing DB-shaped names are not removed.

## Change

- Added generic columnar aliases for ctypes layouts:
  `_RtdlColumnField`, `_RtdlColumnScalar`, `_RtdlColumnClause`,
  `_RtdlColumnRowIdRow`, `_RtdlGroupedCountRow`, and `_RtdlGroupedSumRow`.
- Added generic columnar aliases for constants:
  `_COLUMN_KIND_*` and `_COLUMN_OP_*`.
- Added generic columnar aliases for encoder helpers:
  `_encode_columnar_*` and `_decode_columnar_group_key`.

## Boundary

No native symbol is changed. The aliases point to the existing ctypes layouts
and helper functions, so binary layout and behavior are unchanged. Legacy
DB-shaped names remain because older runtime wrappers and historical tests
still depend on them. New code can prefer the generic columnar aliases.

Compatibility marker: legacy DB-shaped names remain.

## Validation

- Added `tests/goal2558_columnar_ctypes_alias_boundary_test.py`.
- The test verifies that each generic alias is the same object or same constant
  value as the legacy compatibility name.

No pod was used. This is local Python compatibility cleanup and does not need
new NVIDIA evidence.

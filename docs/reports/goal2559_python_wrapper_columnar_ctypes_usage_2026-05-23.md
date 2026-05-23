# Goal2559: Python Wrapper Columnar Ctypes Usage

Date: 2026-05-23

## Scope

Goal2559 starts consuming the generic columnar ctypes aliases added in
Goal2558 inside the active Embree and OptiX Python wrappers. This is limited to
common ctypes layouts shared by the row-id and grouped-count columnar payload
paths.

## Change

- Embree and OptiX wrappers now use `_RtdlColumnField`,
  `_RtdlColumnRowIdRow`, and `_RtdlGroupedCountRow` for common ctypes pointer
  declarations and row-view layouts.
- Legacy `_RtdlDbField`, `_RtdlDbRowIdRow`, and `_RtdlDbGroupedCountRow`
  imports remain as explicit compatibility markers for older tests and callers.

## Boundary

No behavior or native ABI changes are made. This is a Python wrapper naming
cleanup over identity-preserving aliases. OptiX-only compact-summary layouts
remain DB-shaped for now because historical tests still assert their exact
class definitions; they should be migrated in a separate, compatibility-aware
slice.

Boundary marker: OptiX-only compact-summary layouts remain.

## Validation

- Added `tests/goal2559_python_wrapper_columnar_ctypes_usage_test.py`.
- The test checks active Embree/OptiX wrappers use the generic aliases for
  common ctypes layouts and still retain legacy compatibility markers.

No pod was used. This is local Python wrapper cleanup and does not require new
NVIDIA evidence.

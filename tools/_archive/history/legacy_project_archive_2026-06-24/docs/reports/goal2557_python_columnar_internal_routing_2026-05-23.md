# Goal2557: Python Columnar Internal Routing

Date: 2026-05-23

## Scope

Goal2557 continues the app-independence cleanup inside the Python runtime layer.
Goal2556 added generic public prepared-columnar names; this goal changes
internal Python routing names so prepared Embree/OptiX predicate-scan and
grouped-reduction paths are columnar-first internally.

## Change

- Renamed prepared-kernel routing helpers to
  `_prepare_columnar_embree_execution` and
  `_prepare_columnar_optix_execution`.
- Renamed internal execution dataclasses to
  `PreparedEmbreeColumnarExecution` and `PreparedOptixColumnarExecution`.
- Renamed low-level prepared payload wrappers to
  `EmbreePreparedColumnarPayload` and `OptixPreparedColumnarPayload`.
- Kept explicit compatibility aliases for old internal names:
  `PreparedEmbreeDbExecution`, `PreparedOptixDbExecution`,
  `EmbreePreparedDbDataset`, and `OptixPreparedDbDataset`.

## Boundary

This does not rename the older high-level compatibility API
`PreparedEmbreeDbDataset` or `PreparedOptixDbDataset`; Goal2556 already added
the preferred generic public names alongside those. It also does not rename
ctypes layout wrappers such as `_RtdlDbField` because those wrappers preserve
historical Python/native layout compatibility and are asserted by older tests.
In short: ctypes layout wrappers remain unchanged.

## Validation

- Added `tests/goal2557_python_columnar_internal_routing_test.py`.
- The test rejects old `_prepare_db_*` routing helpers and checks that low-level
  prepared payload internals use columnar primary names with compatibility
  aliases.

No pod was used. This is local Python runtime naming cleanup and does not
require new NVIDIA evidence.

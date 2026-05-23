# Goal2556: Python Columnar Public API Boundary

Date: 2026-05-23

## Scope

Goal2556 adds a generic Python public API for prepared columnar payloads while
preserving the older DB-shaped names as compatibility surface. This is a Python
API boundary cleanup, not a native engine behavior change.

## Change

- Added `PreparedEmbreeColumnarPayload` and
  `prepare_embree_columnar_payload`.
- Added `PreparedOptixColumnarPayload` and `prepare_optix_columnar_payload`.
- Updated `prepare_embree_columnar_record_set` and
  `prepare_optix_columnar_record_set` to route through the generic prepared
  columnar payload classes.
- Exported the new names from `rtdsl.__init__` and `rtdsl.__all__`.

## Compatibility

The old `PreparedEmbreeDbDataset`, `PreparedOptixDbDataset`,
`prepare_embree_db_dataset`, and `prepare_optix_db_dataset` names remain
available. The generic prepared classes subclass the old classes so existing
callers and tests keep working while new code can avoid DB-shaped public names.
In short: legacy DB names remain compatibility aliases, not the preferred
language surface.

## Boundary

No native symbol is changed. Python-side ctypes layout wrappers such as
`_RtdlDbField` also remain in place for compatibility with older wrapper code.
Renaming those low-level wrappers is a separate cleanup because many historical
tests explicitly assert their presence.

## Validation

- Added `tests/goal2556_python_columnar_public_api_boundary_test.py`.
- The test verifies the generic names are public, exported, and route direct
  `ColumnarRecordSet` preparation through the generic classes.
- The test also verifies old DB-shaped Python names remain available.

No pod was used. This is local Python API cleanup and does not require new
NVIDIA runtime evidence.

# Goal2555: Native Columnar Helper Boundary

Date: 2026-05-23

## Scope

Goal2555 completes the immediate follow-up from Goal2554 by renaming the
remaining DB-shaped active Embree/OptiX implementation helper names that were
not native ABI compatibility boundaries. The target is active Embree/OptiX
implementation internals only.

Scope marker: active Embree/OptiX implementation internals.

## Change

- Active Embree/OptiX helper structs now use columnar names such as
  `ColumnarPrimaryAxis`, `ColumnarRowBox`, `ColumnarRowBoxSceneData`,
  `ColumnarGroupedCountRayQueryState`, and
  `ColumnarGroupedSumRayQueryState`.
- Active helper functions and globals now use `columnar_*` and
  `g_columnar_*` names instead of `db_*`, embedded `_db_`, and `g_db*`.
- Active implementation constants now use `kColumnar*`, `kColumnKind*`,
  `kColumnOp*`, `RTDL_COLUMN_KIND_*`, and `RTDL_COLUMN_OP_*`.
- The field-oriented helpers produced by the rename are intentionally named
  `columnar_validate_payload_fields` and
  `columnar_copy_dataset_from_payload_fields` to avoid ambiguous
  `columnar_*_columnar_*` names.

## Boundary

No exported C symbol is renamed in this goal. Python compatibility names,
prelude compatibility aliases, historical reports, tutorials, inactive backend
proof surfaces, and app-layer DB/RayDB/DBSCAN wording remain outside this
source-level cleanup. This goal does not make a new performance claim and does
not change runtime semantics.

## Validation

- Added `tests/goal2555_native_columnar_helper_boundary_test.py`.
- The test scans active Embree/OptiX implementation files and rejects
  DB-shaped helper identifiers, embedded `_db_` helper fragments, uppercase
  `DB` implementation wording, and old `RTDL_DB_*` implementation constants.
- The test also checks for representative replacement names and rejects the
  ambiguous `columnar_*_columnar_*` artifacts that can result from mechanical
  renames.

No pod was used. This is a local source-boundary cleanup and does not require
new NVIDIA runtime evidence.

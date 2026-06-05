# Goal3447 - Shape-Pair Active Relation Device Columns

## Status

Implemented locally; pod validation pending.

Goal3447 extends the Goal3442/3443 RayJoin overlay path from a scalar active-count continuation to a reusable, app-agnostic device-column stream. The new OptiX native ABI compacts active shape-pair relation dependencies into CUDA-resident columns:

- `left_id`
- `right_id`
- `requires_segment_intersection`
- `requires_point_containment`

The native engine still sees only generic shape-pair relation flags. RayJoin overlay semantics, richer witness expansion, relation-row naming, and partner continuation stay in Python or partner code.

## What Changed

Native OptiX adds:

- `RtdlNativeShapePairRelationDeviceColumns`
- `rtdl_optix_prepared_shape_pair_relation_active_device_columns`
- `rtdl_optix_release_shape_pair_relation_active_device_columns`
- `shape_pair_relation_active_relation_device_columns_kernel`

The kernel reuses the same active predicate as the Goal3442 scalar device continuation, including the inclusive containment fix, then writes only active relation ids and dependency flags into device columns. Capacity overflow is fail-closed: partial relation columns are not authorized, and the returned metadata reports the required active relation count as the retry hint.

Python adds:

- `OptixShapePairRelationDeviceColumnOutput`
- `PreparedOptixShapePairRelation.active_relation_device_columns(...)`
- generic v2.8 typed-stream metadata for `shape_pair_relation_flags_2d_device_columns`
- an app-layer RayJoin method, `run_packed_left_active_relation_device_columns(...)`, for benchmark timing and metadata

## Claim Boundary

This goal does not authorize:

- v2.8 release
- public speedup wording
- RT-core speedup wording
- true-zero-copy wording
- RayJoin paper reproduction claims
- RTDL-beats-RayJoin claims
- full overlay relation-row or overlay-area completion claims

The goal is a runtime primitive improvement: a generic resident relation-column stream that should make future RayJoin overlay continuation and partner filtering cheaper than host materialized relation rows.

## Validation

Local validation:

- `py -3 -m py_compile src\rtdsl\optix_runtime.py src\rtdsl\v2_8_geometry_relation_typed_stream.py src\rtdsl\__init__.py examples\v2_0\research_benchmarks\spatial_rayjoin\rtdl_rayjoin_v2_spatial_join_app.py`
- `py -3 -m unittest tests.goal3447_shape_pair_active_relation_device_columns_test`

Pod validation target:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so \
python scripts/goal3447_shape_pair_active_relation_device_columns_probe.py \
  --iterations 4 \
  --output docs/reports/goal3447_shape_pair_active_relation_device_columns_pod_2026-06-05.json
```

Expected pod checks:

- host active count equals scalar device active count equals resident relation-column row count
- native phase mode is `active_relation_device_columns`
- CuPy can wrap the resident columns when available
- all claim-boundary flags remain false

## Remaining Work

Goal3447 does not finish full RayJoin overlay. The next useful step is a partner or native continuation over these generic relation columns that can produce richer grouped overlay summaries or bounded witness rows without returning to host materialized relation-row tables.

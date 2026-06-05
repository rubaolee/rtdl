# Goal3447 - Shape-Pair Active Relation Device Columns

## Status

Implemented and pod-validated.

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

Pod validation:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so \
python scripts/goal3447_shape_pair_active_relation_device_columns_probe.py \
  --iterations 4 \
  --output docs/reports/goal3447_shape_pair_active_relation_device_columns_pod_2026-06-05.json
```

Pod artifact:

- `docs/reports/goal3447_shape_pair_active_relation_device_columns_pod_2026-06-05.json`
- `docs/reports/goal3447_shape_pair_active_relation_device_columns_pod_2026-06-05.stdout`

Hardware/result summary:

- Commit: `2b62228f`
- GPU: NVIDIA RTX A5000, driver `580.126.09`
- Dataset: `br_county.cdb` joined against `br_county_start256_count1024.cdb`
- Left/right shapes: `15700 / 949`
- Active relation count: `4543`
- Counts matched for all four iterations:
  - host active count: `[4543, 4543, 4543, 4543]`
  - scalar device active count: `[4543, 4543, 4543, 4543]`
  - resident relation-column row count: `[4543, 4543, 4543, 4543]`
- Median host active-count time: `0.12831534119322896s`
- Median resident relation-column time: `0.0035939733497798443s`
- Median speedup versus host active-count route: `35.419570165171095x`
- CuPy wrapped the resident columns and verified all emitted rows have at least one active dependency flag.
- Native phase mode was `active_relation_device_columns`.
- All claim-boundary flags remained false.

## Remaining Work

Goal3447 does not finish full RayJoin overlay. The next useful step is a partner or native continuation over these generic relation columns that can produce richer grouped overlay summaries or bounded witness rows without returning to host materialized relation-row tables.

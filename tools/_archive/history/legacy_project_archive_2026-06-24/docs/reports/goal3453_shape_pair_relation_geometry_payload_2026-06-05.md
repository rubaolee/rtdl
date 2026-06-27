# Goal3453 - Shape-Pair Relation Geometry Payload Columns

## Status

Implemented and pod-validated on NVIDIA RTX A5000.

Goal3453 adds a generic geometry-payload surface to the resident shape-pair relation column stream. Goal3447-3450 proved active relation ids and dependency flags; this goal exposes the geometry payload needed by future partner/native witness and overlay-area continuations.

## What Changed

The native `RtdlNativeShapePairRelationDeviceColumns` output now includes:

- relation columns: `left_id`, `right_id`, `requires_segment_intersection`, `requires_point_containment`
- generic geometry payload pointers:
  - left/right polygon refs
  - left/right vertex-x columns
  - left/right vertex-y columns
  - left/right bounds columns
- payload sizes:
  - left/right polygon count
  - left/right vertex count

The left geometry payload is retained by the relation-column output owner. The right geometry payload remains owned by the prepared shape-pair handle. Python exposes `as_cupy_geometry_payload_columns()` for explicit partner continuations.

## Boundary

This is not full RayJoin overlay and not a public performance claim. It does not authorize:

- v2.8 release
- public speedup wording
- RT-core speedup wording
- true-zero-copy wording
- RayJoin paper reproduction claims
- RTDL-beats-RayJoin claims
- full overlay-area or exact witness completion claims
- app-specific native-engine logic

The intended claim is narrow: RTDL can now expose the generic geometry payload needed by a future bounded witness/area continuation without baking RayJoin semantics into the native engine.

## Pod Evidence

Artifacts:

- `docs/reports/goal3453_shape_pair_relation_geometry_payload_pod_2026-06-05.json`
- `docs/reports/goal3453_shape_pair_relation_geometry_payload_pod_2026-06-05.stdout`

Pod:

- GPU: NVIDIA RTX A5000, driver 580.126.09
- Commit: `dda288dae545ef115fb46903ad18db62b3bb0aaa`
- Library rebuilt with `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`

The sparse-id fixture validated:

- `geometry_payload_matches: true`
- `metadata_schema_id: shape_pair_relation_flags_2d_device_columns`
- `metadata_geometry_payload.schema: shape_pair_relation_geometry_payload_device_columns`
- `metadata_geometry_payload.device_resident: true`
- `metadata_geometry_payload.left_payload_lifetime: relation_column_output_owner`
- `metadata_geometry_payload.right_payload_lifetime: prepared_shape_pair_relation_handle`
- all claim-boundary flags remained false

The observed CuPy-wrapped geometry payload matched expected refs, vertices, and bounds:

| side | polygon refs | vertex count | bounds rows |
| --- | ---: | ---: | ---: |
| left | 3 | 12 | 3 |
| right | 4 | 16 | 4 |

## Validation

Local validation:

- `py -3 -m py_compile scripts\goal3453_shape_pair_relation_geometry_payload_probe.py`
- `py -3 -m unittest tests.goal3453_shape_pair_relation_geometry_payload_test`

Pod validation:

```bash
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so \
python scripts/goal3453_shape_pair_relation_geometry_payload_probe.py \
  --output docs/reports/goal3453_shape_pair_relation_geometry_payload_pod_2026-06-05.json
```

- `PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so python -m unittest tests.goal3453_shape_pair_relation_geometry_payload_test`

## Remaining Work

The next engineering target is a bounded generic witness/area continuation that consumes relation ids, flags, and geometry payload columns. That continuation must remain generic; RayJoin-specific overlay interpretation belongs in the benchmark app layer.

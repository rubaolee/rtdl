# Goal3455 - Shape-Pair Relation Ordinal Columns

## Status

Implemented and pod-validated on NVIDIA RTX A5000.

Goal3455 adds zero-based `left_ordinal` and `right_ordinal` device columns to the generic shape-pair relation stream.

## Why This Matters

Goal3453 exposed generic geometry payload columns, but relation rows only carried sparse user ids. Sparse ids are correct output identity, but they are not safe indices into geometry payload arrays. A partner continuation needs ordinals to index `left_polygon_refs`, `right_polygon_refs`, bounds, and vertex arrays without assuming ids are dense.

## What Changed

- Native relation-column output now owns:
  - `left_ordinals_device_ptr`
  - `right_ordinals_device_ptr`
- The active relation compaction kernel writes ordinals alongside ids and flags.
- Python exposes:
  - `as_cupy_ordinal_columns()`
  - `metadata["runtime"]["ordinal_columns"]`
- Metadata states that ordinals are `zero_based_index_into_shape_pair_geometry_payload_arrays` and that sparse user ids are not dense geometry indices.

## Boundary

This is a generic continuation-enabling primitive. It does not authorize:

- v2.8 release
- public speedup wording
- RT-core speedup wording
- true-zero-copy wording
- RayJoin paper reproduction claims
- RTDL-beats-RayJoin claims
- full overlay-area or exact witness completion claims
- app-specific native-engine logic

## Validation

Pod evidence:

- Artifact: `docs/reports/goal3455_shape_pair_relation_ordinal_columns_pod_2026-06-05.json`
- Stdout: `docs/reports/goal3455_shape_pair_relation_ordinal_columns_pod_2026-06-05.stdout`
- GPU: NVIDIA RTX A5000, driver 580.126.09
- Commit: `fd200cca7fbbb55211bf2102bc3d1e673727abca`
- `ordinal_rows_match: true`
- `metadata_ordinal_columns.device_resident: true`
- `metadata_geometry_payload.device_resident: true`
- all claim-boundary flags remained false

Local validation:

- `py -3 -m py_compile scripts\goal3455_shape_pair_relation_ordinal_columns_probe.py`
- `py -3 -m unittest tests.goal3455_shape_pair_relation_ordinal_columns_test`

Pod validation:

```bash
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so \
python scripts/goal3455_shape_pair_relation_ordinal_columns_probe.py \
  --output docs/reports/goal3455_shape_pair_relation_ordinal_columns_pod_2026-06-05.json
```

Expected rows:

| left_id | right_id | left_ordinal | right_ordinal |
| ---: | ---: | ---: | ---: |
| 3 | 10 | 0 | 0 |
| 3 | 11 | 0 | 1 |
| 20 | 13 | 1 | 3 |

## Remaining Work

The next step is to consume these ordinals plus the Goal3453 geometry payload in a bounded generic witness/area continuation.

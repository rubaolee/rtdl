# Goal3460 - Large Shape-Pair Relation Content Oracle

## Status

Implemented locally; pod validation pending.

Goal3460 adds an independent large-scale content oracle for the v2.8 shape-pair relation device-column stream. This follows the Goal3459 scale probe, but checks exact relation row content instead of only measuring a bounds-overlap continuation.

## Scope

The probe compares:

- host oracle active relation rows
- device-resident relation column rows
- sparse user IDs
- zero-based geometry payload ordinals
- `requires_segment_intersection`
- `requires_point_containment`

The host oracle intentionally mirrors the generic native relation contract:

- bounds prefilter
- non-collinear segment-edge intersection using the native tolerance rule
- if no segment-edge relation exists, first-left-vertex-in-right or first-right-vertex-in-left containment

## Boundary

This goal does not authorize:

- v2.8 release
- public speedup wording
- broad RT-core speedup wording
- true-zero-copy wording
- RayJoin paper reproduction claims
- RTDL-beats-RayJoin claims
- exact polygon overlay area claims

The public RayJoin CDB polygons are non-integer and non-orthogonal, so the older integer-grid exact-area continuation is not a valid exact overlay oracle for this dataset. Goal3460 is therefore a relation-content oracle, not an exact overlay-area completion.

## Validation

Local validation:

- `py -3 -m py_compile scripts\goal3460_shape_pair_relation_large_content_oracle.py`
- `py -3 -m unittest tests.goal3460_shape_pair_relation_large_content_oracle_test`

Pod validation target:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so \
python -u scripts/goal3460_shape_pair_relation_large_content_oracle.py \
  --max-rows 65536 \
  --progress-every 1000 \
  --output docs/reports/goal3460_shape_pair_relation_large_content_oracle_pod_2026-06-05.json
```

## Remaining Work

The exact overlay lane still needs a generic polygon-continuation primitive for non-integer, non-orthogonal polygons. That is larger than the old integer-grid area helper and remains separate from this content oracle.

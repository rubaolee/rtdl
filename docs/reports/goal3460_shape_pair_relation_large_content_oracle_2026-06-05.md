# Goal3460 - Large Shape-Pair Relation Content Oracle

## Status

Implemented and pod-validated on an NVIDIA RTX A5000 pod.

Goal3460 adds an independent large-scale content oracle for the v2.8 shape-pair relation device-column stream. This follows the Goal3459 scale probe, but checks exact relation row content instead of only measuring a bounds-overlap continuation.

## Scope

The probe compares:

- host oracle active relation rows
- device-resident relation column rows
- sparse user IDs
- zero-based geometry payload ordinals
- `requires_segment_intersection`
- `requires_point_containment`

The host oracle intentionally mirrors the generic native relation contract and numeric contract:

- bounds prefilter
- float32 coordinate quantization, matching the native OptiX payload
- non-collinear segment-edge intersection using the native float32 tolerance rule
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

Pod validation:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so \
python -u scripts/goal3460_shape_pair_relation_large_content_oracle.py \
  --max-rows 65536 \
  --progress-every 1000 \
  --output docs/reports/goal3460_shape_pair_relation_large_content_oracle_pod_2026-06-05.json
```

Observed pod evidence at commit `617a1588` on `NVIDIA RTX A5000, 580.126.09`:

- input: `br_county.cdb` (15,700 left shapes) vs `br_county_start256_count1024.cdb` (949 right shapes)
- host oracle bbox candidates: 5,260
- host oracle active relation rows: 4,543
- device relation rows: 4,543
- segment-intersection relation rows: 4,539
- containment-only relation rows: 4
- missing relation pairs: 0
- extra relation pairs: 0
- flag or ordinal mismatches: 0
- host native-fidelity oracle time: 43.685401489026845 seconds
- device relation-column extraction time: 1.5327195869758725 seconds
- geometry payload and ordinal columns remained device-resident
- all release, public speedup, RT-core speedup, true-zero-copy, RayJoin-paper reproduction, RTDL-beats-RayJoin, and full-overlay-area claim flags remained false

One strict double-precision draft oracle found five apparent mismatches. Direct inspection showed all five were float32 boundary cases: four duplicate-ID same-geometry pairs and one near-endpoint segment relation. The checked-in oracle therefore quantizes host coordinates and segment arithmetic through `ctypes.c_float` to match the native OptiX relation-column contract. This is a native-fidelity content oracle, not a stronger double-precision geometric theorem.

Artifacts:

- `docs/reports/goal3460_shape_pair_relation_large_content_oracle_pod_2026-06-05.json`
- `docs/reports/goal3460_shape_pair_relation_large_content_oracle_pod_2026-06-05.stdout`

## Remaining Work

The exact overlay lane still needs a generic polygon-continuation primitive for non-integer, non-orthogonal polygons. That is larger than the old integer-grid area helper and remains separate from this content oracle.

# Goal3463 - Shape-Pair Relation Witness Continuation

## Status

Implemented locally; pod validation pending.

Goal3463 adds a generic CuPy continuation that consumes resident shape-pair relation ids, flags, ordinals, and geometry payload columns, then emits witness columns for each active relation row.

## Witness Contract

Witness kinds:

- `1`: segment-edge intersection witness
- `2`: left first vertex inside right
- `3`: right first vertex inside left
- `4`: segment flag without a found edge witness
- `5`: containment flag without a found vertex witness

Kinds `4` and `5` are failure sentinels. A valid run must have no unresolved witness kinds.

## Boundary

This is a witness continuation, not an exact polygon overlay-area continuation. It does not compute intersection area, union area, polygon clipping output, or Jaccard.

This goal does not authorize:

- v2.8 release
- public speedup wording
- broad RT-core speedup wording
- true-zero-copy wording
- RayJoin paper reproduction claims
- RTDL-beats-RayJoin claims
- full exact overlay-area completion claims

## Validation

Local validation:

- `py -3 -m py_compile src\rtdsl\geometry_relation_continuations.py scripts\goal3463_shape_pair_relation_witness_continuation_probe.py tests\goal3463_shape_pair_relation_witness_continuation_test.py`
- `py -3 -m unittest tests.goal3463_shape_pair_relation_witness_continuation_test`

Pod validation target:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so \
python -u scripts/goal3463_shape_pair_relation_witness_continuation_probe.py \
  --max-rows 65536 \
  --output docs/reports/goal3463_shape_pair_relation_witness_continuation_pod_2026-06-05.json
```

## Remaining Work

Goal3463 narrows the exact-witness gap, but the exact overlay-area lane still needs a generic polygon clipping/area continuation for non-integer, non-orthogonal polygons.

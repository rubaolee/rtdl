# Goal3463 - Shape-Pair Relation Witness Continuation

## Status

Implemented and pod-validated on an NVIDIA RTX A5000 pod.

Goal3463 adds a generic CuPy continuation that consumes resident shape-pair relation ids, flags, ordinals, and geometry payload columns, then emits witness columns for each active relation row.

## Witness Contract

Witness kinds:

- `1`: segment-edge intersection witness
- `2`: left first vertex inside right
- `3`: right first vertex inside left
- `4`: segment flag without a found edge witness
- `5`: containment flag without a found vertex witness

Kinds `4` and `5` are failure sentinels. A valid run must have no unresolved witness kinds.

For segment-flagged rows, witness discovery uses a small endpoint tolerance (`t/u` within `1e-5`, denominator threshold `1e-8`) because the upstream OptiX relation producer is a float32 boundary-sensitive primitive. This tolerance is recorded in continuation metadata and does not authorize exact double-precision geometric claims.

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

Pod validation:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so \
python -u scripts/goal3463_shape_pair_relation_witness_continuation_probe.py \
  --max-rows 65536 \
  --output docs/reports/goal3463_shape_pair_relation_witness_continuation_pod_2026-06-05.json
```

Observed pod evidence at commit `dd25ccf1` on `NVIDIA RTX A5000, 580.126.09`:

- input: `br_county.cdb` (15,700 left shapes) vs `br_county_start256_count1024.cdb` (949 right shapes)
- active relation rows: 4,543
- segment-flag rows: 4,539
- containment-flag rows: 4
- witness kind counts: `1 -> 4,539`, `2 -> 4`
- unresolved witness rows: 0
- relation-column production time: 1.5187160652130842 seconds
- CuPy witness continuation time: 0.2459023343399167 seconds
- geometry payload and ordinal columns remained device-resident
- all release, public speedup, RT-core speedup, true-zero-copy, RayJoin-paper reproduction, RTDL-beats-RayJoin, and full-overlay-area claim flags remained false

Implementation notes from the pod:

- The RawKernel is self-contained and avoids CUDA header includes because this pod's NVRTC path could not open `math.h`.
- An initial strict endpoint test left five segment-flag rows unresolved. Direct device-payload inspection showed those were native float32 boundary cases, so the final continuation records and uses the explicit endpoint tolerance described above.

Artifacts:

- `docs/reports/goal3463_shape_pair_relation_witness_continuation_pod_2026-06-05.json`
- `docs/reports/goal3463_shape_pair_relation_witness_continuation_pod_2026-06-05.stdout`

## Remaining Work

Goal3463 narrows the exact-witness gap, but the exact overlay-area lane still needs a generic polygon clipping/area continuation for non-integer, non-orthogonal polygons.

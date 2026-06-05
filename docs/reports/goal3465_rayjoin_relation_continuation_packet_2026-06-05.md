# Goal3465 - RayJoin Relation Continuation Packet

## Status

Implemented locally; pod validation pending.

Goal3465 adds a combined current-performance packet for the v2.8 Spatial RayJoin relation stream. Each iteration creates one resident active relation stream, then runs:

- generic grouped-count continuation by left id
- generic bounds-overlap area continuation
- generic relation witness continuation

## Purpose

Goals3459-3464 proved these pieces separately. Goal3465 measures the chained path in one place so the project has a coherent "where are we now?" artifact before designing the larger exact overlay-area primitive.

## Boundary

The packet still does not compute exact polygon overlay area. Bounds-overlap area remains a proxy/upper-bound continuation, and witness columns are relation witnesses, not clipped polygon output.

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

- `py -3 -m py_compile scripts\goal3465_rayjoin_relation_continuation_packet.py`
- `py -3 -m unittest tests.goal3465_rayjoin_relation_continuation_packet_test`

Pod validation target:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so \
python -u scripts/goal3465_rayjoin_relation_continuation_packet.py \
  --iterations 4 \
  --max-rows 65536 \
  --output docs/reports/goal3465_rayjoin_relation_continuation_packet_pod_2026-06-05.json
```

## Remaining Work

Exact overlay-area continuation for non-integer, non-orthogonal polygons remains the main RayJoin gap.

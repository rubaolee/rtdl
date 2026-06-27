# Goal3465 - RayJoin Relation Continuation Packet

## Status

Implemented and validated on the RTX A5000 pod.

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

Pod validation:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so \
python -u scripts/goal3465_rayjoin_relation_continuation_packet.py \
  --iterations 4 \
  --max-rows 65536 \
  --output docs/reports/goal3465_rayjoin_relation_continuation_packet_pod_2026-06-05.json
```

- Artifact:
  `docs/reports/goal3465_rayjoin_relation_continuation_packet_pod_2026-06-05.json`
- Stdout:
  `docs/reports/goal3465_rayjoin_relation_continuation_packet_pod_2026-06-05.stdout`
- Commit under test:
  `852190b0da1b43e11d1fd708746d1d1244d62976`
- GPU:
  NVIDIA RTX A5000, driver 580.126.09
- Dataset:
  `br_county.cdb` (15,700 left shapes) versus
  `br_county_start256_count1024.cdb` (949 right shapes)
- Pod unit test rerun:
  `PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so python -m unittest tests.goal3465_rayjoin_relation_continuation_packet_test`

The packet produced four stable iterations:

| Measure | Value |
| --- | ---: |
| relation rows | 4,543 |
| grouped left rows | 1,261 |
| grouped count sum | 4,543 |
| bounds-overlap area sum | 150.69938331940557 |
| unresolved witness rows | 0 |
| witness kinds | 4,539 segment-edge intersections; 4 containment witnesses |

Timing summary:

| Phase | Median Seconds | Min Seconds | Max Seconds |
| --- | ---: | ---: | ---: |
| relation columns | 0.004716 | 0.004017 | 0.357563 |
| grouped count continuation | 0.000167 | 0.000136 | 0.305229 |
| bounds-overlap area continuation | 0.000920 | 0.000840 | 0.059692 |
| witness continuation | 0.059789 | 0.055268 | 0.068231 |
| total relation plus continuations | 0.065802 | 0.060451 | 0.815237 |

The first iteration includes setup/warm-up costs. The steady-state chain shows
that the current generic relation stream can feed grouped count, proxy area,
and witness continuations in one coherent packet. The witness continuation is
now the largest measured steady-state continuation in this packet.

## Remaining Work

Exact overlay-area continuation for non-integer, non-orthogonal polygons remains the main RayJoin gap.

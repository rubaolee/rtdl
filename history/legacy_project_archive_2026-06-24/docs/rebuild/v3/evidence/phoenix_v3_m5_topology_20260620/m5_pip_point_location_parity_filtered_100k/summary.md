# RayJoin CDB Point-Location Comparison

This run compares the RayJoin-specialized CDB point-location contract: a vertical ray finds the closest CDB boundary segment, then the directed segment maps to a face id. The base CDB, query CDB, and point-location semantics are shared by RTDL OptiX and RTDL Embree; RayJoin is the author `query_exec` PIP path over the same files.

## Input

- Base CDB chains: 16545
- Base CDB boundary segments: 326193
- Query points: 100000
- Contract: vertical-ray closest CDB boundary segment, then directed left/right face-id lookup
- RTDL timed output: scalar positive-face count for RTDL; RayJoin author Query timer for PIP
- RTDL row materialization during timing: False

The query point stream is the backend-parity-filtered 100k CDB stream generated for this run: ambiguous boundary/tie points were rejected so the hardware comparison measures traversal and closest-hit behavior instead of floating-point tie policy.

## Results

| Engine | Median hot query | Native traversal median | Hot repeats | Total hot timed | Positive faces | Speed vs Embree | Speed vs RTDL OptiX | Notes |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| RayJoin RT | 0.470115 ms | n/a | 1000 | 0.470 s | n/a | 11.00x | 5.73x | author `query_exec`; Query timer |
| RTDL OptiX | 2.692629 ms | 1.814979 ms | 1000 | 2.737 s | 43738 | 1.92x | 1.00x | prepared CDB route; scalar count output |
| RTDL Embree | 5.169664 ms | 5.143595 ms | 1000 | 7.857 s | 43738 | 1.00x | 0.521x | CPU BVH; scalar count output |

## Correctness

RTDL OptiX and RTDL Embree materialized all 100000 query rows after timing. Rows matched exactly on `(point_id, face_id, segment_id)`: mismatches = 0. Positive-face counts were stable and equal: 43738.

## Interpretation

- End-to-end RTDL OptiX is 1.92x faster than RTDL Embree for the same CDB face-id count contract.
- Native traversal alone shows the RT-core effect more directly: OptiX 1.814979 ms vs Embree 5.143595 ms, or 2.83x faster traversal.
- The RTDL OptiX wall median is much larger than its native traversal median because this route still pays host/GPU staging, launch, and count-return overhead.
- RayJoin author Query time (0.470115 ms) is faster than the RTDL OptiX hot median (2.692629 ms) on this same-contract PIP row.
- RayJoin author Query time is also 3.86x faster than the RTDL OptiX native traversal median (1.814979 ms).
- This shows RT cores are effective for CDB point-location and that RayJoin's specialized implementation achieves lower per-query latency than the current RTDL OptiX path on this hardware. It does not reproduce the RayJoin paper's experimental comparison.

# RayJoin CDB Point-Location Comparison

This run compares the RayJoin-specialized CDB point-location contract: a vertical ray finds the closest CDB boundary segment, then the directed segment maps to a face id. The base CDB, query CDB, and point-location semantics are shared by RTDL OptiX and RTDL Embree; RayJoin is the author `query_exec` PIP path over the same files.

## Input

- Base CDB chains: 16545
- Base CDB boundary segments: 326193
- Query points: 100000
- Contract: vertical-ray closest CDB boundary segment, then directed left/right face-id lookup
- RTDL timed output: scalar positive-face count for RTDL; RayJoin author Query timer for PIP
- RTDL row materialization during timing: False

The query point stream is the safe 100k CDB stream generated for this run: ambiguous boundary/tie points were rejected so the hardware comparison measures traversal and closest-hit behavior instead of floating-point tie policy.

## Results

| Engine | Median hot query | Native traversal median | Hot repeats | Total hot timed | Positive faces | Speed vs Embree | Speed vs RTDL OptiX | Notes |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| RTDL OptiX | 2.694927 ms | 1.815013 ms | 1000 | 2.788 s | 43738 | 1.87x | 1.00x | prepared CDB route; scalar count output |
| RTDL Embree | 5.040243 ms | 5.016792 ms | 1000 | 7.750 s | 43738 | 1.00x | 0.535x | CPU BVH; scalar count output |

## Correctness

RTDL OptiX and RTDL Embree materialized all 100000 query rows after timing. Rows matched exactly on `(point_id, face_id, segment_id)`: mismatches = 0. Positive-face counts were stable and equal: 43738.

## Interpretation

- End-to-end RTDL OptiX is 1.87x faster than RTDL Embree for the same CDB face-id count contract.
- Native traversal alone shows the RT-core effect more directly: OptiX 1.815013 ms vs Embree 5.016792 ms, or 2.76x faster traversal.
- The RTDL OptiX wall median is much larger than its native traversal median because this route still pays host/GPU staging, launch, and count-return overhead.
- RayJoin author `query_exec` was not provided for this run, so author-code comparison remains blocked.

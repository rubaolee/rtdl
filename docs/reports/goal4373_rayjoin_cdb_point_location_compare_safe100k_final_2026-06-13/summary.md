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
| RayJoin RT | 0.514778 ms | n/a | 20000 | 10.296 s | n/a | 20.29x | 1.85x | author `query_exec`; Query timer |
| RTDL OptiX | 0.952091 ms | 0.085593 ms | 10000 | 10.474 s | 53912 | 10.97x | 1.00x | prepared CDB route; scalar count output |
| RTDL Embree | 10.442629 ms | 10.426036 ms | 1000 | 11.775 s | 53912 | 1.00x | 0.091x | CPU BVH; scalar count output |

## Correctness

RTDL OptiX and RTDL Embree materialized all 100000 query rows after timing. Rows matched exactly on `(point_id, face_id, segment_id)`: mismatches = 0. Positive-face counts were stable and equal: 53912.

## Interpretation

- End-to-end RTDL OptiX is 10.97x faster than RTDL Embree for the same CDB face-id count contract.
- Native traversal alone shows the RT-core effect more directly: OptiX 0.085593 ms vs Embree 10.426036 ms, or 121.81x faster traversal.
- The RTDL OptiX wall median is much larger than its native traversal median because this route still pays host/GPU staging, launch, and count-return overhead. That is why RayJoin's author implementation is 1.85x faster than RTDL OptiX even though both use RT hardware.
- This supports the paper's PIP claim under the right contract: RT cores help CDB point-location strongly. The earlier flat/no-speedup PIP results were measuring a more generic RTDL path rather than this RayJoin-specialized closest-hit face-id route.

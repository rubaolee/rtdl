# Goal4514 / V3 M118 RayJoin Mixed-Explicit Clean-Target Audit

## Conclusion

Spatial RayJoin is closed as a V3 mixed-explicit clean target, not as a primitive-only or public-speedup app. Use Numba for bounded PIP one-shot, RTDL/OptiX prepared batch execution for repeated PIP, and RTDL/OptiX prepared scalar/active-count primitives for LSI and overlay active count. The authors-code comparison remains scalar-count-only: RTDL/OptiX wins LSI, RayJoin RT wins PIP, and full RayJoin paper reproduction plus Section 5.7 8/8 overlay wording remain blocked.

## Current Route

- Decision: `mixed_explicit`.
- Partner policy: `mixed_explicit_user_choice`.
- Primitive contract: `prepared point/closed-shape batch count, segment-pair exact count, shape-pair active count`.
- Reader decision: Use Numba for bounded PIP one-shot; use RTDL/OptiX prepared primitives for repeated PIP, LSI scalar count, and overlay active count.
- User guidance: Do not auto-dispatch. Ask the user which contract they are running: bounded PIP one-shot currently favors Numba, while LSI/overlay and repeated PIP favor RTDL/OptiX.
- M113 reading: Spatial RayJoin uses explicit prepared PIP batch execution and prepared scalar/active-count primitives. The unsafe PIP CUDA graph replay path is quarantined after Goal4451, and M113 prepared graph chunk execution is not the current promoted RayJoin route.

## Recommended Route Matrix

| Contract | Recommended route | Key evidence | Reading |
| --- | --- | ---: | --- |
| PIP one-shot scalar count | Numba CUDA JIT scalar count | 0.23x RTDL/OptiX vs Numba | bounded one-shot PIP favors Numba, not current RTDL/OptiX |
| PIP repeated-request scalar count | RTDL/OptiX prepared point/closed-shape batch executor | 0.145265 ms/request | use batch executor; do not use quarantined CUDA graph replay |
| LSI scalar count | RTDL/OptiX prepared segment-pair count | 262.393x RTDL/OptiX vs Numba | strong RTDL/OptiX-favorable route |
| Overlay active count | RTDL/OptiX prepared shape-pair active count | 210.183x RTDL/OptiX vs Numba | strong RTDL/OptiX-favorable active-count route |

## Authors-Code Scalar-Count Comparison

| Workload/backend | RayJoin RT query ms | RTDL hot query ms | RayJoin RT / RTDL | Readout |
| --- | ---: | ---: | ---: | --- |
| lsi:optix | 0.819 | 0.336 | 2.437x | RTDL backend faster than RayJoin RT for this scalar-count contract |
| lsi:embree | 0.819 | 14.539 | 0.056x | RayJoin RT faster than RTDL backend for this scalar-count contract |
| pip:optix | 0.83 | 12.034 | 0.069x | RayJoin RT faster than RTDL backend for this scalar-count contract |
| pip:embree | 0.83 | 14.168 | 0.059x | RayJoin RT faster than RTDL backend for this scalar-count contract |

## RTDL OptiX vs RTDL Embree

| Row | Contract | Speedup | Reading |
| --- | --- | ---: | --- |
| spatial_rayjoin_lsi | public_cdb_lsi_count | 29.93x | Safe as a prepared segment-pair scalar-count comparison after fresh artifacts pass the stale guard. |
| spatial_rayjoin_pip | public_cdb_pip_count | 1.10x | Safe as a prepared point-in-polygon scalar-count comparison after fresh artifacts pass the stale guard. |

## Section 5.7 Overlay Boundary

- Complete overlay pairs: 2/8.
- Incomplete overlay pairs: 6/8.
- Timing caveat: Paper Table 4 values are historical reference numbers. Local author_rt rows are measured process wall times. RTDL rows are warm-cache medians under the selected protocol.

| Pair | RTDL OptiX total sec | RTDL Embree total sec | OptiX-vs-Embree | Count match |
| --- | ---: | ---: | ---: | --- |
| County x Zipcode | 5.7823 | 15.1211 | 2.62x | True |
| Block x Water | 28.6499 | 53.7928 | 1.88x | True |

## Cleanup Decisions

- Overlay active-count same-contract row: active count 174, counts match `True`, row materialization avoided `True`.
- PIP graph replay: unvalidated `failed_closed_before_native_prepare`, validated `failed_closed_native_prepare`; use the batch executor.
- No public speedup, full RayJoin reproduction, whole-app, automatic partner, or app-specific native-engine claim is authorized by this packet.

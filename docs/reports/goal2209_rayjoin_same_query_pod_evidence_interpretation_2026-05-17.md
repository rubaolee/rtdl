# Goal2209: RayJoin Same-Query Pod Evidence Interpretation

Status: evidence imported for review; no public win claim authorized.

## Evidence Source

- Pod: `root@69.30.85.202 -p 22064`
- GPU: NVIDIA RTX A5000, driver 570.211.01, CUDA 12.8
- RTDL commit under test: `7c80b901b6326e8c4e15e7bbeae7f97f786cb352`
- RayJoin commit: `02bf6220d6d20b04af77ee20364eced75cc029c9`
- Imported artifact summary: `docs/reports/goal2209_rayjoin_same_query_pod_evidence_2026-05-17.json`
- Imported compact artifact directory: `docs/reports/goal2209_rayjoin_same_query_pod_evidence/`
- Full RayJoin query streams were hashed but not copied into the repository.

## What Was Measured

RayJoin was patched only to export the exact generated query stream. RTDL then consumed the same stream through the Goal2192 same-query adapter and ran the same workload with `cpu`, `embree`, and `optix` backends. The declared parity reference was native `cpu`, not the slow Python reference.

This is a same-query and same-row-contract test. It is not yet a full RayJoin paper reproduction, because RayJoin's reported `Query` phase and RTDL's Python runtime call do not have identical phase boundaries.

## Results

| Workload | RayJoin grid query ms | RayJoin LBVH query ms | RayJoin RT query ms | RayJoin RT launches | RTDL CPU sec | RTDL Embree sec | RTDL OptiX sec | RTDL OptiX/CPU | RTDL OptiX/Embree |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| LSI | 4.6893 | 1.52763 | 0.611623 | 4 | 1.153435 | 106.047649 | 0.083064 | 0.072x | 0.001x |
| PIP | 16.8404 | 10.2307 | 0.575066 | 4 | 2.758106 | 0.106248 | 4.107544 | 1.489x | 38.660x |

All RTDL rows matched the native CPU reference:

| Workload | Query count | Reference rows | CPU parity | Embree parity | OptiX parity |
| --- | ---: | ---: | --- | --- | --- |
| LSI | 100000 | 8921 | pass | pass | pass |
| PIP | 100000 | 8686 | pass | pass | pass |

## Interpretation

Goal2207's chunked segment-pair launch fixed the LSI OptiX capacity blocker. The LSI OptiX path now completes the RayJoin-exported 100k-query stream with parity and runs much faster than RTDL's native CPU reference.

RTDL is still not RayJoin-competitive on this measurement. RayJoin's specialized RT query phase is roughly `0.612 ms` for LSI and `0.575 ms` for PIP, while RTDL's full same-stream OptiX runtime calls are roughly `83 ms` for LSI and `4108 ms` for PIP. The phase boundaries differ, but the gap is large enough that a public "RTDL beats RayJoin" claim is not supportable.

PIP is the clearest weak spot. RTDL Embree handles this same PIP stream in about `106 ms`, while RTDL OptiX takes about `4.1 s`. That points to an RTDL OptiX PIP lowering/runtime problem, not a RayJoin dataset problem. The likely issue is that the current generic OptiX point/primitive any-hit packet path still carries too much host/runtime overhead or an inefficient full-row/readback path for positive-hit PIP.

## Claim Boundary

Authorized:

- RTDL can consume RayJoin-exported same-query streams for LSI and PIP.
- RTDL `cpu`, `embree`, and `optix` produced parity-matching rows on the imported 100k-query streams.
- Goal2207 fixed the LSI OptiX `uint32_t` capacity failure for this run.

Not authorized:

- RTDL beats RayJoin.
- RTDL reproduces the full RayJoin paper performance study.
- Broad RT-core speedup.
- v2.0 release readiness.

## Next Work

1. Add a prepared/reused right-side scene path to the same-query RTDL measurement so the RTDL query phase can be separated from packing, upload, acceleration build, and pipeline setup.
2. Diagnose the PIP OptiX positive-hit path; it should not be slower than RTDL Embree on a stream where RayJoin RT is sub-millisecond.
3. Keep the RayJoin exported streams as hash-pinned external artifacts, not committed repository blobs.


# Goal2337: RTDL v2.1 RayJoin First-Hit Runtime Extension

**Date**: 2026-05-18  
**Status**: `v2.1-candidate-evidence-collected`  
**Verdict**: `accept-with-boundary`

## Purpose

Goal2335 proved that current RTDL v2.0 can express RayJoin `query=pip` semantics exactly with generic prepared segment-pair intersection, but it was much slower because it materialized every boundary crossing row and reduced millions of rows on the host.

Goal2337 adds the generic v2.1 primitive needed by that evidence: a prepared segment scene can answer one nearest/first segment witness per probe. RayJoin remains application-level Python logic; the OptiX engine only sees generic segment probes and generic prepared segment primitives.

## New Generic Primitive

The OptiX backend now exposes:

- `RtdlSegmentFirstHitRow`
- `rtdl_optix_run_prepared_segment_first_hit`
- `rtdl_optix_count_prepared_segment_first_hit`
- Python prepared-handle methods:
  - `PreparedOptixSegmentPairIntersection.first_hit_raw(...)`
  - `PreparedOptixSegmentPairIntersection.first_hit(...)`
  - `PreparedOptixSegmentPairIntersection.first_hit_count(...)`

The device kernel keeps one packed `(hit_t, primitive_index)` candidate per probe using a 64-bit atomic minimum. This is the v2.x device-resident grouped-continuation shape we wanted: one bounded witness per probe, not a full crossing table.

## RayJoin Same-Query Evidence

Pod: `root@69.30.85.175 -p 22114`, key `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`  
GPU: `NVIDIA RTX A5000, 570.211.01`  
OptiX SDK: `/root/vendor/optix-sdk`, tag `v8.1.0`  
CUDA build: `/usr/local/cuda-12`, `libnvrtc.so.12`  
Native library: `/root/rtdl_goal2333_clean/build/librtdl_optix.so`

Artifacts:

- `docs/reports/goal2337_v2_1_rayjoin_first_hit_pod/rtdl_first_hit_pip_compare_4096.json`
- `docs/reports/goal2337_v2_1_rayjoin_first_hit_pod/rtdl_first_hit_pip_compare_65536.json`

| Query count | RayJoin positives | RTDL positives | Missing | Extra | v2.0 query+reduce | v2.1 native query | v2.1 query+validation | v2.1 speedup vs v2.0 | v2.1 native / RayJoin query |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4,096 | 3,374 | 3,374 | 0 | 0 | 26.399 ms | 0.823 ms | 1.485 ms | 17.77x | 3.49x slower |
| 65,536 | 53,372 | 53,372 | 0 | 0 | 734.597 ms | 2.855 ms | 12.181 ms | 60.30x | 1.91x slower |

`v2.1 query+validation` includes the Python/NumPy positive-set validation used only to prove equality with RayJoin's exported result set. The native RTDL query is the relevant runtime primitive time.

## What Improved

v2.0 did this:

1. Run generic prepared segment-pair intersection.
2. Emit every crossing row.
3. Copy millions of rows to the host.
4. Reduce by probe/point id in Python.

v2.1 does this:

1. Run generic prepared segment first-hit traversal.
2. Keep one nearest witness per probe on device.
3. Emit only the bounded witness rows.
4. Let the Python application map probe ids to RayJoin point ids.

At 65,536 queries, the emitted rows drop from `2,320,729` crossing rows to `53,372` first-hit rows while preserving the exact RayJoin positive point set.

## Boundaries

This does authorize:

- RTDL v2.1 has a measured generic first-hit/nearest-boundary OptiX primitive.
- The RayJoin PIP support contract can be expressed with RTDL v2.1 using generic native traversal and Python application mapping.
- The measured same-query path is about `60.30x` faster than the v2.0 vertical-probe route at 65,536 queries.
- The native query time is within about `1.91x` of RayJoin's query time at 65,536 queries on this pod.

This does not authorize:

- A claim that RTDL beats RayJoin.
- A whole-RayJoin-paper reproduction claim.
- A broad spatial-join speedup claim.
- A v2.1 release button press without final required consensus.
- Any app-specific native RayJoin/PIP code inside the engine.

## v3.0 Boundary

This goal deliberately does not require user-defined shader injection. The remaining future v3.0 item is still user-extensible shader/code injection. The v2.1 primitive added here is generic runtime functionality: prepared segment first-hit and bounded witness emission.


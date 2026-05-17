# Goal2207: OptiX Segment-Pair Chunked Capacity Fix

Status: local implementation ready for pod validation.

## Why This Exists

Goal2198 r4 reached the same-query RayJoin pod run and completed the RayJoin side plus RTDL CPU/Embree LSI parity. The RTDL OptiX LSI replay then failed with:

```text
RuntimeError: segment-pair intersection output capacity exceeds uint32_t
```

The failure was not an SDK, CUDA, or pod setup issue. It exposed an RTDL OptiX implementation boundary: the generic segment-pair intersection path rejected a large query/reference Cartesian space before launching, even though the real candidate/output count for the RayJoin stream was small.

## Fix

`src/native/optix/rtdl_optix_workloads.cpp` now uses chunked OptiX segment-pair launches by left-side segment count whenever `left_count * right_count` would exceed the 32-bit per-launch candidate space.

The fix is intentionally generic and app-agnostic:

- it does not mention RayJoin, LSI, maps, counties, ZIPs, or any application-specific dataset;
- each chunk preserves the same OptiX custom-primitive traversal and exact host-side refinement;
- candidate records from all chunks are appended and deduplicated/refined by the existing finalizer;
- one chunk still enforces the 32-bit count contract, so oversized launches fail locally instead of overflowing silently.

## Claim Boundary

This fix only authorizes a rerun of the same-query pod evidence path. It does not authorize a release claim, a RayJoin performance win, a broad RTX speedup claim, or a whole-application claim. Those require completed r5-or-newer pod artifacts, imported evidence, and external review.

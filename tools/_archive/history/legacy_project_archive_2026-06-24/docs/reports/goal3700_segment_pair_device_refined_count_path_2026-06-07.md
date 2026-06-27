# Goal3700 Segment-Pair Device-Refined Count Path

Date: 2026-06-07

## Purpose

Goal3698 fixed the RayJoin same-source LSI correctness gap, but the corrected count-only route remained slow because it still downloaded candidate segment pairs and ran exact refinement on the host.

Goal3700 implements the next generic count-only optimization:

```text
OptiX candidate traversal -> device-side exact segment-pair count -> scalar count download
```

The row/witness route is intentionally unchanged.

## Change

Updated:

- `src/native/optix/rtdl_optix_workloads.cpp`

The prepared segment-pair count path now:

1. uploads the left segments in both float candidate form and exact `RtdlSegment` form,
2. reuses the prepared right-side float candidate buffer and a new prepared right-side exact `RtdlSegment` buffer,
3. emits conservative candidate records on the device,
4. launches a generic CUDA exact-refine count kernel over those candidate records,
5. downloads only the final scalar count.

The exact-refine kernel mirrors the existing host-side double-precision segment intersection predicate closely enough to preserve the count contract, but it is not a witness/materialization path.

## Boundaries

This is not an app-specific RayJoin hook:

- no RayJoin/CDB vocabulary is added,
- no app-specific branch is added,
- native ABI names are unchanged,
- row-output mode still uses the existing host exact materializer,
- the optimization applies only to the generic prepared segment-pair scalar count contract.

This report is an implementation note until NVIDIA pod evidence validates compile, count parity, and timing.

## Required Pod Evidence

Before this path can be treated as accepted, an NVIDIA pod must prove:

- `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk` succeeds,
- the focused segment-pair tests pass,
- same-source RayJoin LSI count remains `20860`,
- RTDL normalized pair-set parity remains available from the row path,
- the count-mode phase telemetry shows candidate download near zero,
- the count-mode total query time improves versus Goal3698,
- all claim-boundary flags remain false.

## Claim Boundary

This report does not authorize:

- release,
- default-route promotion,
- RTDL-beats-RayJoin claims,
- RayJoin paper reproduction claims,
- public speedup claims,
- broad RT-core claims,
- true zero-copy claims.

The only intended claim after pod validation is narrower:

```text
For prepared segment-pair scalar counts, exact candidate refinement can be performed on the device without changing the app-agnostic segment-pair contract.
```

## Supersession Note

Goal3701 later replaces this route as the selected scalar-count implementation with a one-pass exact-count OptiX pipeline. Goal3700 remains useful as the intermediate implementation note and fallback concept: it proved that host exact refinement could be moved to the device, but it still retained a candidate-write pass.


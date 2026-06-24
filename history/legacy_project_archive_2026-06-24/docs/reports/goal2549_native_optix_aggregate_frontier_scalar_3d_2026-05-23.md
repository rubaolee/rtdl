# Goal2549 Aggregate-Frontier Native Design Rejection

Date: 2026-05-23

## Decision

The attempted native OptiX symbol for
`generic_aggregate_frontier_inverse_square_scalar_sum_3d_v1` is rejected as an
RTDL engine primitive.

Reason: the native implementation hardcoded the Barnes-Hut-style reduction:

`source_weight * target_or_aggregate_weight / distance^2`

Even though the code avoided Barnes-Hut names, the mathematical operation is
workload-shaped and belongs outside the app-independent engine boundary. Under
the RTDL principle, native engines may know generic traversal, hit collection,
and primitive reductions, but must not embed benchmark-specific force laws.

## Correction Applied

The following were removed from the supported source tree:

- Native C ABI export:
  `rtdl_optix_aggregate_frontier_inverse_square_scalar_sum_3d_device`
- Native CUDA-driver kernel for inverse-square scalar aggregation.
- Python runtime wrapper and public export for that symbol.
- Goal2549 benchmark runner and pod JSON artifacts for the rejected native
  primitive.

## What Remains Valid

The Goal2547 Torch/CUDA prototype remains useful as app/benchmark-side
diagnostic evidence. It is not an RTDL engine primitive and must not be used as
evidence that the engine has a general aggregate-frontier implementation.

## Next Acceptable Design

A compliant native-engine direction should separate mechanics from math:

- Engine-level primitive: generic aggregate-frontier traversal or frontier-row
  production over prepared tree/device arrays.
- Engine-level outputs: accepted aggregate IDs, exact member IDs, per-source
  ranges/counts, diagnostics, or app-neutral hit/frontier flags.
- App/partner-level math: inverse-square scalar/vector accumulation, force law,
  timestep integration, and any benchmark-specific interpretation.

If we want native fused accumulation later, it needs a reviewed operator
plug-in/partner mechanism rather than hardcoded force math in the engine.

## Claim Boundary

- `native_engine_app_specific`: rejected
- `public_speedup_claim_authorized`: false
- `rt_core_traversal`: false
- `supported_engine_primitive`: false
- `status`: rejected design; not part of release/support surface

# Goal2823 Device-Side Batch Partial Reduction

Date: 2026-05-31

Verdict: implementation-pending-pod-evidence.

Goal2823 continues the Goal2821/Goal2822 heterogeneous prepared-aggregate batch
path. Goal2822 fused the per-request block-partial kernels into one 2D-grid
launch, but still downloaded every block partial and reduced those partials on
the host. Goal2823 adds a generic device-side final reduction kernel so the host
downloads only one aggregate row per request.

This is app-agnostic. The vocabulary remains fixed-radius neighbors,
ranked-summary aggregates, request-indexed block partials, and device-side
partial reduction. No RTNN native ABI or benchmark-specific branch is added.

## Change

- Added `fixed_radius_neighbors_3d_ranked_aggregate_partials_reduce`.
- Added the corresponding module function handle:
  `g_frn3d_ranked_aggregate_partials_reduce`.
- The block-partial batch path now launches:
  1. the fused request/query block kernel;
  2. a device-side partial reducer with one block per request;
  3. one compact aggregate download of `request_count` rows.

## Claim Boundary

- No public RTDL-beats-CuPy claim is authorized.
- No RTDL-beats-RTNN-paper claim is authorized.
- No paper reproduction claim is authorized.
- No broad RT-core speedup claim is authorized.
- No whole-app speedup claim is authorized.
- No v2.5 release claim is authorized.
- No performance conclusion is authorized until clean pod artifacts compare the
  device-side partial reducer against Goal2822.

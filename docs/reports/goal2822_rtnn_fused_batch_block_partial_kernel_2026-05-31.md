# Goal2822 Fused Batch Block-Partial Kernel

Date: 2026-05-31

Verdict: implementation-pending-pod-evidence.

Goal2822 targets the remaining overhead inside the Goal2821 heterogeneous
prepared-aggregate batch path. Goal2821 reduced host/native crossings, but the
native block-partial batch still launched one aggregate kernel per request.
Goal2822 adds a fused 2D-grid block-partial kernel: `blockIdx.x` indexes query
blocks and `blockIdx.y` indexes aggregate requests.

This is app-agnostic. The native vocabulary remains fixed-radius neighbors,
prepared queries, ranked-summary aggregates, request radii, `k_max` values, and
block partials. No RTNN-specific ABI or benchmark branch is introduced.

## Change

- Added
  `fixed_radius_neighbors_3d_grid_ranked_summary_aggregate_f32_blocks_batch`.
- Added the corresponding module function handle:
  `g_frn3d_grid_ranked_summary_aggregate_f32_blocks_batch`.
- The prepared-query aggregate batch path now uploads compact request arrays
  (`float radii`, `uint32_t k_values`) and launches one 2D-grid kernel for the
  small-row block-partial batch path.
- The host reduction layout remains `request_index * block_count + block_index`,
  so result semantics stay identical to Goal2821.

## Claim Boundary

- No public RTDL-beats-CuPy claim is authorized.
- No RTDL-beats-RTNN-paper claim is authorized.
- No paper reproduction claim is authorized.
- No broad RT-core speedup claim is authorized.
- No whole-app speedup claim is authorized.
- No v2.5 release claim is authorized.
- No performance conclusion is authorized until clean pod artifacts compare
  the fused batch kernel against Goal2821.

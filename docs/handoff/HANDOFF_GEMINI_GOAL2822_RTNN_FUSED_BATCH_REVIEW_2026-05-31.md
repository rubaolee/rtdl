# Handoff: Goal2822 RTNN Fused Batch Block-Partial Review

Please independently review Goal2822 as a distinct external AI reviewer. This
review should consider Goal2821 and Goal2822 together because Goal2822 hardens
the heterogeneous batch path introduced by Goal2821.

## Context

Goal2821 added runner support and pod evidence for heterogeneous prepared
aggregate sweeps: four radius/K requests over the same resident prepared
search/query handles. Goal2822 then changed the small-row native batch
implementation from one block-partial kernel launch per request to one fused
2D-grid kernel launch where `blockIdx.y` is the aggregate request index.

## Files To Inspect

- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `scripts/goal2348_rtnn_v2_2_external_runner.py`
- `tests/goal2822_rtnn_fused_batch_block_partial_kernel_test.py`
- `tests/goal2821_rtnn_heterogeneous_batched_aggregate_requests_test.py`
- `docs/reports/goal2822_rtnn_fused_batch_block_partial_kernel_2026-05-31.md`
- `docs/reports/goal2822_rtnn_fused_batch_block_partial_kernel_pod/goal2822_summary.json`
- `docs/reports/goal2821_rtnn_heterogeneous_batched_aggregate_requests_2026-05-31.md`
- `docs/reports/goal2821_rtnn_heterogeneous_batched_aggregate_requests_pod/goal2821_summary.json`

## Facts To Verify

- The new native kernel is generic:
  `fixed_radius_neighbors_3d_grid_ranked_summary_aggregate_f32_blocks_batch`.
- The kernel uses `blockIdx.y` as the aggregate request index and writes partials
  as `request_index * gridDim.x + blockIdx.x`.
- The batch path uploads compact request arrays (`float radii`,
  `uint32_t k_values`) and launches the fused batch kernel once for the
  small-row block-partial path.
- Goal2822 keeps the existing host reduction layout, so semantics match
  Goal2821.
- Clean RTX A5000 pod evidence is from commit
  `ef2204808d9997729b194d743f76a8508fd84a85` with `source_dirty: []`.
- Fused batch results exactly matched four sequential single aggregate calls.
- The measured improvement versus Goal2821 batch median is about 1.105x at 32K
  and 1.085x at 65K.
- All public/release/paper/single-request speedup claim flags remain closed.

## Review Questions

1. Is Goal2822 a valid generic v2.5 runtime optimization rather than an
   RTNN-specific shortcut?
2. Does the fused 2D-grid kernel preserve the correctness contract and output
   layout from Goal2821?
3. Are the pod artifacts sufficient for `accept-with-boundary`?
4. Does the report avoid overclaiming the modest 8-11% batch improvement?
5. Should the next target be CUDA graph replay, device-side final reduction of
   block partials, or event-ordered partner chaining?

## Required Output

Write the review to:

`docs/reviews/goal2822_gemini_review_rtnn_fused_batch_block_partial_2026-05-31.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

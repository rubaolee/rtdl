# Goal2771 Consensus - Event-Ordered Grouped Hit-Stream Reduction Consumer

Date: 2026-05-31

Verdict: accept-with-boundary.

Codex + Gemini consensus accepts Goal2771 with boundary.

## Evidence

Codex implemented a bounded grouped-reduction consumer over the existing generic
OptiX hit stream:

- grouping key: generic hit-row `ray_id`;
- output columns: `group_hit_counts`, `group_primitive_id_sum`,
  `group_primitive_id_xor`;
- ordering: OptiX producer stream records a Torch CUDA event, then a separate
  CuPy consumer stream waits with `streamWaitEvent`;
- scope: `bounded_event_ordered_grouped_ray_id_reduction_consumer_only`;
- no host materialization of hit rows or grouped output columns before the
  consumer kernel;
- no true-zero-copy, public speedup, arbitrary partner continuation, release, or
  unbounded stream claim.

Pod validation on `root@69.30.85.171:22167`, clean checkout
`/root/rtdl_goal2771` at `b00b5eec` plus Goal2771 patch:

- `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`: OK.
- Goal2771 focused subset without review/consensus assertion: 5 tests OK.
- Goal2764-Goal2770 surrounding focused regression: 30 tests OK.
- Corrected v2.5 hit-stream regression through Goal2770: 47 tests OK.

The Goal2771 smoke validated grouped device outputs:

- `group_hit_counts = [2, 0, 2]`;
- `group_primitive_id_sum = [1, 0, 1]`;
- `group_primitive_id_xor = [1, 0, 1]`.

## External Review

Gemini review:
`docs/reviews/goal2771_gemini_review_hit_stream_event_ordered_grouped_reduction_2026-05-31.md`

Gemini verdict: `accept-with-boundary`.

Gemini accepted the generic `ray_id` grouping boundary, CUDA-event
cross-stream ordering, avoidance of premature row/output host materialization,
bounded metadata/non-claim discipline, and the narrow smoke coverage.

## Boundary

This consensus is not an unbounded stream or arbitrary continuation approval.
It only accepts the narrow grouped hit-stream consumer proven here:

`async_partner_continuation_authorization_scope =
bounded_event_ordered_grouped_ray_id_reduction_consumer_only`.

It does not authorize true zero-copy, public speedup claims, broader RTDL v2.5
release claims, or app-specific native continuations.

# Goal2772 Consensus - Richer Event-Ordered Grouped Hit-Stream Reductions

Date: 2026-05-31

Verdict: accept-with-boundary.

Codex + Gemini consensus accepts Goal2772 with boundary.

## Evidence

Codex extended the bounded Goal2771 grouped hit-stream reduction consumer with
richer generic output columns:

- `group_primitive_id_min`;
- `group_primitive_id_max`;
- `group_first_hit_row_index`;
- `group_last_hit_row_index`;
- `group_first_primitive_id`;
- `group_last_primitive_id`.

The grouping key remains the generic hit-stream `ray_id` column. All reduced
values come from generic hit-stream columns and caller-owned output buffers.
There is no app/domain vocabulary in the primitive contract.

Pod validation on `root@69.30.85.171:22167`, clean checkout
`/root/rtdl_goal2772` at `1faebe8e` plus Goal2772 patch:

- `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`: OK.
- Goal2772 focused subset without review/consensus assertion: 6 tests OK.
- Corrected v2.5 hit-stream regression through Goal2772: 59 tests OK.

The live smoke observed unsorted hit-stream row order:

- `ray_ids = [0, 2, 0, 2]`;
- `primitive_ids = [0, 0, 1, 1]`.

The richer grouped reductions correctly reflected that row order:

- `group_hit_counts = [2, 0, 2]`;
- `group_primitive_id_min = [0, -1, 0]`;
- `group_primitive_id_max = [1, -1, 1]`;
- `group_first_hit_row_index = [0, -1, 1]`;
- `group_last_hit_row_index = [2, -1, 3]`;
- `group_first_primitive_id = [0, -1, 0]`;
- `group_last_primitive_id = [1, -1, 1]`.

Initial pod testing found and fixed a real initializer bug:
`group_last_hit_row_index` must initialize to `0` before the `atomicMax` pass.
Empty groups are finalized back to the signed-visible `-1` sentinel.

## External Review

Gemini review:
`docs/reviews/goal2772_gemini_review_hit_stream_event_ordered_grouped_richer_reductions_2026-05-31.md`

Gemini verdict: `accept-with-boundary`.

Gemini accepted the generic `ray_id` boundary, richer min/max and first/last
row-order outputs, CUDA-event ordered CuPy consumer, no premature host
materialization of hit rows or grouped output columns, honest row-order wording,
and bounded metadata/non-claim discipline.

## Boundary

This consensus is not an unbounded stream or arbitrary continuation approval.
It only accepts the narrow richer grouped hit-stream consumer proven here:

`async_partner_continuation_authorization_scope =
bounded_event_ordered_grouped_ray_id_reduction_consumer_only`.

It does not authorize true zero-copy, public speedup claims, broader RTDL v2.5
release claims, or app-specific native continuations.

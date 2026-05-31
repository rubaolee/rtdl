# Goal2772 - Richer Event-Ordered Grouped Hit-Stream Reductions

Date: 2026-05-31

Status: implemented and accepted with boundary by Codex + Gemini consensus.

## Purpose

Goal2771 added a bounded CuPy grouped-reduction consumer over the generic OptiX
hit stream, grouped by the generic `ray_id` column. Goal2772 keeps the same
public method and buffer pattern but makes the grouped output more useful:
callers now get generic min/max and first/last row-order reductions in addition
to count/sum/xor.

This is still a primitive/runtime step, not an app workload. The grouping key is
still `ray_id`, and every reduced value comes from generic hit-stream columns.

## Added Output Columns

`PreparedOptixHitStreamGroupedReductionBuffers` now owns these CUDA int64
columns:

- `group_hit_counts`
- `group_primitive_id_sum`
- `group_primitive_id_xor`
- `group_primitive_id_min`
- `group_primitive_id_max`
- `group_first_hit_row_index`
- `group_last_hit_row_index`
- `group_first_primitive_id`
- `group_last_primitive_id`

Empty groups use `-1` as the signed Torch-visible sentinel for min/max and
first/last outputs.

## Execution Contract

The execution ordering is unchanged from Goal2771:

1. OptiX produces hit rows into caller-owned device columns on a producer CUDA
   stream.
2. Torch records a CUDA event on the producer stream after enqueue.
3. A separate CuPy consumer stream waits on that CUDA event.
4. The CuPy RawKernel reduces the stored hit rows by `ray_id` and writes grouped
   output columns on device.
5. Only the small summary is materialized after the consumer stream completes.

## Boundary

Accepted scope:

- OptiX hit-stream producer.
- CuPy RawKernel consumer.
- Cross-stream ordering through a CUDA event.
- Grouping by generic `ray_id`.
- Bounded grouped reductions over stored hit rows.
- Generic primitive-id count/sum/xor/min/max/first/last reductions.
- Caller-owned device output columns.

Explicit non-claims:

- This does not authorize true zero-copy.
- This does not authorize public speedup claims.
- This does not authorize arbitrary partner continuation.
- This does not authorize app-specific native continuations.
- This does not authorize an unbounded stream or unbounded grouped output.
- Query rays are still packed on the host before the native launch.

## Validation Plan

Focused validation:

`PYTHONPATH=src:. python3 -m unittest tests.goal2772_hit_stream_event_ordered_grouped_richer_reductions_test tests.goal2771_hit_stream_event_ordered_grouped_reduction_consumer_test tests.goal2770_hit_stream_event_ordered_row_reduction_consumer_test`

Corrected v2.5 hit-stream regression:

`PYTHONPATH=src:. python3 -m unittest tests.goal2756_reusable_hit_stream_device_output_buffers_test tests.goal2758_reusable_hit_stream_buffer_perf_probe_test tests.goal2760_hit_stream_async_promotion_requirements_test tests.goal2762_hit_stream_device_status_buffers_test tests.goal2764_hit_stream_same_stream_status_consumer_test tests.goal2767_hit_stream_async_input_upload_test tests.goal2768_hit_stream_same_stream_row_window_consumer_test tests.goal2769_hit_stream_same_stream_row_reduction_consumer_test tests.goal2770_hit_stream_event_ordered_row_reduction_consumer_test tests.goal2771_hit_stream_event_ordered_grouped_reduction_consumer_test tests.goal2772_hit_stream_event_ordered_grouped_richer_reductions_test`

## Current Result

Local syntax/static checks on Windows:

- `py -3 -m py_compile src/rtdsl/optix_runtime.py tests/goal2772_hit_stream_event_ordered_grouped_richer_reductions_test.py`:
  OK.
- Goal2772 static/report subset: 5 tests OK.
- Full local Goal2772 suite on Windows without a configured local OptiX library:
  6 tests OK / 1 live CUDA smoke skipped.

Pod validation on `root@69.30.85.171:22167`, clean checkout
`/root/rtdl_goal2772` at `1faebe8e` plus the Goal2772 patch:

- `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`: OK.
- Goal2772 focused subset without the review/consensus assertion:
  6 tests OK.
- Corrected v2.5 hit-stream regression through Goal2772:
  59 tests OK.
- Full Goal2772 test after external review and consensus files were present:
  7 tests OK.
- Full corrected v2.5 hit-stream regression including full Goal2772:
  60 tests OK.

The live smoke observed the stored hit-stream row order:

- `ray_ids = [0, 2, 0, 2]`.
- `primitive_ids = [0, 0, 1, 1]`.

The richer grouped reductions produced:

- `group_hit_counts = [2, 0, 2]`.
- `group_primitive_id_min = [0, -1, 0]`.
- `group_primitive_id_max = [1, -1, 1]`.
- `group_first_hit_row_index = [0, -1, 1]`.
- `group_last_hit_row_index = [2, -1, 3]`.
- `group_first_primitive_id = [0, -1, 0]`.
- `group_last_primitive_id = [1, -1, 1]`.

During initial pod testing, the `group_last_hit_row_index` initializer bug was
found and fixed: it must initialize to `0`, not the `-1` sentinel, before the
`atomicMax` pass. Empty groups are still finalized back to `-1`.

External review:

- Gemini review:
  `docs/reviews/goal2772_gemini_review_hit_stream_event_ordered_grouped_richer_reductions_2026-05-31.md`
  with verdict `accept-with-boundary`.
- Consensus:
  `docs/reports/goal2772_hit_stream_event_ordered_grouped_richer_reductions_consensus_2026-05-31.md`.

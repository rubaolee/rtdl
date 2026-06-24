# Goal2771 - Event-Ordered Grouped Hit-Stream Reduction Consumer

Date: 2026-05-31

Status: implemented and accepted with boundary by Codex + Gemini consensus.

## Purpose

Goal2770 proved that an OptiX producer stream can hand off a generic hit stream
to a separate CuPy consumer stream through a CUDA event. Goal2771 extends that
bounded contract from a single whole-stream row summary to grouped reductions
over the same event-ordered stream.

The grouping key is the generic hit-row `ray_id` column. This is intentionally
not an app/domain key. It lets a caller reduce rows per query/ray without adding
app-specific native continuations.

## Implementation

`src/rtdsl/optix_runtime.py` now adds:

- `PreparedOptixHitStreamGroupedReductionBuffers`, a caller-owned set of CUDA
  output columns:
  - `group_hit_counts`
  - `group_primitive_id_sum`
  - `group_primitive_id_xor`
- `_run_hit_stream_event_ordered_grouped_ray_id_reduction_cupy(...)`, a CuPy
  RawKernel consumer that waits on the producer CUDA event before reading the
  device-resident hit stream.
- `PreparedOptixStaticTriangleScene3D.ray_triangle_hit_stream_event_ordered_grouped_ray_id_reduction(...)`,
  which launches the existing generic hit-stream producer, records a Torch CUDA
  event on the producer stream, then runs the CuPy grouped reduction on a
  separate event-ordered consumer stream.

The consumer kernel writes grouped output columns on device and only
materializes the small summary after the consumer stream has completed.

The runtime smoke uses `deduplicate_primitives=False` so the grouped proof
observes per-ray hit rows. The default producer de-duplication policy remains
unchanged.

## Contract

Accepted scope:

- OptiX hit-stream producer.
- CuPy RawKernel partner consumer.
- cross-stream ordering through a CUDA event.
- Grouping by the generic `ray_id` hit-stream column.
- Bounded grouped reductions over stored hit rows.
- Caller-owned device output columns.

Explicit non-claims:

- This does not authorize true zero-copy.
- This does not authorize public speedup claims.
- This does not authorize arbitrary partner continuation.
- This does not authorize an unbounded stream or unbounded output growth.
- Query rays are still packed on the host before the native launch.

## Validation Plan

Focused validation:

`PYTHONPATH=src:. python3 -m unittest tests.goal2771_hit_stream_event_ordered_grouped_reduction_consumer_test tests.goal2770_hit_stream_event_ordered_row_reduction_consumer_test tests.goal2769_hit_stream_same_stream_row_reduction_consumer_test tests.goal2768_hit_stream_same_stream_row_window_consumer_test tests.goal2767_hit_stream_async_input_upload_test tests.goal2764_hit_stream_same_stream_status_consumer_test`

Regression slice:

`PYTHONPATH=src:. python3 -m unittest tests.goal2756_reusable_hit_stream_device_output_buffers_test tests.goal2758_reusable_hit_stream_buffer_perf_probe_test tests.goal2760_hit_stream_async_promotion_requirements_test tests.goal2762_hit_stream_device_status_buffers_test tests.goal2764_hit_stream_same_stream_status_consumer_test tests.goal2767_hit_stream_async_input_upload_test tests.goal2768_hit_stream_same_stream_row_window_consumer_test tests.goal2769_hit_stream_same_stream_row_reduction_consumer_test tests.goal2770_hit_stream_event_ordered_row_reduction_consumer_test tests.goal2771_hit_stream_event_ordered_grouped_reduction_consumer_test`

## Current Result

Local syntax/static checks on Windows:

- `py -3 -m py_compile src/rtdsl/optix_runtime.py tests/goal2771_hit_stream_event_ordered_grouped_reduction_consumer_test.py`:
  OK.
- Goal2771 static/report subset: 4 tests OK.
- Full local Goal2771 suite on Windows without a configured local OptiX library:
  5 tests OK / 1 live CUDA smoke skipped.

Pod validation on `root@69.30.85.171:22167`, clean checkout
`/root/rtdl_goal2771` at `b00b5eec` plus the Goal2771 patch:

- `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`: OK.
- Goal2771 focused subset without the review/consensus assertion: 5 tests OK.
- Surrounding focused regression:
  `tests.goal2770_hit_stream_event_ordered_row_reduction_consumer_test`
  `tests.goal2769_hit_stream_same_stream_row_reduction_consumer_test`
  `tests.goal2768_hit_stream_same_stream_row_window_consumer_test`
  `tests.goal2767_hit_stream_async_input_upload_test`
  `tests.goal2764_hit_stream_same_stream_status_consumer_test`:
  30 tests OK.
- Corrected v2.5 hit-stream regression:
  `tests.goal2756_reusable_hit_stream_device_output_buffers_test`
  `tests.goal2758_reusable_hit_stream_buffer_perf_probe_test`
  `tests.goal2760_hit_stream_async_promotion_requirements_test`
  `tests.goal2762_hit_stream_device_status_buffers_test`
  `tests.goal2764_hit_stream_same_stream_status_consumer_test`
  `tests.goal2767_hit_stream_async_input_upload_test`
  `tests.goal2768_hit_stream_same_stream_row_window_consumer_test`
  `tests.goal2769_hit_stream_same_stream_row_reduction_consumer_test`
  `tests.goal2770_hit_stream_event_ordered_row_reduction_consumer_test`:
  47 tests OK.
- Full Goal2771 test after external review and consensus files were present:
  6 tests OK.
- Full corrected v2.5 hit-stream regression including Goal2771:
  53 tests OK.

The Goal2771 live smoke verifies:

- 4 stored hit rows from two hitting rays and one miss ray.
- `group_hit_counts = [2, 0, 2]`.
- `group_primitive_id_sum = [1, 0, 1]`.
- `group_primitive_id_xor = [1, 0, 1]`.
- `producer_consumer_stream_ordering = cuda_event_cross_stream`.
- `async_partner_continuation_authorization_scope =
  bounded_event_ordered_grouped_ray_id_reduction_consumer_only`.
- `true_zero_copy_authorized = False`.
- `public_speedup_claim_authorized = False`.

External review:

- Gemini review:
  `docs/reviews/goal2771_gemini_review_hit_stream_event_ordered_grouped_reduction_2026-05-31.md`
  with verdict `accept-with-boundary`.
- Consensus:
  `docs/reports/goal2771_hit_stream_event_ordered_grouped_reduction_consumer_consensus_2026-05-31.md`.

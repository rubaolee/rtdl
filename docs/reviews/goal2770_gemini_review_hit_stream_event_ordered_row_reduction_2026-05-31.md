# Independent Gemini Review for Goal2770: Hit-Stream Event-Ordered Row Reduction

**Date:** 2026-05-31

**Verdict:** `accept-with-boundary`

**Short Technical Reasoning:**
Goal2770 successfully implements and verifies an event-ordered cross-stream row reduction for the generic hit-stream path. The OptiX producer enqueues on a Torch CUDA stream, records an event, and a separate CuPy consumer stream correctly waits on this event before executing the row-reduction kernel. The implementation adheres to the stated boundaries regarding zero-copy, public speedup, and general release claims. The tests accurately reflect these boundaries.

## Answers to Required Review Questions:

1.  **Does Goal2770 actually record a Torch CUDA event after producer enqueue and make a separate CuPy stream wait on that event before launching the row-reduction kernel?**
    Yes. The `ray_triangle_hit_stream_event_ordered_row_reduction_summary` method in `src/rtdsl/optix_runtime.py` creates a `torch.cuda.Event` and records it on the `producer_stream` after the OptiX producer enqueue. It then passes the raw `producer_event.cuda_event` pointer to the `_run_hit_stream_event_ordered_row_reduction_summary_cupy` helper function. This helper creates a `cp.cuda.Stream(non_blocking=True)` and calls `cupy.cuda.runtime.streamWaitEvent` on the consumer stream, waiting for the producer event, before launching the row-reduction kernel. This is further validated by `tests/goal2770_hit_stream_event_ordered_row_reduction_consumer_test.py`.

2.  **Does the Python method preserve the async native owner, producer stream, and producer event lifetimes until after the consumer finishes?**
    Yes. The `torch.cuda.Event` object is created and held within the scope of the `ray_triangle_hit_stream_event_ordered_row_reduction_summary` function. The `_run_hit_stream_event_ordered_row_reduction_summary_cupy` helper synchronizes the `consumer_stream` before returning the `summary` to the caller. This ensures that the producer event remains alive and valid during the entire asynchronous operation until the consumer has completed its work and the results are materialized. The `device_columns` (output buffers) are passed by reference and are managed by the caller, preventing premature closure.

3.  **Are metadata/report boundaries honest: `producer_consumer_stream_ordering = cuda_event_cross_stream`, `cuda_event_cross_stream_ordering_proven = True`, `cuda_event_wait_inserted_before_consumer = True`, `bounded_event_ordered_row_reduction_consumer_only`, `query_rays_still_packed_on_host = True`, and no true-zero-copy or public speedup claim?**
    Yes. Both the `metadata` dictionary returned by the `ray_triangle_hit_stream_event_ordered_row_reduction_summary` method and the `docs/reports/goal2770_hit_stream_event_ordered_row_reduction_consumer_2026-05-31.md` explicitly declare these boundaries and claims. Specifically, `true_zero_copy_authorized` and `public_speedup_claim_authorized` are set to `False`, and `query_rays_still_packed_on_host` is `True`. The `async_partner_continuation_authorization_scope` is correctly set to `bounded_event_ordered_row_reduction_consumer_only`.

4.  **Do the tests cover the exact contract without turning this into a broad partner-continuation or release claim?**
    Yes. The tests in `tests/goal2770_hit_stream_event_ordered_row_reduction_consumer_test.py` are focused on verifying the core event-ordered cross-stream functionality, the presence and correct values of the metadata flags (`true_zero_copy_authorized=False`, `public_speedup_claim_authorized=False`, `bounded_event_ordered_row_reduction_consumer_only`), and a basic smoke test of the runtime. They do not extend to broader claims of arbitrary partner continuation or release readiness.

5.  **Is there any hidden host sync or app-specific engine logic introduced by this patch?**
    No. The only host synchronization identified is `consumer_stream.synchronize()` which occurs explicitly after the consumer kernel finishes, for the purpose of materializing the final summary on the host. This is consistent with the stated boundaries and is not considered hidden. The metadata flags `host_scalar_read_before_consumer: False` and `host_row_materialization_before_consumer: False` confirm no such operations occur prematurely. No app-specific engine logic beyond the scope of a generic hit-stream row reduction is introduced.

## Blocking Issues:
None.

## Non-blocking Follow-up Debt:
None identified for this specific goal's scope. The report itself notes important remaining limits (query rays still packed on host, bounded reduction, final summary synchronization, richer grouped reductions, multi-partner conformance) which are explicitly out of scope for Goal2770.

## Statement of Independence:
This is an independent Gemini review and not a Codex self-review.

# Goal2760 Hit-Stream Async Promotion Requirements

Date: 2026-05-31

Status: implemented locally

## Purpose

Goals2756 and 2758 made generic OptiX ray/triangle hit-stream output columns
more useful by adding caller-owned reusable CUDA buffers and measuring the
reduced output-allocation overhead on the RTX A5000 pod. That was real progress,
but it did not remove the next synchronization boundary: the current native
producer still synchronizes before returning host-visible `row_count` and
`overflow` metadata.

Goal2760 makes that boundary explicit in the public v2.5 handoff metadata and
adds a fail-closed async-promotion checklist. The point is to prevent future
reports, examples, or partner code from treating reusable CUDA output buffers as
proof of event/same-stream continuation or true zero-copy.

## Current Runtime Fact

The current OptiX hit-stream device-column implementation still follows this
shape:

1. launch the generic OptiX hit-stream producer on `CUstream stream = 0`;
2. call `cuStreamSynchronize(stream)`;
3. download the device `row_count`, `hit_event_count`, and `overflow` counters;
4. return CUDA column pointers plus host-visible scalar metadata to Python.

Python therefore records:

- `producer_consumer_stream_ordering="host_synchronized_before_consumer"`;
- `host_synchronization_used=True`;
- `zero_copy_compatible_stream_ordering=False`;
- `completion_event_handle_available=False`;
- `same_stream_handle_available=False`;
- `device_resident_row_count_for_partner=False`;
- `device_resident_overflow_for_partner=False`;
- `async_partner_continuation_authorized=False`;
- `true_zero_copy_authorized=False`.

This is safe and reproducible, but it is not an async producer-to-partner
continuation.

## Runtime Additions

`src/rtdsl/hit_stream_handoff.py` now exposes:

- `GENERIC_HIT_STREAM_ASYNC_PROMOTION_REQUIREMENTS_VERSION`;
- `describe_v2_5_hit_stream_async_promotion_requirements()`;
- explicit scalar-visibility and async-state fields in hit-stream handoff
  metadata and partner transfer plans.

The new requirements function records the concrete pieces needed before an async
promotion can be considered:

- `producer_stream_handle_or_same_stream_token`;
- `completion_event_handle_with_lifetime_owner`;
- `device_resident_row_count_ptr`;
- `device_resident_overflow_ptr`;
- `fail_closed_overflow_flag_visible_to_partner`;
- `explicit_release_for_event_and_temporary_counter_storage`.

The required Python carrier fields are similarly explicit:

- `producer_stream_identity`;
- `completion_event_identity`;
- `consumer_wait_contract`;
- `row_count_device_column_or_bounded_capacity_contract`;
- `overflow_device_flag_contract`;
- `event_owner_lifetime_state`.

## Required Hardware Evidence Before Promotion

The next implementation goal can choose event-based ordering or same-stream
ordering, but either route must prove the following on a pod:

- same-pointer hit-stream columns are preserved;
- no `cuStreamSynchronize` runs on the producer path before partner launch;
- a dependent consumer proves event wait or same-stream ordering;
- row count and overflow are consumed through device-resident state, or a
  bounded-capacity contract that does not need a host scalar read;
- timings separate producer launch, event wait, continuation, and materialization.

## Forbidden Shortcuts

Goal2760 explicitly rejects these promotions:

- treating `host_synchronized_before_consumer` as zero-copy-compatible;
- treating reusable output buffers as async proof;
- treating host-visible `row_count` after `cuStreamSynchronize` as a
  device-resident counter;
- authorizing public speedup from metadata alone.

This goal does not authorize true zero-copy, async partner continuation, or any
public speedup claim; in short, it makes no public speedup claim. It only makes
the next real implementation target precise.

## Files Changed

- `src/rtdsl/hit_stream_handoff.py`
- `src/rtdsl/__init__.py`
- `tests/goal2760_hit_stream_async_promotion_requirements_test.py`
- `docs/reports/goal2760_hit_stream_async_promotion_requirements_2026-05-31.md`
- `docs/research/future_version_to_do_list.md`

## Validation

Local focused gate:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m py_compile src/rtdsl/hit_stream_handoff.py src/rtdsl/__init__.py tests/goal2760_hit_stream_async_promotion_requirements_test.py
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2760_hit_stream_async_promotion_requirements_test tests.goal2758_reusable_hit_stream_buffer_perf_probe_test tests.goal2756_reusable_hit_stream_device_output_buffers_test tests.goal2752_hit_stream_zero_copy_ordering_metadata_test tests.goal2746_optix_hit_stream_host_sync_ordering_test
```

Result: `18` tests passed, `1` skipped on the local non-CUDA Windows runtime.

Broader v2.5 hit-stream metadata gate:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2684_generic_rt_hit_stream_handoff_test tests.goal2685_device_resident_hit_stream_handoff_test tests.goal2690_post_goal2689_contract_honesty_test tests.goal2694_hit_stream_neutral_seam_metadata_test tests.goal2698_hit_stream_partner_continuation_plan_test tests.goal2700_explicit_hit_stream_gather_partner_test tests.goal2704_native_hit_stream_output_abi_contract_test tests.goal2706_native_optix_hit_stream_device_columns_test tests.goal2708_hit_stream_cuda_array_torch_carrier_adapter_test tests.goal2719_native_hit_stream_materialization_proof_metadata_test tests.goal2734_v2_5_same_pointer_zero_copy_boundary_audit_test tests.goal2737_native_hit_stream_owner_lifecycle_guard_test tests.goal2738_native_hit_stream_stream_ordering_boundary_test tests.goal2740_hit_stream_cross_partner_transfer_plan_test tests.goal2744_native_hit_stream_release_enforcement_audit_test tests.goal2746_optix_hit_stream_host_sync_ordering_test tests.goal2750_hit_stream_transfer_stream_ordering_gate_test tests.goal2752_hit_stream_zero_copy_ordering_metadata_test tests.goal2754_current_v25_hit_stream_perf_probe_test tests.goal2756_reusable_hit_stream_device_output_buffers_test tests.goal2758_reusable_hit_stream_buffer_perf_probe_test tests.goal2760_hit_stream_async_promotion_requirements_test
```

Result: `102` tests passed, `2` skipped on the local non-CUDA Windows runtime.

## External Review

Claude review:

- `docs/reviews/goal2761_claude_review_goal2760_hit_stream_async_promotion_requirements_2026-05-31.md`
- verdict: `accept-with-boundary`
- named boundary: current v2.5 OptiX hit-stream output is CUDA-resident and
  caller-reusable, but still host-synchronized before partner continuation.
  Async promotion still requires native stream/event state, device-resident
  row-count and overflow state, partner wait proof, and pod evidence.

Gemini review attempt:

- `gemini-2.5-flash` failed with server-side `MODEL_CAPACITY_EXHAUSTED`;
- `gemini-2.0-flash` is not available in this CLI (`ModelNotFoundError`);
- no Gemini review is claimed for this goal.

## Boundary

The v2.5 hit-stream handoff is stronger after this goal because its current
synchronization state is harder to misread. It is still not the final
device-resident continuation design. The next code-bearing target remains a
generic event/same-stream producer API plus device-resident count/overflow
handling, followed by pod validation.

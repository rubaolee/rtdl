# Claude Review: Goal2760 Hit-Stream Async Promotion Requirements

Date: 2026-05-31
Reviewer: Claude Sonnet 4.6 (independent read-only review)
Verdict: **accept-with-boundary**

Note: A Gemini Flash review attempt failed with server-side capacity exhaustion.
This document is the external consensus artifact for Goal2760.

---

## Review Scope

Files inspected:

- `src/rtdsl/hit_stream_handoff.py`
- `src/rtdsl/__init__.py`
- `src/native/optix/rtdl_optix_workloads.cpp` (lines 10316–10453)
- `tests/goal2760_hit_stream_async_promotion_requirements_test.py`
- `docs/reports/goal2760_hit_stream_async_promotion_requirements_2026-05-31.md`
- `docs/research/future_version_to_do_list.md` (v2.5+ section)

---

## Question 1: Does Goal2760 correctly preserve the current runtime truth that OptiX hit-stream output is `host_synchronized_before_consumer`?

**Yes, and the chain is directly verifiable.**

The C++ implementation (`rtdl_optix_workloads.cpp`, lines 10400–10413):

```cpp
CUstream stream = 0;
OPTIX_CHECK(optixLaunch(..., stream, ...));
CU_CHECK(cuStreamSynchronize(stream));   // ← sync point
...
download(&attempted_rows, d_row_count.ptr, 1);
download(&overflow, d_overflow.ptr, 1);
```

The sync precedes both scalar downloads. `optix_runtime.py` reflects this by
hardcoding `producer_consumer_stream_ordering="host_synchronized_before_consumer"`
in both `ray_triangle_hit_stream_device_columns` and
`ray_triangle_hit_stream_into_device_columns`. The Python-level handoff
metadata then correctly derives:

- `host_synchronization_used=True`
- `zero_copy_compatible_stream_ordering=False`
- `event_or_same_stream_ordering_proven=False`
- `completion_event_handle_available=False`
- `same_stream_handle_available=False`
- `async_partner_continuation_authorized=False`
- `true_zero_copy_authorized=False`

The new `describe_v2_5_hit_stream_async_promotion_requirements()` function
(hit_stream_handoff.py:585–648) makes this the authoritative entry point for
the async-promotion state, with `current_runtime_ordering_state` set to
`"host_synchronized_before_consumer"` and every authorization flag explicitly
`False`. There are no inconsistencies between the C++ state, the runtime Python
metadata, and the new requirements descriptor.

---

## Question 2: Do the new metadata fields and `describe_v2_5_hit_stream_async_promotion_requirements()` clearly prevent reusable output buffers from being mistaken for event/same-stream or true zero-copy proof?

**Yes. The separation is explicit and structurally enforced.**

The handoff metadata records `caller_owned_output_buffers` and
`reusable_output_buffers_used` as separate boolean fields that say nothing
about stream ordering. The stream ordering fields (`zero_copy_compatible_stream_ordering`,
`event_or_same_stream_ordering_proven`) derive solely from
`producer_consumer_stream_ordering`, which remains `"host_synchronized_before_consumer"`.
The two sets of fields cannot be confused by reading the metadata.

The new requirements function adds an explicit `forbidden_promotion_shortcuts`
tuple (lines 637–642):

- `"treating host_synchronized_before_consumer as zero-copy-compatible"`
- `"using reusable output buffers as async proof"`
- `"using host-visible row_count after cuStreamSynchronize as a device-resident counter"`
- `"authorizing public speedup from metadata alone"`

The `claim_boundary` string in both `RtdlNativeDeviceHitStreamOutput.to_metadata()`
and `describe_v2_5_hit_stream_async_promotion_requirements()` reinforce the
same constraint. Any code or report consuming this metadata must actively
override multiple explicit `False` fields to reach a zero-copy or async claim.
That is the correct fail-closed design.

---

## Question 3: Are the required future ABI pieces clear enough?

**Yes. All five pieces named in the review brief are present, with additional
detail.**

The `required_native_abi_extensions` tuple (lines 609–615) names:

| Required piece (review brief)          | Field in requirements dict |
|----------------------------------------|----------------------------|
| producer stream or same-stream token   | `producer_stream_handle_or_same_stream_token` |
| completion event handle with lifetime owner | `completion_event_handle_with_lifetime_owner` |
| device-resident row-count pointer      | `device_resident_row_count_ptr` |
| device-resident overflow pointer       | `device_resident_overflow_ptr` |
| partner consumer wait proof            | listed in `required_partner_consumer_proofs` |

The sixth field (`explicit_release_for_event_and_temporary_counter_storage`)
addresses the lifetime-owner question for the new event and counter storage.

`required_python_carrier_fields` (lines 617–623) names the Python-side
counterparts: `producer_stream_identity`, `completion_event_identity`,
`consumer_wait_contract`, `row_count_device_column_or_bounded_capacity_contract`,
`overflow_device_flag_contract`, `event_owner_lifetime_state`.

`required_pod_validation` (lines 631–636) specifies what hardware evidence
must be produced before promotion is considered — including the explicit
requirement that no `cuStreamSynchronize` runs on the producer path before
partner launch.

The coverage is complete against the five-piece checklist from the brief.

---

## Question 4: Does the test gate verify both the native sync point and the Python metadata boundary without overclaiming?

**Yes. The test is well-structured and notably honest.**

Four test methods:

**`test_async_promotion_requirements_are_exported_and_fail_closed`**
Calls `rt.describe_v2_5_hit_stream_async_promotion_requirements()` and
asserts `current_runtime_ordering_state="host_synchronized_before_consumer"`,
all authorization flags `False`, and that the required ABI extension names
and pod-validation strings are present in their respective tuples. Does not
assert any promotion is authorized.

**`test_current_handoff_and_transfer_metadata_expose_sync_blocker`**
Builds a fake CUDA handoff with `producer_consumer_stream_ordering=
"host_synchronized_before_consumer"` and `reusable_output_buffers_used=True`,
then checks that the handoff metadata and the `plan_v2_5_hit_stream_partner_transfer`
plan both carry the blocker state. All async/zero-copy fields are asserted
`False`. The test confirms that setting `reusable_output_buffers_used=True`
does not lift any authorization flag.

**`test_native_and_python_paths_remain_host_synchronized_before_return`**
This is the strongest test. It reads the C++ source file directly, slices
the `_impl_optix` function body, and asserts:

- `"CUstream stream = 0;"` is present
- `"cuStreamSynchronize(stream)"` is present
- The sync index is less than the index of `"download(&attempted_rows"` and
  `"download(&overflow"` — verifying ordering, not just presence

It then reads `optix_runtime.py` and checks that exactly two occurrences of
`producer_consumer_stream_ordering="host_synchronized_before_consumer"` appear
in the two hit-stream methods, and that neither `"same_stream"` nor
`"producer_event_waited_by_consumer"` appears.

**`test_report_records_current_blocker_and_next_abi_requirements`**
Reads the report file and checks for required strings. The assertions include
`"This goal does not authorize true zero-copy"` and `"no public speedup claim"`,
locking the report text against future weakening.

No test asserts any async or zero-copy claim. The native-code slice test is
the most important contribution of this test suite: it is a live file probe
that would fail if the C++ sync is ever removed without updating the Python
metadata.

**One minor fragility**: the C++ slice is bounded by searching for the non-impl
function name after the impl function's start position. This relies on file
ordering (impl before non-impl). The ordering holds in the current source, and
the approach is readable, but it is worth noting for any future C++ refactor
that changes function order.

---

## Question 5: Are there any app-specific or domain-specific terms in the new primitive contract?

**No app-specific vocabulary introduced.**

All new field names, tuple values, and function names are generic:
`hit_stream`, `ray_ids`, `primitive_ids`, `async_promotion`, `stream_ordering`,
`event_handle`, `device_resident_row_count`, `device_resident_overflow`,
`fail_closed_overflow_flag`, `producer_stream_identity`,
`consumer_wait_contract`. None of these encode a specific application,
dataset, or spatial-join operation.

The existing `native_engine_app_specific_vocab_allowed=False` constraint in
`describe_generic_device_resident_hit_stream_handoff_3d()` (line 535) and the
`app_specific_semantics_allowed=False` in `RtdlTypedPrimitivePayloadColumns.to_metadata()`
(line 494) are both preserved. The new requirements descriptor is consistent
with the app-agnostic native/runtime direction.

---

## Summary

Goal2760 does exactly what it claims: it hardens the v2.5 hit-stream boundary
by making the current synchronization state and the missing async pieces
explicit in runtime metadata, tests, and report. It does not introduce a new
async implementation, does not authorize true zero-copy, and does not make a
public speedup claim. All five required future ABI pieces are named precisely.
The test gate verifies both the native sync point in C++ source and the Python
metadata boundary, without overclaiming.

**Verdict: accept-with-boundary**

**Named boundary:**
Current v2.5 OptiX hit-stream output is CUDA-resident and caller-reusable
(Goal2756). It is still host-synchronized before partner continuation
(`cuStreamSynchronize` before row-count and overflow download). Async
promotion requires: a producer stream or same-stream token in the native ABI,
a completion event handle with a lifetime owner, device-resident row-count
and overflow state accessible to the partner without a host scalar read, and
pod evidence that a dependent consumer proves event-wait or same-stream
ordering without any device-wide synchronization on the producer path. None
of those conditions are met by this goal. True zero-copy, async partner
continuation, and public speedup claims remain unauthorized.

# Gemini Review Handoff: Goal2760 Hit-Stream Async Promotion Requirements

Please perform an independent read-only review of Goal2760 and write your review
to:

`docs/reviews/goal2761_gemini_review_goal2760_hit_stream_async_promotion_requirements_2026-05-31.md`

## Context

Recent v2.5 goals added generic OptiX ray/triangle hit-stream device columns
and reusable caller-owned CUDA output buffers:

- Goal2756: reusable hit-stream device output buffers.
- Goal2758: measured the narrow output-allocation benefit on the RTX A5000 pod.

Goal2760 does **not** claim a new async implementation. It hardens the boundary
before the next implementation step by making the current host-synchronized
state and missing async pieces explicit in runtime metadata, tests, and report.

## Files To Inspect

- `src/rtdsl/hit_stream_handoff.py`
- `src/rtdsl/__init__.py`
- `src/rtdsl/optix_runtime.py`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `tests/goal2760_hit_stream_async_promotion_requirements_test.py`
- `docs/reports/goal2760_hit_stream_async_promotion_requirements_2026-05-31.md`
- `docs/research/future_version_to_do_list.md`

## Review Questions

1. Does Goal2760 correctly preserve the current runtime truth that OptiX
   hit-stream output is `host_synchronized_before_consumer`?
2. Do the new metadata fields and
   `describe_v2_5_hit_stream_async_promotion_requirements()` clearly prevent
   reusable output buffers from being mistaken for event/same-stream or true
   zero-copy proof?
3. Are the required future ABI pieces clear enough: producer stream or same-stream
   token, completion event handle with lifetime owner, device-resident row-count
   pointer, device-resident overflow pointer, and partner consumer wait proof?
4. Does the test gate verify both the native sync point and the Python metadata
   boundary without overclaiming?
5. Are there any app-specific or domain-specific terms in the new primitive
   contract that would violate the app-agnostic native/runtime direction?

## Expected Verdict

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

If accepted with boundary, name the exact boundary. Do not authorize true
zero-copy, public speedup, release readiness, or async continuation unless the
code and hardware evidence truly prove it.

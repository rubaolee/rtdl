# Claude Review Handoff: Goal2762 Hit-Stream Device Status Buffers

Please perform an independent read-only review of Goal2762 and write your review
to:

`docs/reviews/goal2763_claude_review_goal2762_hit_stream_device_status_buffers_2026-05-31.md`

## Context

Goal2760 made the async-promotion blocker explicit: reusable CUDA output buffers
are not enough for async partner continuation because the current OptiX producer
still synchronizes before returning host-visible `row_count` and `overflow`.

Goal2762 adds the next generic building block: caller-owned device status
buffers for row count, hit-event count, and overflow, written by the native
OptiX hit-stream producer alongside caller-owned `ray_ids` and `primitive_ids`.
It intentionally keeps `producer_consumer_stream_ordering="host_synchronized_before_consumer"`.

## Files To Inspect

- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/hit_stream_handoff.py`
- `tests/goal2762_hit_stream_device_status_buffers_test.py`
- `tests/goal2760_hit_stream_async_promotion_requirements_test.py`
- `docs/reports/goal2762_hit_stream_device_status_buffers_2026-05-31.md`
- `docs/research/future_version_to_do_list.md`

## Validation Already Run

Local Windows:

- `py_compile` passed for `src/rtdsl/optix_runtime.py`, `src/rtdsl/hit_stream_handoff.py`, and the Goal2762 test.
- Focused gate: `17` tests passed, `2` skipped.
- Broader v2.5 hit-stream gate: `107` tests passed, `3` skipped.

Pod `root@69.30.85.171:22167`, patched from pushed commit `ccc07b5f`:

- `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk` passed.
- Runtime gate with `RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so` passed: `17` tests.
- The Goal2762 runtime smoke checked status tensor values:
  `row_count=1`, `hit_event_count=1`, `overflow=0`.

## Review Questions

1. Is the native ABI generic and app-agnostic?
2. Does the implementation correctly pass caller-owned status pointers into the
   OptiX launch params and return pointer identity in `RtdlNativeDeviceHitStreamColumns`?
3. Does Python correctly expose the status buffers and propagate status pointer
   metadata through `RtdlHitStreamColumnHandoff` and partner transfer planning?
4. Does the goal preserve the boundary that this is still
   `host_synchronized_before_consumer`, not async partner continuation and not
   true zero-copy?
5. Are tests and report sufficient for this building block?

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, `reject`.
Name any boundary precisely.

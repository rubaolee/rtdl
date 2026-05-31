# Gemini Review Request: Goal2756 Reusable Hit-Stream Device Output Buffers

Please perform a read-only independent review of Goal2756 and write your review
to:

`docs/reviews/goal2757_gemini_review_goal2756_reusable_hit_stream_buffers_2026-05-31.md`

## Context

Goal2756 adds a generic OptiX path where caller-owned CUDA `int64` tensors are
used as reusable output buffers for the ray/triangle hit-stream columns
`ray_ids` and `primitive_ids`.

This should reduce one overhead source identified after Goal2754: per-run native
output-column allocation and release. It must not be treated as true zero-copy,
because producer/consumer ordering is still host-synchronized before partner
consumption.

## Files To Review

- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/hit_stream_handoff.py`
- `src/rtdsl/__init__.py`
- `tests/goal2756_reusable_hit_stream_device_output_buffers_test.py`
- `tests/goal2746_optix_hit_stream_host_sync_ordering_test.py`
- `docs/reports/goal2756_reusable_hit_stream_device_output_buffers_2026-05-31.md`
- `docs/reports/goal2756_pod_artifacts/goal2756_reusable_hit_stream_device_output_buffers_69_30_85_171_2026-05-31.json`
- `docs/research/future_version_to_do_list.md`

## Questions

1. Does the native implementation preserve the old native-owned path while
   adding a safe caller-owned path?
2. Does the Python runtime preserve app-agnostic naming and expose a usable
   reusable-buffer contract?
3. Is the metadata honest about caller-owned lifetime, host synchronization, and
   no true-zero-copy authorization?
4. Does the pod artifact support the narrow hardware claim made in the report?
5. Are there bugs, missing tests, stale claims, app-shaped leakage, or release
   overclaims?

## Required Verdict

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Please keep the review concrete and file-grounded.

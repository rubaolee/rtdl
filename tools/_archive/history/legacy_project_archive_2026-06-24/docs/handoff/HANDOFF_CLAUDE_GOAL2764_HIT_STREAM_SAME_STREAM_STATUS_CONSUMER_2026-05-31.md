# Handoff: Goal2764 Hit-Stream Same-Stream Status Consumer Review

Please perform an independent read-only review of Goal2764 and write your
review to:

`docs/reviews/goal2765_claude_review_goal2764_hit_stream_same_stream_status_consumer_2026-05-31.md`

## Context

Goal2764 implements the next v2.5 hit-stream promotion step: an OptiX producer
launches into caller-owned CUDA hit-stream columns and caller-owned CUDA status
buffers on a caller-provided stream, then a bounded CuPy RawKernel consumer reads
the device status on that same stream before any host scalar row-count read.

The intended verdict, if correct, is not a broad zero-copy release claim. It is a
narrow runtime-contract proof:

- same-stream producer/consumer ordering is proven for the bounded status
  consumer;
- producer-side host scalar synchronization is avoided before the consumer;
- device status is consumed by the partner kernel;
- general async partner continuation, event-based cross-stream continuation,
  arbitrary row consumers, true zero-copy wording, and public speedup claims
  remain unauthorized.

## Files To Inspect

- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/hit_stream_handoff.py`
- `tests/goal2764_hit_stream_same_stream_status_consumer_test.py`
- `tests/goal2760_hit_stream_async_promotion_requirements_test.py`
- `docs/reports/goal2764_hit_stream_same_stream_status_consumer_2026-05-31.md`
- `docs/research/future_version_to_do_list.md`

## Review Questions

1. Does the new native on-stream symbol avoid `cuStreamSynchronize` and host
   `download(...)` on the producer path before the partner consumer?
2. Does the native async owner correctly preserve temporary ray, flag, and launch
   parameter storage until the consumer is done?
3. Does the Python CuPy consumer really read device-resident `row_count`,
   `hit_event_count`, and `overflow` on the same stream?
4. Does the metadata avoid overclaiming true zero-copy, public speedup, broad
   partner continuation, or release readiness?
5. Are the tests and report sufficient to treat this as accepted internal v2.5
   evidence, assuming the recorded pod validation is accurate?

## Evidence Already Collected

Local Windows:

`$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2764_hit_stream_same_stream_status_consumer_test tests.goal2760_hit_stream_async_promotion_requirements_test tests.goal2762_hit_stream_device_status_buffers_test`

Result: 14 passed, 2 skipped for local CUDA/OptiX runtime availability.

Pod:

`ssh root@69.30.85.171 -p 22167 -i C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`

Build:

`make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`

Result: success.

Live Goal2764:

`PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so python3 -m unittest -v tests.goal2764_hit_stream_same_stream_status_consumer_test`

Result: 5 passed, 0 skipped.

Corrected hit-stream gate:

57 tests passed across Goal2704/2706/2710/2719/2720/2737/2738/2746/2750/2752/2756/2758/2760/2762/2764.

## Required Review Format

Use one of the project verdict values:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Please lead with the verdict, then list findings and any required follow-up.
State explicitly that this is an independent Claude review and that Codex+Codex
does not count as external consensus.

# Goal2750 Hit-Stream Transfer Stream-Ordering Gate

Date: 2026-05-30

Status: implemented and pod-validated

## Purpose

Goals2738 and 2746 made stream-ordering metadata visible for native OptiX
hit-stream device columns. Goal2740 then planned cross-partner transfer. One
remaining risk was subtle: a device-resident hit stream with
`producer_consumer_stream_ordering="not_proven"` could still receive a transfer
plan that looked executable for Triton/CuPy/Numba device consumers.

Goal2750 hardens that planner. Device partners now fail closed unless the
hit-stream handoff records proven producer/consumer ordering.

## Change

`plan_v2_5_hit_stream_partner_transfer(...)` now emits:

- `producer_consumer_stream_ordering`;
- `device_consumer_requires_stream_ordering`;
- `stream_ordering_blocks_device_consumer`;
- status `stream_ordering_proof_required` when device columns are otherwise
  ready but the stream-ordering proof is missing.

For device partners:

| Input ordering | Planner status | Execution without copy | Boundary |
| --- | --- | ---: | --- |
| `not_proven` | `stream_ordering_proof_required` | false | fail closed before a device consumer can read stale or racing columns |
| `producer_event_waited_by_consumer` | `torch_carrier_preview` / descriptor preview | true | ordering proof exists, but no true zero-copy or speedup claim |
| `host_synchronized_before_consumer` | `torch_carrier_preview` / descriptor preview | true | safe host-synchronized handoff, but not a no-sync zero-copy path |

This does not implement event-based native output. It prevents the transfer
planner from over-approving unsynchronized device reads.

## Validation

Local Windows:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal2750_hit_stream_transfer_stream_ordering_gate_test \
  tests.goal2740_hit_stream_cross_partner_transfer_plan_test \
  tests.goal2738_native_hit_stream_stream_ordering_boundary_test \
  tests.goal2746_optix_hit_stream_host_sync_ordering_test \
  tests.goal2748_triton_group_id_device_error_flag_test

Ran 24 tests in 0.035s
OK (skipped=2)
```

Pod:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so \
timeout 240 python3 -m unittest \
  tests.goal2750_hit_stream_transfer_stream_ordering_gate_test \
  tests.goal2740_hit_stream_cross_partner_transfer_plan_test \
  tests.goal2738_native_hit_stream_stream_ordering_boundary_test \
  tests.goal2746_optix_hit_stream_host_sync_ordering_test \
  tests.goal2748_triton_group_id_device_error_flag_test

Ran 24 tests in 0.610s
OK
```

## Boundary

Goal2750 is a planner safety gate, not a performance promotion. It does not
change the native OptiX ABI and does not claim true zero-copy. The actual future
promotion target remains a native event/stream contract where the OptiX producer
records an event and the Triton/partner consumer waits on that event without a
device-wide synchronization.

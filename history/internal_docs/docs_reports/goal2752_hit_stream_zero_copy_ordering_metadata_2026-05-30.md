# Goal2752 Hit-Stream Zero-Copy Ordering Metadata

Date: 2026-05-30

Status: implemented

## Purpose

Goal2750 made the hit-stream transfer planner fail closed when stream ordering
is not proven. Goal2752 tightens the next claim boundary: a handoff can be safe
to consume because the host synchronized before returning, but that is not the
same as event/same-stream ordering for future no-sync zero-copy promotion.

## Change

Hit-stream handoff metadata, native-output metadata, and transfer plans now
separate:

- `stream_synchronization_proven`: the consumer can safely read the producer
  columns;
- `host_synchronization_used`: the proof came from a host/device sync before
  the consumer;
- `event_or_same_stream_ordering_proven`: the proof is an event/same-stream
  ordering shape that could support a future no-host-sync path;
- `zero_copy_compatible_stream_ordering`: the ordering shape is compatible with
  future true-zero-copy review, though true-zero-copy remains unauthorized.

## Classification

| Ordering state | Safe to consume | Host sync used | Future zero-copy-compatible ordering | Current zero-copy authorized |
| --- | ---: | ---: | ---: | ---: |
| `not_proven` | false | false | false | false |
| `host_synchronized_before_consumer` | true | true | false | false |
| `same_stream` | true | false | true | false |
| `producer_event_waited_by_consumer` | true | false | true | false |

This keeps the current OptiX native device-column path honest: Goal2746 proved
host-synchronized correctness, not event-ordered zero-copy.

## Validation

Local Windows:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal2752_hit_stream_zero_copy_ordering_metadata_test \
  tests.goal2750_hit_stream_transfer_stream_ordering_gate_test \
  tests.goal2740_hit_stream_cross_partner_transfer_plan_test \
  tests.goal2738_native_hit_stream_stream_ordering_boundary_test \
  tests.goal2746_optix_hit_stream_host_sync_ordering_test

Ran 23 tests in 0.037s
OK
```

Pod:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so \
timeout 240 python3 -m unittest \
  tests.goal2752_hit_stream_zero_copy_ordering_metadata_test \
  tests.goal2750_hit_stream_transfer_stream_ordering_gate_test \
  tests.goal2740_hit_stream_cross_partner_transfer_plan_test \
  tests.goal2738_native_hit_stream_stream_ordering_boundary_test \
  tests.goal2746_optix_hit_stream_host_sync_ordering_test

Ran 23 tests in 0.014s
OK
```

## Boundary

Goal2752 is metadata and planner claim hardening. It does not add native OptiX
event handles, does not remove `cuStreamSynchronize`, and does not authorize
true zero-copy. It narrows the future work to a real event/same-stream producer
and consumer contract.

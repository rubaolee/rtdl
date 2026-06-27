# Goal2831 Primitive Payload Column Descriptors

Date: 2026-05-31

## Purpose

Goal2829 proved a narrow same-stream continuation: a fixed-radius CUDA graph can expose device-resident partial aggregate rows, and a bounded CuPy rawkernel can reduce them on the same native CUDA stream before host partial-row materialization.

Goal2831 turns that proof into a reusable v2.5 contract layer: typed primitive-payload column descriptors. The descriptor records the information a partner planner needs without becoming a memory manager or an app-specific API.

## New Contract Surface

Added in `src/rtdsl/hit_stream_handoff.py`:

- `GENERIC_PRIMITIVE_PAYLOAD_COLUMN_DESCRIPTOR_VERSION`
- `GENERIC_PRIMITIVE_PAYLOAD_COLUMN_ROLES`
- `GENERIC_PRIMITIVE_PAYLOAD_FALLBACK_REASONS`
- `RtdlPrimitivePayloadColumnDescriptor`
- `describe_primitive_payload_column_descriptor(...)`
- `describe_fixed_radius_graph_partial_payload_descriptor(...)`

The descriptor wraps an `RtdlBufferDescriptor` and adds:

- semantic role;
- producer and consumer boundary names;
- stream ordering state;
- lifetime state;
- fallback reason;
- host-materialization status;
- native-producer flag;
- neutral-buffer seam metadata.

## Goal2829 Integration

`PreparedOptixFixedRadiusRankedSummaryAggregateBatchGraph3D.replay_same_stream_device_partials_summary_cupy()` now includes a `primitive_payload_column_descriptors` metadata tuple. The descriptor for the graph partial buffer records:

- name: `fixed_radius_ranked_summary_aggregate_partials`
- dtype: `struct:RtdlFixedRadiusRankedNeighborAggregate`
- semantic role: `partial_aggregate_rows`
- producer: `optix_cuda_graph`
- consumer: `partner_partial_reduction`
- device: `cuda:0`
- source protocol: `native_cuda_device_pointer`
- stream ordering: `same_stream`
- lifetime state: `producer_retained`
- transfer status: `borrowed_device_pointer_unmeasured`

## Claim Boundary

`accept-with-boundary`

This goal is a contract-layer hardening step. It makes typed payload buffers, fallback reasons, stream ordering, and neutral-buffer lifetime state visible to tests and user-facing metadata.

It does not authorize:

- arbitrary partner execution;
- broad true-zero-copy claims;
- public speedup claims;
- paper reproduction claims;
- whole-app acceleration claims;
- v2.5 release claims.

True zero-copy still requires measured same-pointer/no-host-stage evidence plus proven same-stream or event-ordered stream ordering.

## Validation

Local focused suite:

```text
python -m unittest \
  tests.goal2831_primitive_payload_column_descriptor_test \
  tests.goal2829_fixed_radius_graph_same_stream_device_partials_test \
  tests.goal2789_neutral_buffer_torch_carrier_reconciliation_test \
  tests.goal2685_device_resident_hit_stream_handoff_test
```

Result:

```text
Ran 29 tests in 0.480s
OK (skipped=1)
```

## Next Step

Use this descriptor to drive the next runtime step: a partner-neutral continuation planner that can choose CuPy/Triton/Numba from descriptor capabilities, fail closed with explicit fallback reasons, and preserve event/same-stream ordering metadata through the whole primitive-to-partner path.

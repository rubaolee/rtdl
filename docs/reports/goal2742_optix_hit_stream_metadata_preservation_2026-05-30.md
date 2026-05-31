# Goal2742 - OptiX Hit-Stream Metadata Preservation

Date: 2026-05-30

Status: local Codex implementation complete; external review covered by the
Goal2740/2741 transfer-boundary review lane unless a separate reviewer requests
deeper native inspection.

## Purpose

The v2.5 hit-stream handoff dataclass gained new lifetime and stream-ordering
metadata in Goal2737 and Goal2738. The OptiX runtime creates a native handoff,
then rebuilds the dataclass after adding `query_pack` and `native_call` phase
timings. That rebuild must preserve every boundary-critical field as the
handoff grows.

Goal2742 fixes the first observed preservation gap: the rebuild now carries
`producer_consumer_stream_ordering` through from the original native handoff.

## Change

`src/rtdsl/optix_runtime.py` now passes:

```python
producer_consumer_stream_ordering=handoff.producer_consumer_stream_ordering
```

when reconstructing the `RtdlHitStreamColumnHandoff` with extra timing fields.

The current native OptiX path still records `not_proven` unless a future native
event/synchronization path supplies stronger evidence. This change is therefore
metadata preservation, not a new synchronization proof.

## Tests

`tests/goal2738_native_hit_stream_stream_ordering_boundary_test.py` now includes
a static regression that checks the OptiX runtime preserves the stream-ordering
field during the rebuild.

Validation:

```text
py -3 -m unittest \
  tests.goal2738_native_hit_stream_stream_ordering_boundary_test \
  tests.goal2740_hit_stream_cross_partner_transfer_plan_test \
  tests.goal2704_native_hit_stream_output_abi_contract_test \
  tests.goal2708_hit_stream_cuda_array_torch_carrier_adapter_test
21 tests OK

py -3 -m py_compile src/rtdsl/optix_runtime.py \
  tests/goal2738_native_hit_stream_stream_ordering_boundary_test.py
clean
```

Pod validation on `root@69.30.85.171:22167` after pulling commit `af74e334`:

```text
python3 -m unittest \
  tests.goal2738_native_hit_stream_stream_ordering_boundary_test \
  tests.goal2740_hit_stream_cross_partner_transfer_plan_test \
  tests.goal2704_native_hit_stream_output_abi_contract_test \
  tests.goal2708_hit_stream_cuda_array_torch_carrier_adapter_test
21 tests OK
```

## Boundary

- No native ABI changed.
- No true-zero-copy claim is authorized.
- No stream synchronization claim is authorized.
- This only prevents a future proven stream-ordering state from being dropped by
  Python-side metadata reconstruction.

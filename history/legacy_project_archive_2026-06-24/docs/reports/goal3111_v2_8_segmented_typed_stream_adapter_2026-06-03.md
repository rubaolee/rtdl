# Goal3111: v2.8 Segmented Typed-Stream Adapter

Date: 2026-06-03

Status: internal reference adapter, no native promotion

Materialization token: `host_reference_contract_adapter`

## Purpose

Goal3108 defined the v2.8 typed result-stream contract. Goal3111 adds the first
executable bridge on top of it: a local reference adapter that turns an existing
segmented row stream into a typed result stream and, when requested, a grouped
continuation plan.

This is useful because v2.8 needs to connect existing pieces before promoting
native producers or partner consumers:

- segmented row pages already define deterministic paging and
  `fail_closed_overflow`,
- typed result streams define columns, status columns, ordering, and claim
  boundaries,
- grouped continuation plans define explicit user-selected partner continuation.

Goal3111 connects those pieces in one testable path.

## What Was Added

New module:

- `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`

New exported surface:

- `V28SegmentedTypedStreamAdapterResult`
- `build_segmented_typed_stream_adapter`
- `execute_segmented_typed_stream_reference_continuation`
- `plan_segmented_typed_stream_partner_continuation`
- `execute_segmented_typed_stream_partner_continuation`
- `validate_segmented_typed_stream_adapter`
- `v2_8_segmented_typed_stream_adapter_summary`
- adapter version/status/materialization constants

The adapter:

1. emits a `SegmentedRowStream` from generic rows,
2. maps each row-schema field into a typed result-stream column role,
3. builds required status columns,
4. creates a `V28TypedResultStreamContract`,
5. optionally creates a `V28GroupedContinuationPlan`,
6. records concrete status values such as row count, page capacity, overflow,
   and complete-candidate-coverage.

The module also adds a reference grouped-continuation consumer:

- `execute_segmented_typed_stream_reference_continuation`

That function reconstructs the segmented rows, maps the typed continuation plan
onto the existing v2.5 `execute_v2_5_partner_continuation_reference` oracle, and
returns reference outputs while preserving the same non-authorizing flags. This
gives native producers and partner consumers a concrete local oracle before any
runtime promotion.

Goal3117 extends the same module with an explicit partner-consumer front door.
It supports a dry-run request locally and a fail-closed execution path that
requires caller-supplied partner columns. It never secretly materializes host
rows into partner tensors.

## Boundary

This is a reference adapter only.

It is:

- not a native producer
- not a partner consumer promotion
- not a device-residency proof
- not a true-zero-copy claim
- not a release authorization
- not a public speedup claim
- not broad RT-core wording
- not hidden dispatch
- not hidden partner selection
- not app-specific native-engine behavior
- not user-defined shader injection

The adapter may record CUDA-shaped `RtdlBufferDescriptor` pointers when provided
by a caller, but that is pointer metadata only. The adapter still sets
`device_resident_result_stream_proven = False` and
`true_zero_copy_claim_authorized = False`.

## Why This Helps v2.8

This gives the next native or partner implementation a concrete target:

- produce the same typed stream metadata,
- preserve the same required status columns,
- preserve the same fail-closed overflow behavior,
- preserve explicit user partner choice,
- pass the same contract validation.

The next real performance step can now compare a native producer or partner
consumer against this reference contract and reference grouped-continuation
consumer without changing the claim boundary.

## Validation

Local validation commands:

```powershell
py -3 -m py_compile src\rtdsl\v2_8_segmented_typed_stream_adapter.py src\rtdsl\v2_8_typed_result_stream.py src\rtdsl\__init__.py
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3111_v2_8_segmented_typed_stream_adapter_test tests.goal3108_v2_8_typed_result_stream_contract_test tests.goal3105_v2_8_benchmark_runtime_gap_map_test
```

Observed local result after the Goal3114 reference-consumer extension:
`py_compile` passed, and the focused unittest command ran 22 tests successfully.

The test checks:

- the adapter summary is internal and non-authorizing,
- segmented rows become a typed result stream plus grouped continuation plan,
- CUDA pointer-shaped metadata does not authorize zero-copy,
- missing roles fail closed,
- `auto` partner selection fails closed,
- segmented overflow preserves `SegmentedRowStreamOverflowError`,
- reference grouped-continuation consumer outputs for grouped argmax,
  segmented sum, and top-k required-`k` behavior,
- this report records the reference-adapter and reference-consumer boundary.

## Next Step

The next v2.8 step should replace the host-reference producer in one narrow
benchmark subpath with a real typed-stream producer or consumer. The best
candidate remains a ranked-summary or bounded-witness path because it serves
multiple benchmark apps while keeping the engine vocabulary generic.

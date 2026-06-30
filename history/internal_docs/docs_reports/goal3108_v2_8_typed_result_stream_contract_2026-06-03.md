# Goal3108: v2.8 Typed Result-Stream Contract

Date: 2026-06-03

Status: internal v2.8 runtime-engineering slice, no release authorization

## Purpose

Goal3105 closed v2.7 as an internal discovery/orchestration version and opened
v2.8 around the first runtime target:

`typed_device_resident_result_streams_and_grouped_continuation`

Goal3108 implements the first contract-level slice of that target. The problem
is that RTDL already had several useful pieces, but they lived as separate
islands:

- `segmented_row_stream.py` describes bounded row pages and the
  `fail_closed_overflow` policy.
- `hit_stream_handoff.py` and v2.5 handoff work describe device-column exchange
  for a few specific continuation paths.
- `grouped_reduction_contracts.py` and `partner_continuation_protocol.py`
  describe grouped reductions and continuation operations.
- `neutral_buffer_seam.py` describes stream/lifetime ownership boundaries.

The new `src/rtdsl/v2_8_typed_result_stream.py` module gives these pieces a
shared typed stream vocabulary before any native kernel is promoted. In plain
terms, this is the typed device-resident result streams foundation that future
v2.8 producers and continuations should share.

## What Was Added

The new module defines:

- `V28TypedResultColumn`, wrapping the existing `RtdlBufferDescriptor` so v2.8
  streams reuse the established typed-buffer protocol instead of inventing a
  second memory model.
- `V28TypedResultStreamContract`, with generic stream kinds such as
  `hit_stream`, `candidate_stream`, `ranked_summary_stream`,
  `bounded_witness_stream`, and `grouped_reduction_stream`.
- Required status columns: `row_count`, `capacity`, `overflow`, and
  `complete_candidate_coverage`.
- Ordering states: `event_ordered`, `group_ordered`, `stable_row_order`, and
  `unordered_with_explicit_sort_key`.
- `V28GroupedContinuationPlan`, which maps a typed stream onto the existing
  v2.5 continuation operations such as `grouped_argmin_f64`,
  `grouped_argmax_f64`, `grouped_topk_f64`,
  `grouped_vector_sum_f64x2`, and `bounded_collect_finalize_i64`.
- Validator helpers for both the stream contract and grouped continuation plan.
- Public exports through `rtdsl.__init__`.

This is deliberately app-agnostic. The vocabulary is about typed streams,
groups, items, scores, payloads, masks, witnesses, and status columns. It does
not introduce benchmark-app terms into the native engine or the public contract.

## Contract Boundaries

This is a contract-level slice, not a native kernel promotion.

It is also:

- not a release authorization
- not a public speedup claim
- not a broad RT-core claim
- not a true-zero-copy claim
- not hidden dispatch
- not hidden partner selection
- not app-specific native engine behavior
- not user-defined shader injection

Users must still choose partners explicitly. The grouped continuation plan
rejects `auto` partner selection and keeps the claim flags false.

## Why This Is The Right First v2.8 Step

The benchmark-app gap map from Goal3105 shows the same runtime need across many
apps: RTDL needs generic device-resident result streams that can feed grouped
continuations without repeatedly materializing host-side tables. Goal3108 does
not solve that performance problem by itself. It makes the next steps testable:

1. native producers can target one stream schema,
2. partner continuations can consume the same schema,
3. status and overflow behavior are explicit,
4. ordering requirements are visible,
5. claim boundaries are machine-checkable.

This keeps the engine primitive-first and app-agnostic while giving v2.8 a
clear runtime substrate to extend.

## Validation

Local validation commands:

```powershell
py -3 -m py_compile src\rtdsl\v2_8_typed_result_stream.py src\rtdsl\__init__.py
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3108_v2_8_typed_result_stream_contract_test tests.goal3105_v2_8_benchmark_runtime_gap_map_test
```

Observed local result: `py_compile` passed, and the focused unittest command
ran 13 tests successfully.

The new unit test checks:

- the summary uses the Goal3105 v2.8 runtime target,
- the stream contract uses typed device columns and required status columns,
- `fail_closed_overflow` is preserved from segmented row streams,
- grouped continuation plans require an explicit user-selected partner,
- missing status columns fail closed,
- unordered streams require a row-offset column,
- wrong group-column roles fail closed,
- public exports expose the contract surface,
- this report records the narrow claim boundary.

## Next Step

The next v2.8 engineering target should be an actual typed-stream producer or
consumer that uses this contract in one benchmark path, still without changing
the public claim boundary. A good first candidate is a bounded witness or ranked
summary stream because those are shared by Hausdorff/X-HD, RTNN, spatial
RayJoin, contact-manifold, and RT-DBSCAN-style workloads.

# Goal3110: v2.8 Typed Result-Stream Contract 2-AI Consensus

Date: 2026-06-03

Status: accepted as an internal v2.8 contract slice, no release authorization

## Scope

Goal3108 adds the first v2.8 contract-level implementation for:

`typed_device_resident_result_streams_and_grouped_continuation`

The accepted scope is narrow. This goal defines typed result-stream columns,
status columns, ordering states, grouped continuation planning, and validation
helpers. It does not promote a native producer, does not promote a partner
consumer, and does not provide pod or performance evidence.

## Review Inputs

Codex implementation and validation:

- `src/rtdsl/v2_8_typed_result_stream.py`
- `src/rtdsl/__init__.py`
- `tests/goal3108_v2_8_typed_result_stream_contract_test.py`
- `docs/reports/goal3108_v2_8_typed_result_stream_contract_2026-06-03.md`

External review:

- `docs/reviews/goal3109_gemini_review_goal3108_typed_result_stream_contract_2026-06-03.md`

Claude was also requested through:

- `docs/handoff/HANDOFF_CLAUDE_GOAL3108_V2_8_TYPED_RESULT_STREAM_2026-06-03.md`

The Claude attempt did not produce a review because the local Claude session was
still quota-limited with `You've hit your session limit - resets 3:50am
(America/New_York)`. It is not counted as consensus evidence.

## Validation

Codex ran:

```powershell
py -3 -m py_compile src\rtdsl\v2_8_typed_result_stream.py src\rtdsl\__init__.py
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3108_v2_8_typed_result_stream_contract_test tests.goal3105_v2_8_benchmark_runtime_gap_map_test
```

Observed result:

- `py_compile`: passed
- focused unittest: 13 tests, OK

Gemini reviewed the implementation statically and recorded the same claim
boundary. Its verdict was `accept-with-boundary`.

## Consensus Verdict

Codex + Gemini consensus: `accept-with-boundary`

This is accepted as an internal v2.8 foundation because:

- the contract reuses the existing `RtdlBufferDescriptor` typed-buffer protocol,
- the contract records the existing `fail_closed_overflow` segmented-row policy,
- grouped continuation operations are limited to declared v2.5 continuation
  operation names,
- stream kinds, column roles, status columns, and ordering states are generic,
- benchmark-app names and app-domain behavior are absent from the contract,
- validators fail closed on missing status columns, hidden dispatch, automatic
  partner selection, and unauthorized claim flags,
- users must choose partners explicitly.

## Boundaries

This consensus does not authorize:

- a v2.8 release,
- public speedup wording,
- broad RT-core wording,
- true-zero-copy wording,
- hidden dispatch,
- hidden partner selection,
- app-specific native-engine behavior,
- user-defined shader injection,
- paper-reproduction claims,
- pod or hardware performance claims.

## Next Accepted Engineering Step

The next v2.8 step should implement a real typed-stream producer or consumer on
top of this contract. The best first target is either a bounded witness stream
or a ranked summary stream, because those are shared across Hausdorff/X-HD,
RTNN, spatial RayJoin, contact-manifold, and RT-DBSCAN-style workloads.

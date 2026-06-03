# Goal3119: v2.8 Explicit Partner-Consumer Front Door 2-AI Consensus

Date: 2026-06-03

Status: accepted as an internal dry-run/bridge contract, hardware execution pending

## Scope

Goal3117 adds an explicit partner-consumer front door over the segmented typed
stream adapter:

- `plan_segmented_typed_stream_partner_continuation`
- `execute_segmented_typed_stream_partner_continuation`

The accepted local scope is dry-run mapping plus fail-closed execution
requirements. Real partner execution requires caller-supplied partner columns
and a partner runtime; it was not executed on this Windows environment.

## Review Inputs

Codex implementation and validation:

- `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`
- `src/rtdsl/__init__.py`
- `tests/goal3111_v2_8_segmented_typed_stream_adapter_test.py`
- `docs/reports/goal3117_v2_8_explicit_partner_consumer_front_door_2026-06-03.md`

External review:

- `docs/reviews/goal3118_gemini_review_goal3117_explicit_partner_consumer_front_door_2026-06-03.md`

## Validation

Codex ran:

```powershell
py -3 -m py_compile src\rtdsl\v2_8_segmented_typed_stream_adapter.py src\rtdsl\v2_8_typed_result_stream.py src\rtdsl\__init__.py
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3111_v2_8_segmented_typed_stream_adapter_test tests.goal3108_v2_8_typed_result_stream_contract_test tests.goal3105_v2_8_benchmark_runtime_gap_map_test
```

Observed result:

- `py_compile`: passed
- focused unittest: 25 tests, OK

## Consensus Verdict

Codex + Gemini consensus: `accept`

The internal bridge is accepted because:

- it requires an explicit partner name,
- it rejects `partner="auto"`,
- dry-run exposes the partner-column mapping,
- execution requires caller-supplied `partner_columns`,
- it refuses hidden host materialization,
- supported and unsupported operations are visible,
- all release, speedup, RT-core, true-zero-copy, hidden-dispatch,
  app-specific-engine, and user-defined-shader claim flags remain false.

## Boundaries

This consensus does not authorize:

- a v2.8 release,
- hardware partner execution claims,
- device-residency claims,
- true-zero-copy claims,
- public speedup wording,
- broad RT-core wording,
- hidden dispatch,
- hidden partner selection,
- app-specific native-engine behavior,
- user-defined shader injection.

## Next Required Step

The next step needs a CUDA-capable environment: supply actual Torch/Numba/CuPy
partner columns and execute one supported operation through this front door,
then compare results against the Goal3114 Python reference consumer.

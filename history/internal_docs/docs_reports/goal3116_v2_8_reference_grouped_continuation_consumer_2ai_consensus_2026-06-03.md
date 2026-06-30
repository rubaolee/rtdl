# Goal3116: v2.8 Reference Grouped-Continuation Consumer 2-AI Consensus

Date: 2026-06-03

Status: accepted as an internal v2.8 reference consumer, no release authorization

## Scope

Goal3114 extends the segmented typed-stream adapter with:

`execute_segmented_typed_stream_reference_continuation`

The function validates a `V28SegmentedTypedStreamAdapterResult`, reconstructs
segmented rows, maps the adapter's `V28GroupedContinuationPlan` into the
existing v2.5 Python reference continuation executor, and returns reference
outputs with claim flags kept false.

## Review Inputs

Codex implementation and validation:

- `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`
- `src/rtdsl/__init__.py`
- `tests/goal3111_v2_8_segmented_typed_stream_adapter_test.py`
- `docs/reports/goal3114_v2_8_reference_grouped_continuation_consumer_2026-06-03.md`

External review:

- `docs/reviews/goal3115_gemini_review_goal3114_reference_grouped_continuation_consumer_2026-06-03.md`

Note: the Gemini review title contains a stale phrase, `Hit-Stream
Neutral-Seam Reconciliation`, but the body reviews Goal3114's reference
grouped-continuation consumer and gives a concrete `Accept` verdict.

## Validation

Codex ran:

```powershell
py -3 -m py_compile src\rtdsl\v2_8_segmented_typed_stream_adapter.py src\rtdsl\v2_8_typed_result_stream.py src\rtdsl\__init__.py
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3111_v2_8_segmented_typed_stream_adapter_test tests.goal3108_v2_8_typed_result_stream_contract_test tests.goal3105_v2_8_benchmark_runtime_gap_map_test
```

Observed result:

- `py_compile`: passed
- focused unittest: 22 tests, OK

## Consensus Verdict

Codex + Gemini consensus: `accept`

This internal reference consumer is accepted because:

- it reuses `execute_v2_5_partner_continuation_reference`,
- it avoids creating a second reduction oracle,
- it maps grouped argmax, segmented sum, and top-k `k` handling through the
  existing v2.5 reference semantics,
- it explicitly handles the listed grouped/segmented operations at the contract
  level,
- it keeps native producer, partner consumer, device-residency, true-zero-copy,
  release, speedup, RT-core, hidden-dispatch, hidden-partner, app-specific
  engine, and user-defined shader claims false.

## Boundaries

This consensus does not authorize:

- a v2.8 release,
- native producer promotion,
- partner consumer promotion,
- device-residency claims,
- true-zero-copy claims,
- public speedup wording,
- broad RT-core wording,
- hidden dispatch,
- hidden partner selection,
- app-specific native-engine behavior,
- user-defined shader injection,
- paper-reproduction claims,
- pod or hardware performance claims.

## Next Accepted Engineering Step

The next v2.8 step should choose one benchmark subpath and replace either the
reference producer or reference consumer with a real native or partner
implementation that emits or consumes the same typed stream contract. If the
step touches OptiX or GPU partner execution, pod validation is required.

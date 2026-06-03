# Goal3113: v2.8 Segmented Typed-Stream Adapter 2-AI Consensus

Date: 2026-06-03

Status: accepted as an internal v2.8 reference adapter, no release authorization

## Scope

Goal3111 adds a local reference adapter over the Goal3108 typed result-stream
contract:

- it emits a `SegmentedRowStream`,
- maps row-schema fields to typed result-stream columns,
- builds required status columns,
- creates a `V28TypedResultStreamContract`,
- optionally creates a `V28GroupedContinuationPlan`,
- records status values for row count, capacity, overflow, and
  complete-candidate-coverage.

The accepted scope is `host_reference_contract_adapter`. This is not a native
producer and not a partner consumer promotion.

## Review Inputs

Codex implementation and validation:

- `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`
- `src/rtdsl/__init__.py`
- `tests/goal3111_v2_8_segmented_typed_stream_adapter_test.py`
- `docs/reports/goal3111_v2_8_segmented_typed_stream_adapter_2026-06-03.md`

External review:

- `docs/reviews/goal3112_gemini_review_goal3111_segmented_typed_stream_adapter_2026-06-03.md`

Gemini Flash initially produced a weak `needs-more-evidence` review that
deferred to human review. Codex did not count that version. Codex then supplied
the relevant source text inline, and Gemini rewrote the review with a concrete
`Accept` verdict and file-level findings.

## Validation

Codex ran:

```powershell
py -3 -m py_compile src\rtdsl\v2_8_segmented_typed_stream_adapter.py src\rtdsl\v2_8_typed_result_stream.py src\rtdsl\__init__.py
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3111_v2_8_segmented_typed_stream_adapter_test tests.goal3108_v2_8_typed_result_stream_contract_test tests.goal3105_v2_8_benchmark_runtime_gap_map_test
```

Observed result:

- `py_compile`: passed
- focused unittest: 19 tests, OK

## Consensus Verdict

Codex + Gemini consensus: `accept`

This is accepted as an internal v2.8 reference adapter because:

- it bridges `SegmentedRowStream` to the Goal3108 typed result-stream contract,
- it preserves the segmented-row fail-closed overflow behavior,
- it records required status values,
- it rejects missing role metadata,
- it rejects `auto` partner selection when a continuation is requested,
- it validates the grouped continuation plan,
- it keeps all release, speedup, RT-core, true-zero-copy, hidden-dispatch,
  hidden-partner, app-specific-engine, and user-defined-shader claims false.

## Boundaries

This consensus does not authorize:

- a v2.8 release,
- public speedup wording,
- broad RT-core wording,
- true-zero-copy wording,
- native producer promotion,
- partner consumer promotion,
- hidden dispatch,
- hidden partner selection,
- app-specific native-engine behavior,
- user-defined shader injection,
- paper-reproduction claims,
- pod or hardware performance claims.

## Next Accepted Engineering Step

The next v2.8 step should replace the host-reference producer or consumer in one
narrow benchmark subpath with a real typed-stream producer or consumer. The best
first candidates are ranked-summary and bounded-witness paths because they are
shared by Hausdorff/X-HD, RTNN, spatial RayJoin, contact-manifold, and
RT-DBSCAN-style workloads.

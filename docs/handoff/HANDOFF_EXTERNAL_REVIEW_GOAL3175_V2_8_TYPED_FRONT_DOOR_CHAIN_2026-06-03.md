# External Review Handoff: Goal3175 v2.8 Typed Front-Door Chain

Please perform an independent read-only review of the v2.8 typed front-door work from Goal3169 through Goal3174 on RTDL `main`.

## Expected Output

Write the review to one of:

- Gemini: `docs/reviews/goal3175_gemini_review_v2_8_typed_front_door_chain_2026-06-03.md`
- Claude: `docs/reviews/goal3175_claude_review_v2_8_typed_front_door_chain_2026-06-03.md`

Use exactly one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

State explicitly that the review is independent of Codex authoring and is a distinct AI-system review.

## Commit Range And Evidence

Review current `main` through commit `e27efc79`.

Primary implementation/report/test files:

- `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`
- `src/rtdsl/v2_8_typed_result_stream.py`
- `src/rtdsl/v2_8_benchmark_runtime_gap.py`
- `src/rtdsl/__init__.py`
- `examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `examples/v2_0/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py`
- `docs/reports/goal3169_barnes_hut_grouped_vector_typed_stream_front_door_2026-06-03.md`
- `docs/reports/goal3170_v2_8_runtime_gap_barnes_hut_vector_stream_refresh_2026-06-03.md`
- `docs/reports/goal3171_direct_compact_mask_typed_stream_front_door_2026-06-03.md`
- `docs/reports/goal3172_v2_8_runtime_gap_compact_mask_refresh_2026-06-03.md`
- `docs/reports/goal3173_direct_bounded_collect_typed_stream_front_door_2026-06-03.md`
- `docs/reports/goal3174_v2_8_runtime_gap_bounded_collect_refresh_2026-06-03.md`
- `tests/goal3169_barnes_hut_grouped_vector_typed_stream_front_door_test.py`
- `tests/goal3170_v2_8_runtime_gap_barnes_hut_vector_stream_refresh_test.py`
- `tests/goal3171_direct_compact_mask_typed_stream_front_door_test.py`
- `tests/goal3172_v2_8_runtime_gap_compact_mask_refresh_test.py`
- `tests/goal3173_direct_bounded_collect_typed_stream_front_door_test.py`
- `tests/goal3174_v2_8_runtime_gap_bounded_collect_refresh_test.py`

## Review Questions

1. Do the new direct front doors remain generic and app-agnostic?
   - `execute_grouped_vector_sum_typed_stream_partner_columns(...)`
   - `execute_compact_mask_typed_stream_partner_columns(...)`
   - `execute_bounded_collect_typed_stream_partner_columns(...)`

2. Do the migrated app wrappers preserve the principle that app semantics live in examples/user code while the v2.8 runtime consumes generic columns and operations?

3. Are the explicit-partner rules preserved?
   - no hidden dispatch
   - no automatic partner selection
   - no auto-Triton wording

4. Are claim boundaries preserved?
   - no release authorization
   - no public speedup claim
   - no broad RT-core speedup claim
   - no true-zero-copy claim
   - no app-specific native-engine behavior

5. Do the runtime-gap refreshes honestly move only the front-door gap from missing to present while keeping native typed-producer/device-residency/performance evidence as remaining work?

6. Are there test gaps or wording gaps before the next v2.8 engineering step?

## Suggested Validation

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3169_barnes_hut_grouped_vector_typed_stream_front_door_test `
  tests.goal3170_v2_8_runtime_gap_barnes_hut_vector_stream_refresh_test `
  tests.goal3171_direct_compact_mask_typed_stream_front_door_test `
  tests.goal3172_v2_8_runtime_gap_compact_mask_refresh_test `
  tests.goal3173_direct_bounded_collect_typed_stream_front_door_test `
  tests.goal3174_v2_8_runtime_gap_bounded_collect_refresh_test `
  tests.goal3111_v2_8_segmented_typed_stream_adapter_test `
  tests.goal3105_v2_8_benchmark_runtime_gap_map_test
```

## Boundaries For Reviewer

This is not a release review and should not authorize v2.8 release packaging. It is an engineering-chain review for the typed front-door direction. If the work is sound but still needs native typed producers, device residency evidence, broader partner conformance, or performance evidence, use `accept-with-boundary`.

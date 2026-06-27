# External Review Handoff: Goal4052/4053 Numba Presegmented Vector Sum Chain

Please perform an independent read-only review of Goal4052 and Goal4053 on
current `main`.

## Context

These goals respond to a generic runtime bottleneck found while improving the
Barnes-Hut benchmark foundation: presegmented grouped-vector streams should not
fall back to atomic-by-group Numba continuation or repeated front-door setup.

Important boundary: this must remain a generic partner continuation primitive.
It must not add Barnes-Hut, force-law, or app-specific native-engine logic, and
must not authorize release, public speedup, whole-app speedup, RT-core speedup,
true zero-copy, or automatic partner-selection claims.

## Files To Inspect

- `src/rtdsl/numba_partner_continuation.py`
- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`
- `src/rtdsl/__init__.py`
- `examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py`
- `tests/goal4052_numba_presegmented_vector_sum_test.py`
- `tests/goal4053_numba_presegmented_vector_sum_prepared_session_test.py`
- `docs/reports/goal4052_numba_presegmented_vector_sum_2026-06-08.md`
- `docs/reports/goal4052_numba_presegmented_vector_sum_pod_probe.json`
- `docs/reports/goal4053_numba_presegmented_vector_sum_prepared_session_2026-06-08.md`
- `docs/reports/goal4053_numba_presegmented_vector_sum_prepared_session_pod_probe.json`

## Required Checks

1. Verify Goal4052 is generic: it adds a Numba `grouped_vector_sum_f64x2` offset
   path over `row_offsets`, `values_x`, and `values_y`, not app logic.
2. Verify Goal4052 keeps the safe default `validate_row_offsets=True` and makes
   the no-validation hot path explicit and metadata-visible.
3. Verify Goal4053 prepared sessions validate neutral handoff once, reuse output
   columns, and do not perform per-run neutral-handoff validation.
4. Verify the pod evidence is internally consistent:
   - Goal4052 direct offset kernel matches atomic and is >2x faster on tested
     shapes.
   - Goal4053 prepared replay matches atomic and is >3x faster than both atomic
     and the one-shot adapter on tested shapes.
5. Verify all claim-boundary flags remain false and no wording overclaims
   release readiness, whole-app acceleration, RT-core acceleration, true
   zero-copy, or app-specific engine behavior.
6. State a verdict using one of: `accept`, `accept-with-boundary`,
   `needs-more-evidence`, or `reject`.

## Output Path

Write your review to one of:

- `docs/reviews/goal4054_claude_review_goal4052_4053_numba_vector_sum_chain_2026-06-08.md`
- `docs/reviews/goal4054_gemini_review_goal4052_4053_numba_vector_sum_chain_2026-06-08.md`

Do not edit source files for this review.


# Gemini Review Request - Goal2774 v2.5 Grouped Hit-Stream Support Matrix

Please perform an independent read-only review of Goal2774.

## Context

Goal2771 and Goal2772 added/proved a CuPy consumer for event-ordered OptiX hit
streams:

- grouped by generic `ray_id`
- reductions over generic `primitive_id`
- count/sum/xor/min/max
- first/last hit row index
- first/last primitive id by stored hit-stream row order
- signed `-1` empty-group sentinels

Goal2774 is not adding a new performance claim. It declares that shape in the
v2.5 generic partner-continuation contract and fixes the support matrix so that
only actually supported partner cells are marked as preview.

## Files To Inspect

- `src/rtdsl/partner_continuation_protocol.py`
- `src/rtdsl/v2_5_partner_support_matrix.py`
- `src/rtdsl/__init__.py`
- `tests/goal2662_v2_5_partner_continuation_contract_test.py`
- `tests/goal2671_v2_5_preview_gate_test.py`
- `tests/goal2696_v2_5_partner_support_matrix_test.py`
- `tests/goal2774_v2_5_grouped_hit_stream_support_matrix_test.py`
- `docs/reports/goal2774_v2_5_grouped_hit_stream_support_matrix_2026-05-31.md`
- continuity context:
  - `tests/goal2771_hit_stream_event_ordered_grouped_reduction_consumer_test.py`
  - `tests/goal2772_hit_stream_event_ordered_grouped_richer_reductions_test.py`

## Required Checks

1. Confirm the new operation name and field names are generic/app-agnostic.
2. Confirm the support matrix is honest:
   - `python_reference`: `reference_contract`
   - `cupy_conformance`: `preview_not_promoted`
   - `triton`: `unsupported_fail_closed`
   - `numba`: `unsupported_fail_closed`
3. Confirm Goal2774 does not authorize public speedup, release, true zero-copy,
   or RT traversal replacement claims.
4. Confirm the reference semantics match Goal2772: row-order first/last and `-1`
   empty-group sentinels.
5. Confirm the changed older tests still preserve the v2.5 Triton-first/Numba
   fallback policy without pretending this new CuPy preview is a Triton kernel.
6. List any blockers or required follow-up before Goal2775.

## Validation Commands

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal2662_v2_5_partner_continuation_contract_test tests.goal2671_v2_5_preview_gate_test tests.goal2696_v2_5_partner_support_matrix_test tests.goal2774_v2_5_grouped_hit_stream_support_matrix_test
py -3 -m unittest tests.goal2771_hit_stream_event_ordered_grouped_reduction_consumer_test tests.goal2772_hit_stream_event_ordered_grouped_richer_reductions_test
```

## Output

Write your review to:

`docs/reviews/goal2774_gemini_review_v2_5_grouped_hit_stream_support_matrix_2026-05-31.md`

Use verdict `accept`, `accept-with-boundary`, or `needs-more-evidence`.

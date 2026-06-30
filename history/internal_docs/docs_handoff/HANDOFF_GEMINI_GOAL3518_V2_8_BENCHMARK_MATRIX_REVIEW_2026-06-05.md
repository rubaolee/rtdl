# Handoff: Gemini Review For Goal3518 v2.8 Benchmark Matrix

Please perform an independent read-only review of Goal3518.

## Files To Inspect

- `src/rtdsl/v2_8_benchmark_matrix.py`
- `src/rtdsl/__init__.py`
- `tests/goal3518_v2_8_benchmark_matrix_test.py`
- `docs/reports/goal3518_v2_8_benchmark_matrix_refresh_2026-06-05.md`
- Key evidence artifacts referenced by the report, especially:
  - `docs/reports/goal2968_current_packet_plus_raydb_gate_triage_2026-06-01.json`
  - `docs/reports/goal2959_current_packet_after_rtnn_chunk_pod/goal2855_summary.json`
  - `docs/reports/goal2959_current_packet_after_rtnn_chunk_pod/goal2801_hausdorff_xhd.json`
  - `docs/reports/goal2965_raydb_current_gate_pod/goal2965_raydb_same_contract_gate_current.json`
  - `docs/reports/goal3511_overlay_area_steady_state_relation_stream_pod_2026-06-05.json`

## Questions

1. Does the matrix cover all 10 promoted v2.8 benchmark apps, with extra rows only where contracts differ?
2. Are the classifications (`primitive_only`, `partner_needed`, `prepared_execution_needed`) honest and app-agnostic?
3. Are setup, warmup, steady-state, and validation timing cells either numeric or explicitly explained without bare placeholders?
4. Does the spatial RayJoin overlay row avoid collapsing setup/cache/warmup with steady-state execution, and does it avoid RayJoin paper-reproduction claims?
5. Do all claim-boundary flags remain false?
6. Are any numbers copied incorrectly from the cited evidence artifacts?

## Required Output

Write your review to:

`docs/reviews/goal3521_gemini_review_goal3518_v2_8_benchmark_matrix_2026-06-05.md`

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

# Gemini Review Handoff: Goal2241 RayJoin PIP Closed-Shape Path

Please independently review Goal2241.

Read:

- `docs/reports/goal2241_rayjoin_same_query_pip_closed_shape_path_2026-05-17.md`
- `scripts/goal2192_rayjoin_same_query_stream_runner.py`
- `tests/goal2192_rayjoin_same_query_stream_adapter_test.py`
- `tests/goal2241_rayjoin_same_query_pip_closed_shape_path_test.py`
- Context: `docs/reports/goal2238_closed_shape_membership_primitive_2026-05-17.md`
- Context: `docs/reports/goal2240_closed_shape_membership_2ai_consensus_2026-05-17.md`

Questions:

1. Does the runner correctly route only PIP/OptiX through the generic
   `closed_shape_membership_2d_optix` primitive?
2. Does the Python mapping preserve the RayJoin same-query output contract
   (`point_id`, `polygon_id`, `contains`) without putting app vocabulary into
   the native engine?
3. Does the report keep the claim boundary narrow and avoid implying full
   RayJoin reproduction, v2.0 release readiness, or paper-scale speedup?
4. Are the tests sufficient for this wiring change before pod timing?

Write your review to:

`docs/reviews/goal2242_gemini_review_goal2241_rayjoin_pip_closed_shape_path_2026-05-17.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. State clearly that this is an independent Gemini review distinct from
Codex.

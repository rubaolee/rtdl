# Gemini Addendum Review Handoff: Goal2241 Prepack Update

Please independently review the Goal2241 addendum after the first Gemini review.

The post-review change is narrow:

- `scripts/goal2192_rayjoin_same_query_stream_runner.py` now pre-packs PIP
  points and shapes once per `run-stream` invocation for the PIP/OptiX backend.
- Warmups/repeats reuse the packed inputs.
- The output metadata records
  `input_preparation_path: prepacked_points_and_shapes_once_per_run_stream`.

Read:

- `scripts/goal2192_rayjoin_same_query_stream_runner.py`
- `docs/reports/goal2241_rayjoin_same_query_pip_closed_shape_path_2026-05-17.md`
- `tests/goal2192_rayjoin_same_query_stream_adapter_test.py`
- `tests/goal2241_rayjoin_same_query_pip_closed_shape_path_test.py`
- Previous review:
  `docs/reviews/goal2242_gemini_review_goal2241_rayjoin_pip_closed_shape_path_2026-05-17.md`

Questions:

1. Is the prepack-once change safe and limited to PIP/OptiX?
2. Does it avoid changing the output contract or app/native boundary?
3. Is it appropriate to measure the primitive with prepacked inputs, given the
   primitive accepts `PackedPoints` and `PackedPolygons`?
4. Does the claim boundary remain narrow pending pod timing?

Write your addendum to:

`docs/reviews/goal2244_gemini_review_goal2241_prepack_addendum_2026-05-17.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. State clearly that this is an independent Gemini addendum review
distinct from Codex.

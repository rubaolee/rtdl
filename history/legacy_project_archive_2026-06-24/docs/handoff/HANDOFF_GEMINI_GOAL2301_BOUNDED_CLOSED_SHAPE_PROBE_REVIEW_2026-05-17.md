# Gemini Review Task: Goal2301 Bounded Closed-Shape Point Probe

Please perform an independent read-only review of Goal2301.

Read:

- `docs/reports/goal2301_bounded_closed_shape_point_probe_2026-05-17.md`
- `tests/goal2301_bounded_closed_shape_point_probe_test.py`
- `src/native/optix/rtdl_optix_core.cpp`
- `docs/reports/goal2301_bounded_point_probe_baseline_current_pod_2026-05-17.json`
- `docs/reports/goal2301_bounded_point_probe_candidate_pod_2026-05-17.json`
- `docs/reports/goal2301_bounded_point_probe_candidate_pip_count_phase_pod_2026-05-17.json`
- `docs/reports/goal2301_short_origin_inside_negative_pod_2026-05-17.json`
- `docs/reports/goal2301_tiny_crossing_negative_pod_2026-05-17.json`

Review questions:

1. Confirm the source change stays app-agnostic: it changes the generic
   point/closed-shape membership probe geometry and does not add RayJoin,
   PIP, polygon, map, county, or join-specific native ABI names.
2. Confirm the evidence supports the narrow claim: on the measured 100,000-query
   RayJoin-exported PIP stream, the bounded probe preserves the exact expected
   count `8686` and improves positive rows and scalar count over the current
   baseline.
3. Confirm the two tiny-probe variants are correctly rejected because they
   returned zero positives.
4. Confirm the report does not overclaim RayJoin reproduction, RTDL beating
   RayJoin, whole-app speedup, true zero-copy, or v2.0 release readiness.
5. Note any risks: fixed `0.5` half-length generality, other coordinate scales,
   possible future need for a configurable/proven query extent, or missing
   additional datasets.

Write your review to:

- `docs/reviews/goal2302_gemini_review_goal2301_bounded_closed_shape_probe_2026-05-17.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. This is an independent Gemini review distinct from Codex.

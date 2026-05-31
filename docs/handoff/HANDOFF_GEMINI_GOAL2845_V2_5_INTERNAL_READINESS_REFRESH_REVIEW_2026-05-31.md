# Gemini Review Task: Goal2845 v2.5 Internal Readiness Refresh

Please perform an independent read-only review of Goal2845 and write your review to:

`docs/reviews/goal2846_gemini_review_goal2845_v2_5_internal_readiness_refresh_2026-05-31.md`

## Files To Inspect

- `src/rtdsl/v2_5_internal_readiness.py`
- `src/rtdsl/v2_5_execution_path_policy.py`
- `tests/goal2845_v2_5_internal_readiness_refresh_test.py`
- `tests/goal2811_rtnn_direct_aggregate_kernel_test.py`
- `docs/reports/goal2845_v2_5_internal_readiness_refresh_2026-05-31.md`
- Related evidence reports/reviews:
  - `docs/reports/goal2835_primitive_payload_entrypoint_metadata_2026-05-31.md`
  - `docs/reports/goal2837_fixed_radius_graph_entrypoint_metadata_2026-05-31.md`
  - `docs/reports/goal2839_rtnn_same_stream_runner_mode_2026-05-31.md`
  - `docs/reports/goal2841_rtnn_same_stream_scale_probe_2026-05-31.md`
  - `docs/reports/goal2843_v2_5_execution_path_policy_2026-05-31.md`
  - `docs/reviews/goal2844_gemini_review_goal2843_execution_path_policy_2026-05-31.md`

## Questions

1. Does Goal2845 correctly index the post-2808 hardening chain from Goal2835 through Goal2844 in the internal readiness packet?
2. Is adding `execution_path_policy` to the core validations appropriate and bounded?
3. Is the Goal2811 test edit a stale source-shape assertion repair rather than a runtime semantics change?
4. Does the report honestly record the pod exact-band failure before repair and avoid pretending it was a runtime problem?
5. Does Goal2845 avoid release, public speedup, broad RT-core, whole-app speedup, true zero-copy, package-install, Triton auto-selection, or native app-specific engine claims?

## Required Verdict

Use exactly one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Expected likely verdict is `accept-with-boundary` because this is an internal readiness index refresh plus stale-test repair, not a release gate.


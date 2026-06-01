# Handoff: Gemini Review Request for Goal2941-2943 Row-Stream Front Door Chain

Date: 2026-06-01
Requested reviewer: Gemini / Antigravity

Please perform an independent read-only review of the Goal2941-Goal2943 chain.

## Scope

Review these artifacts:

- `docs/reports/goal2941_rayjoin_row_view_partner_columns_scale_probe_2026-06-01.md`
- `docs/reports/goal2941_rayjoin_row_view_partner_columns_scale_probe_pod/goal2941_rayjoin_row_view_partner_columns_large.json`
- `docs/reports/goal2942_current_packet_after_row_columns_2026-06-01.md`
- `docs/reports/goal2942_current_packet_after_row_columns_pod/goal2855_summary.json`
- `docs/reports/goal2942_current_packet_after_row_columns_pod/goal2942_triage.json`
- `docs/reports/goal2943_generic_event_ordered_hit_stream_front_door_2026-06-01.md`
- `docs/reports/goal2943_generic_event_ordered_hit_stream_front_door_pod/goal2943_front_door_smoke.json`
- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/generic_primitives.py`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/v2_5_internal_readiness.py`
- `tests/goal2941_rayjoin_row_view_partner_columns_scale_probe_test.py`
- `tests/goal2942_current_packet_after_row_columns_test.py`
- `tests/goal2943_generic_event_ordered_hit_stream_front_door_test.py`

## Questions

1. Does Goal2941 correctly bound the Spatial RayJoin typed partner-column bridge as host-staged, not true device-resident zero-copy?
2. Does Goal2942 honestly show that the seven-app packet remains green after the row-column bridge, with no claim-boundary violations?
3. Does Goal2943 materially improve user ergonomics by exposing a generic public front door for RTDL/OptiX event-ordered hit-stream grouped reduction?
4. Does Goal2943 remain app-agnostic by grouping only `ray_id` and reducing only `primitive_id`, with app semantics outside the native engine?
5. Does the partner-choice boundary hold: CuPy executes as an explicit conformance/preview partner, while Triton and Numba fail closed for this operation?
6. Are there any overclaims around true zero-copy, public speedup, whole-app acceleration, paper reproduction, or release readiness?

## Expected Output

Write the review to:

`docs/reviews/goal2944_gemini_review_goal2941_2943_row_stream_front_door_2026-06-01.md`

Use one of the standard verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Please include concrete file/path evidence and call out any required fixes before release wording or broader v2.5 readiness claims.

## Boundary

This review should not mutate source files. It should not authorize release.
Release/public claims still require a user-requested release packet and fresh
3-AI consensus.

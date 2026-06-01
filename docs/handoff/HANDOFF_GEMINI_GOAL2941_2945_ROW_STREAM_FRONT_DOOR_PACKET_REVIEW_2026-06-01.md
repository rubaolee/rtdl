# Handoff: Gemini Review Goal2941-2945 Row-Stream Front Door Packet

Please perform an independent Gemini/Antigravity review of the Goal2941-2945
chain and write the result to:

`docs/reviews/goal2946_gemini_review_goal2941_2945_row_stream_front_door_packet_2026-06-01.md`

## Context

This chain responds to the v2.5-v3.0 roadmap priority: make RT cores easy to
use from Python while letting users explicitly choose partners. It does not
authorize a release or public speedup claim.

Recent artifacts to inspect:

- `docs/reports/goal2941_rayjoin_row_view_partner_columns_scale_probe_2026-06-01.md`
- `docs/reports/goal2941_rayjoin_row_view_partner_columns_scale_probe_pod/goal2941_rayjoin_row_view_partner_columns_large.json`
- `docs/reports/goal2942_current_packet_after_row_columns_2026-06-01.md`
- `docs/reports/goal2942_current_packet_after_row_columns_pod/goal2855_summary.json`
- `docs/reports/goal2943_generic_event_ordered_hit_stream_front_door_2026-06-01.md`
- `docs/reports/goal2943_generic_event_ordered_hit_stream_front_door_pod/goal2943_front_door_smoke.json`
- `docs/reports/goal2945_current_packet_after_hit_stream_front_door_2026-06-01.md`
- `docs/reports/goal2945_current_packet_after_hit_stream_front_door_pod/goal2855_summary.json`
- `docs/reports/goal2945_current_packet_after_hit_stream_front_door_pod/goal2945_triage.json`
- `src/rtdsl/generic_primitives.py`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/partner_continuation_protocol.py`
- `src/rtdsl/v2_5_partner_support_matrix.py`
- `src/rtdsl/v2_5_internal_readiness.py`
- `tests/goal2941_rayjoin_row_view_partner_columns_scale_probe_test.py`
- `tests/goal2943_generic_event_ordered_hit_stream_front_door_test.py`
- `tests/goal2945_current_packet_after_hit_stream_front_door_test.py`

## Review Questions

1. Do Goal2941-2945 preserve the app-agnostic native-engine boundary?
2. Is the new public front door genuinely generic, or does it hide
   app-specific RayJoin/spatial/database logic?
3. Are the partner-choice boundaries honest: explicit CuPy preview where
   implemented, Triton/Numba fail closed where not implemented, no hidden
   forced partner path?
4. Does the Goal2945 packet fairly show no regression after the front door?
5. Are all claim boundaries intact: no release, public speedup, broad RT-core,
   whole-app speedup, true-zero-copy, package-install, paper-reproduction, or
   app-specific engine-logic claims?
6. What should be the next generic runtime primitive after this chain? Please
   assess the proposed direction: prepared, event-ordered, payload-mapped
   primitive-column reductions over RT hit streams.

## Expected Verdict

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, `reject`.

Please lead with findings, cite concrete files/artifacts, and distinguish
release-gate concerns from internal-engineering concerns.

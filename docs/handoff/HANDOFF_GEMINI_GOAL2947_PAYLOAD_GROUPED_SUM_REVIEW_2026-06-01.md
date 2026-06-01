# Handoff: Gemini Review Goal2947 Payload-Mapped Hit-Stream Continuation

Please perform an independent Gemini/Antigravity review of Goal2947 and write
the result to:

`docs/reviews/goal2949_gemini_review_goal2947_payload_grouped_sum_front_door_2026-06-01.md`

## Context

Goal2947 adds a generic v2.5 event-ordered RT hit-stream continuation:

- operation: `hit_stream_primitive_payload_grouped_sum_f64`
- front doors:
  - `rt.prepare_generic_ray_triangle_event_ordered_payload_grouped_sum_3d(...)`
  - `rt.run_generic_ray_triangle_event_ordered_payload_grouped_sum_3d(...)`
- current executable partner: `cupy` / `cupy_conformance`
- Triton/Numba: fail closed for this operation

This is meant to help users write Python+partner+RTDL programs where RTDL/OptiX
produces generic hit rows and the chosen partner reduces user-provided generic
primitive payload columns. It must not become app-specific RayJoin, database,
or geometry-overlay engine logic.

## Files And Artifacts To Inspect

- `src/rtdsl/partner_continuation_protocol.py`
- `src/rtdsl/v2_5_partner_support_matrix.py`
- `src/rtdsl/v2_5_partner_conformance_matrix.py`
- `src/rtdsl/v2_5_determinism_policy.py`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/generic_primitives.py`
- `src/rtdsl/__init__.py`
- `src/rtdsl/v2_5_internal_readiness.py`
- `scripts/goal2947_generic_event_ordered_payload_grouped_sum_front_door_smoke.py`
- `tests/goal2947_generic_event_ordered_payload_grouped_sum_front_door_test.py`
- `docs/reports/goal2947_generic_event_ordered_payload_grouped_sum_front_door_2026-06-01.md`
- `docs/reports/goal2947_generic_event_ordered_payload_grouped_sum_front_door_pod/goal2947_payload_grouped_sum_smoke.json`

## Review Questions

1. Does Goal2947 preserve the app-agnostic engine boundary?
2. Is `hit_stream_primitive_payload_grouped_sum_f64` a generic primitive rather
   than hidden app logic?
3. Are partner boundaries honest: explicit CuPy preview, Triton/Numba fail
   closed, no hidden forced partner path?
4. Does the pod smoke prove the intended event-ordered RT producer plus CuPy
   consumer path without host scalar/row materialization before the consumer?
5. Are claim boundaries intact: no release, public speedup, broad RT-core,
   whole-app speedup, true-zero-copy, package-install, paper reproduction, or
   app-specific native engine logic?
6. What performance risk should Codex attack next? In particular, comment on
   whether the current single-kernel CuPy consumer should be scale-probed and
   potentially optimized with multi-block partial reductions.

## Expected Verdict

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, `reject`.

Please lead with concrete findings and file/artifact references.

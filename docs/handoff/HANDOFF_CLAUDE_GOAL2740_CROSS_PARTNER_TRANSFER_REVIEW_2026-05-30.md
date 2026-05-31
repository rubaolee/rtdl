# Handoff: Claude Review For Goal2740 Cross-Partner Transfer Plan

Please perform a critical, read-only review of Goal2740.

## Context

RTDL v2.5 is hardening the device-resident RT hit-stream handoff and typed
primitive payload column design. Recent goals:

- Goal2736 aligned Tier A apps with primitive-first planning.
- Goal2737 added native hit-stream owner lifecycle guards.
- Goal2738 added producer/consumer CUDA stream-ordering boundary metadata.
- Goal2739 provided Gemini review, accepting with boundary and flagging
  cross-partner transfer semantics as remaining risk.

Goal2740 responds by adding an explicit partner transfer/carrier plan so Triton,
CuPy, Numba, and the Python reference path are not hidden behind a Torch-shaped
execution helper.

## Files To Inspect

- `src/rtdsl/hit_stream_handoff.py`
- `src/rtdsl/__init__.py`
- `tests/goal2740_hit_stream_cross_partner_transfer_plan_test.py`
- `docs/reports/goal2740_hit_stream_cross_partner_transfer_plan_2026-05-30.md`
- Prior context if needed:
  - `docs/reports/goal2734_v2_5_same_pointer_zero_copy_boundary_audit_2026-05-30.md`
  - `docs/reports/goal2736_tier_a_primitive_first_plan_alignment_2026-05-30.md`
  - `docs/reports/goal2737_native_hit_stream_owner_lifecycle_guard_2026-05-30.md`
  - `docs/reports/goal2738_native_hit_stream_stream_ordering_boundary_2026-05-30.md`
  - `docs/reviews/goal2739_gemini_review_goal2736_2738_v25_primitive_lifetime_stream_2026-05-30.md`

## Review Questions

1. Does `plan_v2_5_hit_stream_partner_transfer(...)` correctly make partner
   carrier/transfer choices explicit for Python reference, Triton, CuPy, and
   Numba?
2. Does the implementation preserve the v2.5 boundary that CuPy is currently
   descriptor-only for this generic hit-stream slice, while Triton/Numba remain
   preview-gated?
3. Does the raw CUDA-array-interface hardening prevent fake/unproven pointers
   from being adapted at runtime without blocking hardware-proven native
   hit-stream columns?
4. Does the new plan avoid authorizing silent copies, true zero-copy claims,
   public speedup claims, or partner replacement of RTDL/OptiX traversal?
5. Are there code/test/report gaps that should block accepting Goal2740?

## Expected Output

Write your review to:

`docs/reviews/goal2741_claude_review_goal2740_cross_partner_transfer_2026-05-30.md`

Use one of these verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

Please include a short risk list and exact file references where useful. Do not
modify source code.
